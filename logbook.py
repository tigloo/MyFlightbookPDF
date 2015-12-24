# -*- coding: utf-8 -*-

import codecs
import csv
import unicodecsv
import sys
import re
import datetime
import math

#
# Snippet below based on YAPTU, "Yet Another Python Templating Utility, Version 1.2"
#
# Originally from
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52305
# Author: Alex Martelli
# License: PSF
#
# Additional modifications by Peter Norvig, found at
# http://aima.cs.berkeley.edu/yaptu.py
# License: assumed PSF
#
# Additional modifications by Till Gerken
# (removed HTML entity processing)
#
class Copier:
    "Smart-copier (YAPTU) class"

    def copyblock(self, i=0, last=None):
        "Main copy method: process lines [i,last) of block"

        def repl(match, self=self):
            "Replace the match with its value as a Python expression."
            expr = self.preproc(match.group(1), 'eval')
            if self.verbose: print '=== eval{%s}' % expr,
            try:
                val = eval(expr, self.globals)
            except:
                self.oops('eval', expr)
            if callable(val): val = val()
            if val == None: val = ''
            if self.verbose: print '========>', val
            return str(val)

        block = self.globals['_bl']
        if last is None: last = len(block)
        while i < last:
            line = block[i]
            if line.startswith("#["):   # a statement starts at line block[i]
                # i is the last line to _not_ process
                stmt = line[2:].strip()
                j = i+1   # look for 'finish' from here onwards
                nest = 1  # count nesting levels of statements
                while j<last and not stmt.endswith("#]"):
                    line = block[j]
                    # first look for nested statements or 'finish' lines
                    if line.startswith("#]"):    # found a statement-end
                        nest = nest - 1
                        if nest == 0: break  # j is first line to _not_ process
                    elif line.startswith("#["):   # found a nested statement
                        nest = nest + 1
                    elif nest == 1 and line.startswith("#|"):
                        # look for continuation only at this nesting
                        nestat = line[2:].strip()
                        stmt = '%s _cb(%s,%s)\n%s' % (stmt,i+1,j,nestat)
                        i=j     # again, i is the last line to _not_ process
                    j = j+1
                if stmt == '': ## A multi-line python suite
                    self.execute(''.join(block[i+1:j]))
                    i = j+1
                else:  ## The header of a for loop (etc.) is on this line
                    self.execute("%s _cb(%s,%s)" % (stmt,i+1,j))
                    i = j+1
            else:       # normal line, just copy with substitution
                self.outf.write(self.regex.sub(repl,self.preproc(line,'copy')))
                i = i+1

    def __init__(self, globals):
        "Create a Copier."
        self.regex   = re.compile("<<(.*?)>>")
        self.globals = globals
        self.globals['_cb'] = self.copyblock
        self.outf = sys.stdout
        self.verbose = 0

    def execute(self, stmt):
        stmt = self.preproc(stmt, 'exec') + '\n'
        if self.verbose:
            print "******* executing {%s} in %s" % (stmt, self.globals.keys())
        try:
            exec stmt in self.globals
        except:
            self.oops('exec', stmt)

    def oops(self, why, what):
        print 'Something went wrong in %sing {%s}' % (why, what)
        print 'Globals:', self.globals.keys(), \
            self.globals.get('SECTIONS', '???')
        raise

    def preproc(self, string, why, reg=re.compile("")):
        # If it starts with '/', change to '_'
        if why in ('exec', 'eval'):
            string = string.strip()
            if string[0] == '/':
                string = '_' + string[1:]
            return string
        elif why == 'copy':
            # Expand & < > into entitites if surrounded by whitespace
            return string

    def copyfile(self, filename, ext="html"):
        "Convert filename.* to filename.ext, where ext defaults to html."
        global yaptu_filename
        outname = re.sub('[.][a-zA-Z0-9]+?$', '', filename) + '.'+ext
        print 'Transforming', filename, 'to', outname
        self.globals['_bl'] = file(filename).readlines()
        yaptu_filename = filename
        self.outf = file(outname, 'w')
        self.copyblock()

    def copyout(self, templatefile, outfile):
        self.globals['_bl'] = templatefile.readlines()
        self.globals['_outf'] = outfile
        self.outf = outfile
        self.copyblock()
#
# YAPTU snippet end
#

#---------------------------------------------------------------------
# Define global variables to be used by the template
#---------------------------------------------------------------------
# Buffer for individual CSV rows
rows = []
#---------------------------------------------------------------------

def csv_unireader(f, encoding="utf-8"):
    for row in csv.reader(codecs.iterencode(codecs.iterdecode(f, encoding), "utf-8")):
        yield [e.decode("utf-8") for e in row]

def csvToTex(templatePath, csvfile, templatefile, outfile):
    global rows

    reader = unicodecsv.DictReader(csvfile, encoding='utf-8-sig')
    rows = list(reader)

    # Check if first column is parsed incorrectly (the Date column keeps its quotes
    # and is named ""Date"". If an incorrect parsing is detected, fix it.
    for i in range(len(rows)):
        if u'"Date"' in rows[i].keys():
            rows[i][u'Date'] = rows[i].pop(u'"Date"')

    #------------------------------------------------------------------------
    #
    # Data Pre-Processing
    # NOTE: This is something that most likely should be done at the database
    #       level for efficiency reasons.
    #

    # The CSV export is unsorted, sort it by date.
    # Sorting is done by 'Date' column first, then by 'Engine Start' and 'Flight Start'
    #
    # TODO: Can we assume that these fields are always filled?
    rows.sort(key=lambda x: (datetime.datetime.strptime(x[u'Date'], '%m/%d/%Y'), datetime.datetime.strptime(x[u'Engine Start'], '%Y-%m-%d %H:%M:%SZ') if u'Engine Start' in x.keys() and x[u'Engine Start'] != u'' else datetime.datetime.min, datetime.datetime.strptime(x[u'Flight Start'], '%Y-%m-%d %H:%M:%SZ') if u'Flight Start' in x.keys() and x[u'Flight Start'] != u'' else datetime.datetime.min))

    # 'Landings' always contains the sum of landings. For the logbook we need
    # to distinguish between day and night landings. Since these are not always
    # filled, we apply the following logic here:
    # If day and night landings are both 0, we assume that the total number of
    # landings are day landings.
    # If either day or night landings are filled with a value, the total number
    # of landings is ignored.
    # TODO: Deal with corner case where the sum of day and night landings does
    #       not equal the number of total landings (this could happen if total
    #       landings is filled out and night landings is only filled with the
    #       number of night landings, while day landings is left at 0).
    for i in range(len(rows)):
        if rows[i][u'FS Day Landings'] == '0' and rows[i][u'FS Night Landings'] == '0':
            rows[i][u'FS Day Landings'] = rows[i][u'Landings']

    #------------------------------------------------------------------------

    # Read template and process it, output will be sent to stdout
    copyGlobals = globals()
    copyGlobals['_templatePath'] = templatePath
    copier = Copier(copyGlobals)
    copier.copyout(templatefile, outfile)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:\n%s <CSV file>\n\n<CSV file>\tInput file to process.\n\nOutput is sent to stdout.' % (sys.argv[0])
        exit()

    with open(sys.argv[1], 'rb') as csvfile:
        csvToTex('', csvfile, file('logbook_template.tex.py'), sys.stdout)
