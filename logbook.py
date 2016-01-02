# -*- coding: utf-8 -*-

import codecs
import csv
import unicodecsv
import sys
import re
import datetime
import math
import locale
import argparse

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

def texEscape(text):
    CHARS = [
        [u'\\', u'\\letterbackslash{}'],
        [u'&',  u'\\&'],
        [u'%',  u'\\%'],
        [u'$',  u'\\$'],
        [u'#',  u'\\#'],
        [u'_',  u'\\letterunderscore{}'],
        [u'{',  u'\\letteropenbrace{}'],
        [u'}',  u'\\letterclosebrace{}'],
        [u'~',  u'\\lettertilde{}'],
        [u'^',  u'\\letterhat{}']
    ]

    retval = text

    for i in range(len(CHARS)):
        retval = retval.replace(CHARS[i][0], CHARS[i][1])

    return retval

#
# Returns -1 for x < y
# Returns 0 for x == y
# Returns 1 for x > y
def rowDateCompare(x, y):
    xDateStr = x[u'Date']
    xEngineStartStr = x[u'Engine Start'] if u'Engine Start' in x.keys() else u''
    xFlightStartStr = x[u'Flight Start'] if u'Flight Start' in x.keys() else u''

    xDate = datetime.datetime.strptime(xDateStr, '%Y-%m-%d')
    xEngineStart = datetime.datetime.strptime(xEngineStartStr, '%Y-%m-%d %H:%M:%SZ') if xEngineStartStr != u'' else datetime.datetime.min
    xFlightStart = datetime.datetime.strptime(xFlightStartStr, '%Y-%m-%d %H:%M:%SZ') if xFlightStartStr != u'' else datetime.datetime.min

    yDateStr = y[u'Date']
    yEngineStartStr = y[u'Engine Start'] if u'Engine Start' in y.keys() else u''
    yFlightStartStr = y[u'Flight Start'] if u'Flight Start' in y.keys() else u''

    yDate = datetime.datetime.strptime(yDateStr, '%Y-%m-%d')
    yEngineStart = datetime.datetime.strptime(yEngineStartStr, '%Y-%m-%d %H:%M:%SZ') if yEngineStartStr != u'' else datetime.datetime.min
    yFlightStart = datetime.datetime.strptime(yFlightStartStr, '%Y-%m-%d %H:%M:%SZ') if yFlightStartStr != u'' else datetime.datetime.min

    if xDate < yDate:
        return -1

    if xDate > yDate:
        return 1

    # Flight dates are equal, sort by engine start
    if xEngineStart < yEngineStart:
        return -1

    if xEngineStart > yEngineStart:
        return 1

    # Engine start dates are equal (probably due to being datetime.min), sort by flight start
    if xFlightStart < yFlightStart:
        return -1

    if xFlightStart > yFlightStart:
        return 1

    return 0

