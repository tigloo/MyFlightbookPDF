\documentclass{article}

\usepackage[utf8]{inputenc}
\usepackage{graphicx}
\usepackage{tabu}
\usepackage[table,x11names]{xcolor}
\usepackage{fancyhdr}
\usepackage{pifont}
\usepackage{pbox}

\usepackage[a4paper,landscape,left=1cm,right=1cm,headheight=40pt,foot=80pt]{geometry}

\usepackage{multirow}

\newcolumntype{L}[1]{>{\raggedright\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}
\newcolumntype{C}[1]{>{\centering\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}
\newcolumntype{R}[1]{>{\raggedleft\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}

\pagestyle{fancy}

\fancyhead{}
\fancyfoot[L]{\fontfamily{lmss}\selectfont \small Logbook format according to EASA Part FCL.050}
\fancyfoot[R]{\fontfamily{lmss}\selectfont Page \thepage}
\fancyfoot[C]{\fontfamily{lmss}\selectfont \small Column 1 in local time, all others in UTC. Date format according to ISO 8601.}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}

\begin{document}

\fontfamily{lmss}\selectfont

#[
_outf.write('\\centerline{\\includegraphics[width=0.6\\textwidth]{%smyflightbook.png}}' % (_templatePath))
#]

\vspace{10pt}

\begin{center}
\Large
Pilot's Logbook for

\vspace{10pt}
\renewcommand{\arraystretch}{1.5}
\begin{tabu}{|m{0.2\textwidth}m{0.2\textwidth}|}
\hline
#[
_outf.write(('Name: & %s \\\\' % (_pilotDetails[u'name'])).encode('utf-8'))
#]
\cline{2-2}
#[
_outf.write(('Address: & %s \\\\' % (_pilotDetails[u'address1'])).encode('utf-8'))
#]
\cline{2-2}
#[
_outf.write((' & %s \\\\' % (_pilotDetails[u'address2'])).encode('utf-8'))
#]
\cline{2-2}
#[
_outf.write((' & %s \\\\' % (_pilotDetails[u'address3'])).encode('utf-8'))
#]
\cline{2-2}
#[
if len(_pilotDetails[u'licenseNr']) > 1:
    licenseStr = u''
    for license in _pilotDetails[u'licenseNr'].split(';'):
        licenseStr += '%s \\\\ \n & ' % license
    licenseStr += '\\\\ \n'
    _outf.write(('License Number(s): & %s' % (licenseStr)).encode('utf-8'))
else:
    _outf.write(('License Number(s): & \\\\').encode('utf-8'))
    _outf.write(('\\cline{2-2} ').encode('utf-8'))
    _outf.write((' & \\\\').encode('utf-8'))
#]
\hline
\end{tabu}
\end{center}

\pagebreak

#[
_outf.write(('\\fancyhead[C]{\\includegraphics[width=3cm]{%smyflightbook.png}}' % (_templatePath)).encode('utf-8'))
_outf.write(('\\fancyhead[R]{\\fontfamily{lmss}\\selectfont \\small %s \\linebreak License Number(s): %s}' % (_pilotDetails[u'name'], _pilotDetails[u'licenseNr'])).encode('utf-8'))
#]

\rowcolors{1}{white}{Snow2}
\renewcommand{\arraystretch}{3.2}

#[
#---------------------------------------------------------------------
# Number of flights to include on a single page
RowsPerPage = 12
#---------------------------------------------------------------------

currentRowInTable = 0

totalCategoryLastPage = {}
totalDayLandingsLastPage = 0
totalNightLandingsLastPage = 0
totalFlightTimeLastPage = 0.0
totalNightLastPage = 0.0
totalIMCLastPage = 0.0
totalPICLastPage = 0.0
totalSICLastPage = 0.0
totalDualLastPage = 0.0
totalCFILastPage = 0.0
#]

#[ while currentRowInTable < len(rows):

\noindent\resizebox{\textwidth}{!}{
    \begin{tabu}{|[1.5pt]m{0.015\textwidth}|l|l|m{0.07\textwidth}|l|m{0.07\textwidth}|m{0.14\textwidth}|m{0.1\textwidth}|m{0.2\textwidth}|l|L{5cm}|l|l|[1.5pt]m{0.05\textwidth}|m{0.05\textwidth}|m{0.05\textwidth}|m{0.05\textwidth}|m{0.05\textwidth}|l|l|l|m{0.08\textwidth}|m{0.25\textwidth}|[1.5pt]}

\hiderowcolors

\tabucline[1.5pt]-
\multirow{3}{*}{No} & 1 & \multicolumn{2}{l|}{2} & \multicolumn{2}{l|}{3} & \multicolumn{2}{l|}{4} & 5 & 6 & 7 & \multicolumn{2}{l|[1.5pt]}{8} & \multicolumn{2}{l|}{9} & \multicolumn{4}{l|}{10} & \multicolumn{3}{l|}{11} & 12 \\
\cline{2-23}

 & \multirow{2}{*}{DATE} & \multicolumn{2}{l|}{DEPARTURE} & \multicolumn{2}{l|}{ARRIVAL} & \multicolumn{2}{l|}{AIRCRAFT} & \multirow{2}{*}{CATEGORY} & \multirow{2}{0.05\textwidth}{TOTAL TIME OF FLIGHT} & \multirow{2}{*}{NAME(S) PIC} & \multicolumn{2}{l|[1.5pt]}{LANDINGS} & \multicolumn{2}{p{0.1\textwidth}|}{OPERATIONAL CONDITION TIME} & \multicolumn{4}{l|}{PILOT FUNCTION TIME} & \multicolumn{3}{l|}{FSTD SESSION} & \multirow{2}{0.2\textwidth}{REMARKS AND ENDORSEMENTS} \\
\cline{3-8} \cline{12-22}
 & & PLACE & TIME & PLACE & TIME & MAKE, MODEL, VARIANT & REGISTRATION & & & & DAY & NIGHT & NIGHT & IFR & PIC & SIC & DUAL & CFI & DATE & TYPE & TOTAL TIME OF SESSION & \\

\showrowcolors
\tabucline[1.5pt]-

#[
totalCategoryThisPage = {}
totalDayLandingsThisPage = 0
totalNightLandingsThisPage = 0
totalFlightTimeThisPage = 0.0
totalNightThisPage = 0.0
totalIMCThisPage = 0.0
totalPICThisPage = 0.0
totalSICThisPage = 0.0
totalDualThisPage = 0.0
totalCFIThisPage = 0.0

for i in range(RowsPerPage):

    if currentRowInTable >= len(rows):
        # We exceeded the logbook, so print an empty line to fill the table properly
        _outf.write(u' & & & & & & & & & & & & & & & & & & & & & & \\\\')
    else:
        # The CSV export contains different date formats, so parse them individually
        logDate = datetime.datetime.strptime(rows[currentRowInTable][u'Date'], '%Y-%m-%d')

        # Replace dashes in route with spaces to be able to work with airport codes separated by either spaces or dashes
        rows[currentRowInTable][u'Route'] = rows[currentRowInTable][u'Route'].replace('-', ' ')
        route = rows[currentRowInTable][u'Route'].split(' ')
        departureCode = route[0]
        arrivalCode   = route[-1]

        #
        # Parse flight time and calculate totals
        #
        flightTime    = 0.0 if rows[currentRowInTable][u'Total Flight Time'] == u'' else round(locale.atof(rows[currentRowInTable][u'Total Flight Time'])*60)/60
        dayLandings   = 0 if rows[currentRowInTable][u'FS Day Landings'] == u'' else locale.atoi(rows[currentRowInTable][u'FS Day Landings'])
        nightLandings = 0 if rows[currentRowInTable][u'FS Night Landings'] == u'' else locale.atoi(rows[currentRowInTable][u'FS Night Landings'])
        timeNight     = 0.0 if rows[currentRowInTable][u'Night'] == u'' else round(locale.atof(rows[currentRowInTable][u'Night'])*60)/60
        timeIMC       = 0.0 if rows[currentRowInTable][u'IMC'] == u'' else round(locale.atof(rows[currentRowInTable][u'IMC'])*60)/60
        timePIC       = 0.0 if rows[currentRowInTable][u'PIC'] == u'' else round(locale.atof(rows[currentRowInTable][u'PIC'])*60)/60
        timeSIC       = 0.0 if rows[currentRowInTable][u'SIC'] == u'' else round(locale.atof(rows[currentRowInTable][u'SIC'])*60)/60
        timeDual      = 0.0 if rows[currentRowInTable][u'Dual Received'] == u'' else round(locale.atof(rows[currentRowInTable][u'Dual Received'])*60)/60
        timeCFI       = 0.0 if rows[currentRowInTable][u'CFI'] == u'' else round(locale.atof(rows[currentRowInTable][u'CFI'])*60)/60
        flightStart   = rows[currentRowInTable][u'Flight Start'] if rows[currentRowInTable][u'Engine Start'] == u'' else rows[currentRowInTable][u'Engine Start']
        flightEnd     = rows[currentRowInTable][u'Flight End'] if rows[currentRowInTable][u'Engine End'] == u'' else rows[currentRowInTable][u'Engine End']

        #
        # Remove text in parentheses from category names
        # Convert: "Helicopter (R22)" to "Helicopter"
        #
        cleanCategory = re.sub(r'\([^)]*\)', '', rows[currentRowInTable][u'Category/Class']).strip()

        if cleanCategory in totalCategoryThisPage.keys():
            totalCategoryThisPage[cleanCategory] += 1
        else:
            totalCategoryThisPage[cleanCategory] = 1

        totalFlightTimeThisPage += flightTime
        totalDayLandingsThisPage += dayLandings
        totalNightLandingsThisPage += nightLandings
        totalNightThisPage += timeNight
        totalIMCThisPage += timeIMC
        totalPICThisPage += timePIC
        totalSICThisPage += timeSIC
        totalDualThisPage += timeDual
        totalCFIThisPage += timeCFI

        _outf.write((u'%i & %s & %s & %s & %s & %s & %s & %s & %s & %d:%02d & & %i & %i & %d:%02d & %d:%02d & %d:%02d & %d:%02d & %d:%02d & %d:%02d & & & & %s %s %s \\\\ ' % (currentRowInTable+1,
            logDate.date().isoformat(),
            departureCode, flightStart,
            arrivalCode, flightEnd,
            rows[currentRowInTable][u'Model'],
            rows[currentRowInTable][u'Tail Number'],
            rows[currentRowInTable][u'Category/Class'],
            math.floor(flightTime), round(flightTime*60%60),
            dayLandings, nightLandings,
            math.floor(timeNight), round(timeNight*60%60),
            math.floor(timeIMC), round(timeIMC*60%60),
            math.floor(timePIC), round(timePIC*60%60),
            math.floor(timeSIC), round(timeSIC*60%60),
            math.floor(timeDual), round(timeDual*60%60),
            math.floor(timeCFI), round(timeCFI*60%60),
            rows[currentRowInTable][u'Flight Properties'],
            rows[currentRowInTable][u'Comments'],
            '' if len(route)<=2 else ('Route: ' + rows[currentRowInTable][u'Route']))).encode('utf-8'))

    _outf.write(u'\hline ')

    currentRowInTable += 1
#]

#[

totalFlightTime = totalFlightTimeThisPage + totalFlightTimeLastPage
totalDayLandings = totalDayLandingsThisPage + totalDayLandingsLastPage
totalNightLandings = totalNightLandingsThisPage + totalNightLandingsLastPage
totalNight = totalNightThisPage + totalNightLastPage
totalIMC = totalIMCThisPage + totalIMCLastPage
totalPIC = totalPICThisPage + totalPICLastPage
totalSIC = totalSICThisPage + totalSICLastPage
totalDual = totalDualThisPage + totalDualLastPage
totalCFI = totalCFIThisPage + totalCFILastPage

#
# Sum up category totals as separate string
#
categoryTotalThisPageStr = u''
for category in totalCategoryThisPage:
    categoryTotalThisPageStr += u'%s: %i\\newline ' % (category, totalCategoryThisPage[category])

categoryTotalLastPageStr = u''
for category in totalCategoryLastPage:
    categoryTotalLastPageStr += u'%s: %i\\newline ' % (category, totalCategoryLastPage[category])

# Compute totals by joining the "this page" and "last page" totals arrays
for category in totalCategoryThisPage:
    if category in totalCategoryLastPage.keys():
        totalCategoryLastPage[category] += totalCategoryThisPage[category]
    else:
        totalCategoryLastPage[category] = totalCategoryThisPage[category]

categoryTotalStr = u''
for category in totalCategoryLastPage:
    categoryTotalStr += u'%s: %i\\newline ' % (category, totalCategoryLastPage[category])

_outf.write(u'\multicolumn{7}{l|[1.5pt]}{\cellcolor{white}} & TOTAL THIS PAGE & %s & %d:%02d & & %i & %i & %d:%02d & %d:%02d & %d:%02d & %d:%02d & %d:%02d & \\multicolumn{1}{l|[1.5pt]}{%d:%02d} & \\multicolumn{4}{c}{\\cellcolor{white}\\textbf{I certify that the entries in this log are true.}} \\\\' % (
    categoryTotalThisPageStr,
    math.floor(totalFlightTimeThisPage), round(totalFlightTimeThisPage*60%60),
    totalDayLandingsThisPage, totalNightLandingsThisPage,
    math.floor(totalNightThisPage), round(totalNightThisPage*60%60),
    math.floor(totalIMCThisPage), round(totalIMCThisPage*60%60),
    math.floor(totalPICThisPage), round(totalPICThisPage*60%60),
    math.floor(totalSICThisPage), round(totalSICThisPage*60%60),
    math.floor(totalDualThisPage), round(totalDualThisPage*60%60),
    math.floor(totalCFIThisPage), round(totalCFIThisPage*60%60)))

_outf.write(u'\cline{8-19}')

_outf.write(u'\multicolumn{7}{l|[1.5pt]}{\cellcolor{white}} & TOTAL FROM PREVIOUS PAGES & %s & %d:%02d & & %i & %i & %d:%02d & %d:%02d & %d:%02d & %d:%02d & %d:%02d & \\multicolumn{1}{l|[1.5pt]}{%d:%02d} & \\multicolumn{4}{c}{\\cellcolor{white}} \\\\' % (
    categoryTotalLastPageStr,
    math.floor(totalFlightTimeLastPage), round(totalFlightTimeLastPage*60%60),
    totalDayLandingsLastPage, totalNightLandingsLastPage,
    math.floor(totalNightLastPage), round(totalNightLastPage*60%60),
    math.floor(totalIMCLastPage), round(totalIMCLastPage*60%60),
    math.floor(totalPICLastPage), round(totalPICLastPage*60%60),
    math.floor(totalSICLastPage), round(totalSICLastPage*60%60),
    math.floor(totalDualLastPage), round(totalDualLastPage*60%60),
    math.floor(totalCFILastPage), round(totalCFILastPage*60%60)))

_outf.write(u'\cline{8-23}')

_outf.write(u'\multicolumn{7}{l|[1.5pt]}{\cellcolor{white}} & TOTAL TIMES & %s & %d:%02d & & %i & %i & %d:%02d & %d:%02d & %d:%02d & %d:%02d & %d:%02d & \\multicolumn{1}{l|[1.5pt]}{%d:%02d} & \\multicolumn{4}{c}{\\cellcolor{white}\\textbf{PILOT\'S SIGNATURE}} \\\\' % (
    categoryTotalStr,
    math.floor(totalFlightTime), round(totalFlightTime*60%60),
    totalDayLandings, totalNightLandings,
    math.floor(totalNight), round(totalNight*60%60),
    math.floor(totalIMC), round(totalIMC*60%60),
    math.floor(totalPIC), round(totalPIC*60%60),
    math.floor(totalSIC), round(totalSIC*60%60),
    math.floor(totalDual), round(totalDual*60%60),
    math.floor(totalCFI), round(totalCFI*60%60)))

totalFlightTimeLastPage += totalFlightTimeThisPage
totalDayLandingsLastPage += totalDayLandingsThisPage
totalNightLandingsLastPage += totalNightLandingsThisPage
totalNightLastPage += totalNightThisPage
totalIMCLastPage += totalIMCThisPage
totalPICLastPage += totalPICThisPage
totalSICLastPage += totalSICThisPage
totalDualLastPage += totalDualThisPage
totalCFILastPage += totalCFIThisPage
#]

\tabucline[1.5pt]{8-19}

\end{tabu}
}

\pagebreak[4]

#]

\end{document}