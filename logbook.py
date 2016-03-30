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
from collections import Counter

CONF_PILOT_NAME         = u'pilot_name'
CONF_PILOT_ADDRESS1     = u'pilot_address1'
CONF_PILOT_ADDRESS2     = u'pilot_address2'
CONF_PILOT_ADDRESS3     = u'pilot_address3'
CONF_PILOT_LICENSE_NR   = u'pilot_licensenr'

CONF_UTCONLY            = u'utc_only'               # Only use UTC dates and use flight start / engine start as date of flight
CONF_FRACTIONS          = u'fractions'              # Instead of HH:MM, use fractions of hours

# Global variable for configuration storage
CONFIGURATION_OPTIONS   = {}

def setConfigurationOption(option, value):
    global CONFIGURATION_OPTIONS

    # Escape if necessary
    if option in [CONF_PILOT_NAME, CONF_PILOT_ADDRESS1, CONF_PILOT_ADDRESS2, CONF_PILOT_ADDRESS3, CONF_PILOT_LICENSE_NR]:
        if not isinstance(value, basestring):
            value = u''
        value = texEscape(value)

    CONFIGURATION_OPTIONS[option] = value

def getConfigurationOption(option):
    if option in CONFIGURATION_OPTIONS.keys():
        return CONFIGURATION_OPTIONS[option]
    else:
        return None

def initConfiguration():
    # Default to using local time for log date and UTC for engine&flight start/end
    setConfigurationOption(CONF_UTCONLY, False)

    # Default to showing HH:MM instead of fractions
    setConfigurationOption(CONF_FRACTIONS, False)

#
# Takes a float that contains a duration (flight time, time on condition, etc.)
# and returns a formatted string, either of the form HH:MM or as fraction of hours.
# The format is chosen depending on the current configuration.
#
def durationToString(duration):
    if getConfigurationOption(CONF_FRACTIONS):
        return '%.2f' % duration
    else:
        return '%d:%02d' % (math.floor(duration), round(duration*60%60))

#
# Initializes a dictionary that stores totals for various categories.
# These totals are typically summed up per page and per logbook overall.
# The return value is an initialized dictionary.
#
def initTotals():
    totals = {}
    totals['category'] = Counter()
    totals['dayLandings'] = Counter()
    totals['nightLandings'] = Counter()
    totals['flightTime'] = Counter()
    totals['night'] = Counter()
    totals['imc'] = Counter()
    totals['pic'] = Counter()
    totals['sic'] = Counter()
    totals['dual'] = Counter()
    totals['cfi'] = Counter()

    return totals

#
# Takes a storage array initialized by initTotals(), looks up a key to collect
# totals in identified by totalKey (imc, pic, sic, dual, ...) and adds in the category
# totalCategory (AMEL, ASEL, ...) the total valueToAdd.
#
def addToTotals(storage, totalKey, totalCategory, valueToAdd):
    tmpStorage = storage
    tmpStorage[totalKey][totalCategory] += valueToAdd
    return tmpStorage

#
# Sums up to totals storage arrays. This is used to compute last page and this page totals.
# Works through all keys in storage2 and adds them to storage1 if necessary. This means
# that storage1 and storage2 are not interchangeable parameters!
# Usage: sumTotals(totalsLastPage, totalsThisPage)
# Returns: summed up array
def sumTotals(storage1, storage2):
    output = storage1
    for key in storage1:
        output[key] = storage1[key] + storage2[key]

    return output

#
# Takes a storage array and a key to collect totals in and returns a formatted string
# containing all sums per stored category.
#
def totalsString(storage, totalKey):
    categoryTotalStr = u''
    for category in storage[totalKey]:
        categoryTotalStr += u'%s: %i\\newline ' % (category, storage[totalKey][category])

    return categoryTotalStr

#
# Formatter for totalsStringFormatted():
# Formats a parameter as an integer.
#
def formatIntAsString(param):
    return '%i' % param