def csvToTex(templatePath, csvfile, pilotDetails, localeToUse, templatefile, outfile):
    global rows

    # NOTE: It is bad practice to just set a new locale and not reset it before returning.
    # However, it doesn't make sense to reset it either and retrieving all locale settings is cumbersome.
    try:
        locale.setlocale(locale.LC_ALL, localeToUse)
    except locale.Error:
        # If we did not succeed in setting the locale, use en_US as default
        locale.setlocale(locale.LC_ALL, 'en_US')

    # Determine thousands-separator. We use the opposite of the decimal point because in some locales
    # it may not be set even though it is present in the CSV data.
    thousandsSeparator = ',' if locale.localeconv()['decimal_point'] == '.' else '.'

    # Sniff to detect delimiter and other format parameters
    sniffBuffer = csvfile.read(2048)
    csvfile.seek(0)

    # Detect CSV dialect
    dialect = unicodecsv.Sniffer().sniff(sniffBuffer, ',;')

    # We know that quotes need to be used
    dialect.quoting = csv.QUOTE_ALL
    dialect.doublequote = True

    # Detect file encoding
    if sniffBuffer.startswith(codecs.BOM_UTF8):
        encoding = 'utf-8-sig'
    else:
        encoding = 'utf-8'

    reader = unicodecsv.DictReader(csvfile, dialect=dialect, encoding=encoding)
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
    #rows.sort(cmp=rowDateCompare)
    rows.sort(key=lambda x: (datetime.datetime.strptime(x[u'Date'], '%Y-%m-%d'), datetime.datetime.strptime(x[u'Engine Start'], '%Y-%m-%d %H:%M:%SZ') if u'Engine Start' in x.keys() and x[u'Engine Start'] != u'' else datetime.datetime.min, datetime.datetime.strptime(x[u'Flight Start'], '%Y-%m-%d %H:%M:%SZ') if u'Flight Start' in x.keys() and x[u'Flight Start'] != u'' else datetime.datetime.min))

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

        # Remove anonymous tail numbers
        if rows[i][u'Tail Number'].startswith(u'#'):
            rows[i][u'Tail Number'] = u'N/A'

        # Escape user supplied content
        rows[i][u'Model'] = texEscape(rows[i][u'Model'])
        rows[i][u'Tail Number'] = texEscape(rows[i][u'Tail Number'])
        rows[i][u'Category/Class'] = texEscape(rows[i][u'Category/Class'])
        rows[i][u'Route'] = texEscape(rows[i][u'Route'])
        rows[i][u'Flight Properties'] = texEscape(rows[i][u'Flight Properties'])
        rows[i][u'Comments'] = texEscape(rows[i][u'Comments'])

        # Remove thousands-separator if it is present
        rows[i][u'Total Flight Time'] = rows[i][u'Total Flight Time'].replace(thousandsSeparator, '')
        rows[i][u'FS Day Landings'] = rows[i][u'FS Day Landings'].replace(thousandsSeparator, '')
        rows[i][u'FS Night Landings'] = rows[i][u'FS Night Landings'].replace(thousandsSeparator, '')
        rows[i][u'Night'] = rows[i][u'Night'].replace(thousandsSeparator, '')
        rows[i][u'IMC'] = rows[i][u'IMC'].replace(thousandsSeparator, '')
        rows[i][u'PIC'] = rows[i][u'PIC'].replace(thousandsSeparator, '')
        rows[i][u'SIC'] = rows[i][u'SIC'].replace(thousandsSeparator, '')
        rows[i][u'Dual Received'] = rows[i][u'Dual Received'].replace(thousandsSeparator, '')
        rows[i][u'CFI'] = rows[i][u'CFI'].replace(thousandsSeparator, '')

    # Escape pilot details
    for key in pilotDetails:
        pilotDetails[key] = texEscape(pilotDetails[key])

    #------------------------------------------------------------------------

    # Read template and process it, output will be sent to stdout
    copyGlobals = globals()
    copyGlobals['_templatePath'] = templatePath
    copyGlobals['_pilotDetails'] = pilotDetails
    copier = Copier(copyGlobals)
    copier.copyout(templatefile, outfile)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Logbook compiler for Myflightbook.com. Takes CSV files as input and translates it to TeX code.')
    parser.add_argument('--locale', help='Locale to use')
    parser.add_argument('--pilotname', help='Pilot\'s name')
    parser.add_argument('--address1', help='Address line 1')
    parser.add_argument('--address2', help='Address line 2')
    parser.add_argument('--address3', help='Address line 3')
    parser.add_argument('--license', help='License number. Individual license numbers may be separated via semicolon (\';\')')
    parser.add_argument('csvfile', help='Input file to process')

    args = parser.parse_args()

    pilotDetails = {}
    pilotDetails[u'name'] = '' if args.pilotname == None else args.pilotname
    pilotDetails[u'address1'] = '' if args.address1 == None else args.address1
    pilotDetails[u'address2'] = '' if args.address1 == None else args.address2
    pilotDetails[u'address3'] = '' if args.address1 == None else args.address3
    pilotDetails[u'licenseNr'] = '' if args.address1 == None else args.license

    with open(args.csvfile, 'rb') as csvfile:
        csvToTex('', csvfile, pilotDetails, args.locale, file('logbook_template.tex.py'), sys.stdout)