#
# Takes a storage array and a key to collect totals in and returns a formatted string
# containing all sums per stored category. In contrast to the previous function, this
# one omits the category itself and uses a user-supplied function to format the output.
#
def totalsStringFormatted(storage, totalKey, formatFunction):
    categoryTotalStr = u''

    for category in storage[totalKey]:
        categoryTotalStr += u'%s\\newline ' % (formatFunction(storage[totalKey][category]))

    return categoryTotalStr

#
# Returns a string with all categories separated by linebreaks
#
def allCategoriesStr(storage, totalKey):
    retval = u''

    for category in storage[totalKey]:
        retval += u'%s\\newline ' % category

    return retval

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

#
# Escape LaTeX control sequences in input variable text so that the
# string can be rendered as is. Returns the escaped string.
#
def texEscape(text):
    CHARS = {
        u'\\': u'\\textbackslash{}',
        u'&':  u'\\&',
        u'%':  u'\\%',
        u'$':  u'\\$',
        u'#':  u'\\#',
        u'_':  u'\\_',
        u'{':  u'\\{',
        u'}':  u'\\}',
        u'~':  u'\\textasciitilde{}',
        u'^':  u'\\textasciicircum{}'
    }

    CHARS = dict((re.escape(k), v) for k, v in CHARS.iteritems())
    pattern = re.compile("|".join(CHARS.keys()))
    retval = pattern.sub(lambda m: CHARS[re.escape(m.group(0))], text)

    return retval

#
# Takes a CSV file and transforms it to a TeX file which can subsequently be rendered
# by LaTeX / XeTeX / LuaLaTeX.
#
# Makes use of several global variables ("rows" and data passed via _globals) to exchange
# data with the code embedded in the template.
#
# templatePath  - Path to where the template data is stored. Must end in a slash or be empty.
# csvfile       - File handle of the CSV file.
# pilotDetails  - Information about the pilot - data is used by the template
# localeToUse   - Locale which is used to parse the CSV data (impacts decimal parsing)
# templatefile  - File handle of the template file itself
# outfile       - File handle of the TeX output
#
def csvToTex(templatePath, csvfile, localeToUse, templatefile, outfile):
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

    #------------------------------------------------------------------------

    # Read template and process it, output will be sent to stdout
    copyGlobals = globals()
    copyGlobals['_templatePath'] = templatePath
    copier = Copier(copyGlobals)
    copier.copyout(templatefile, outfile)

if __name__ == '__main__':
    initConfiguration()

    parser = argparse.ArgumentParser(description='Logbook compiler for Myflightbook.com. Takes CSV files as input and translates it to TeX code.')
    parser.add_argument('--locale', help='Locale to use')
    parser.add_argument('--pilotname', help='Pilot\'s name')
    parser.add_argument('--address1', help='Address line 1')
    parser.add_argument('--address2', help='Address line 2')
    parser.add_argument('--address3', help='Address line 3')
    parser.add_argument('--license', help='License number. Individual license numbers may be separated via semicolon (\';\')')
    parser.add_argument('--utconly', action='store_true', help='Use a simplified, UTC-only date and time format')
    parser.add_argument('--fractions', action='store_true', help='Show fractions instead of HH:MM times')
    parser.add_argument('csvfile', help='Input file to process')

    args = parser.parse_args()

    setConfigurationOption(CONF_PILOT_NAME, args.pilotname)
    setConfigurationOption(CONF_PILOT_ADDRESS1, args.address1)
    setConfigurationOption(CONF_PILOT_ADDRESS2, args.address2)
    setConfigurationOption(CONF_PILOT_ADDRESS3, args.address3)
    setConfigurationOption(CONF_PILOT_LICENSE_NR, args.license)
    setConfigurationOption(CONF_UTCONLY, args.utconly)
    setConfigurationOption(CONF_FRACTIONS, args.fractions)

    with open(args.csvfile, 'rb') as csvfile:
        csvToTex('', csvfile, args.locale, file('logbook_template.tex.py'), sys.stdout)
