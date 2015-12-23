\documentclass{article}

\usepackage[a4paper,landscape,left=1cm,right=1cm,headheight=40pt]{geometry}

\usepackage[utf8]{inputenc}
\usepackage{graphicx}
\usepackage{tabu}
\usepackage[table,x11names]{xcolor}
\usepackage{fancyhdr}
\usepackage{pifont}
\usepackage{pbox}

\usepackage{multirow}

\newcolumntype{L}[1]{>{\raggedright\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}
\newcolumntype{C}[1]{>{\centering\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}
\newcolumntype{R}[1]{>{\raggedleft\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}

\pagestyle{fancy}
\fancyhead{}
\fancyfoot{}
#[
print '\\fancyhead[C]{\\includegraphics[width=3cm]{%smyflightbook.png}}' % (globals()['_templatePath'])
#]
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}

\begin{document}

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
totalFlightMinutesLastPage = 0
totalNightLastPage = 0.0
totalIMCLastPage = 0.0
totalPICLastPage = 0.0
totalSICLastPage = 0.0
totalDualLastPage = 0.0
totalCFILastPage = 0.0
#]

#[ while currentRowInTable < len(rows):

\noindent\resizebox{\textwidth}{!}{
    \begin{tabu}{|[1.5pt]m{0.015\textwidth}|l|l|m{0.07\textwidth}|l|m{0.07\textwidth}|l|m{0.1\textwidth}|l|l|L{5cm}|l|l|[1.5pt]m{0.05\textwidth}|m{0.05\textwidth}|m{0.05\textwidth}|m{0.05\textwidth}|m{0.05\textwidth}|l|l|l|l|m{0.2\textwidth}|[1.5pt]}

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
totalFlightMinutesThisPage = 0
totalNightThisPage = 0.0
totalIMCThisPage = 0.0
totalPICThisPage = 0.0
totalSICThisPage = 0.0
totalDualThisPage = 0.0
totalCFIThisPage = 0.0

for i in range(RowsPerPage):

    if currentRowInTable >= len(rows):
        # We exceeded the logbook, so print an empty line to fill the table properly
        _outf.write(' & & & & & & & & & & & & & & & & & & & & & & \\\\')
    else:
        # The CSV export contains different date formats, so parse them individually
        logDate = datetime.datetime.strptime(rows[currentRowInTable]['Date'], '%m/%d/%Y')

        departureCode = rows[currentRowInTable]['Route'].split(' ')[0]
        arrivalCode   = rows[currentRowInTable]['Route'].split(' ')[-1]

        #
        # Parse flight time and calculate totals
        #
        timeParts = [int(s) for s in rows[currentRowInTable]['Total Flight Time (HH:MM)'].split(':')]
        totalFlightMinutesThisPage += timeParts[0] * 60 + timeParts[1]

        dayLandings   = 0 if rows[currentRowInTable]['FS Day Landings'] == '' else int(rows[currentRowInTable]['FS Day Landings'])
        nightLandings = 0 if rows[currentRowInTable]['FS Night Landings'] == '' else int(rows[currentRowInTable]['FS Night Landings'])
        timeNight     = 0.0 if rows[currentRowInTable]['Night'] == '' else float(rows[currentRowInTable]['Night'])
        timeIMC       = 0.0 if rows[currentRowInTable]['IMC'] == '' else float(rows[currentRowInTable]['IMC'])
        timePIC       = 0.0 if rows[currentRowInTable]['PIC'] == '' else float(rows[currentRowInTable]['PIC'])
        timeSIC       = 0.0 if rows[currentRowInTable]['SIC'] == '' else float(rows[currentRowInTable]['SIC'])
        timeDual      = 0.0 if rows[currentRowInTable]['Dual Received'] == '' else float(rows[currentRowInTable]['Dual Received'])
        timeCFI       = 0.0 if rows[currentRowInTable]['CFI'] == '' else float(rows[currentRowInTable]['CFI'])

        if rows[currentRowInTable]['Category/Class'] in totalCategoryThisPage.keys():
            totalCategoryThisPage[rows[currentRowInTable]['Category/Class']] += 1
        else:
            totalCategoryThisPage[rows[currentRowInTable]['Category/Class']] = 1

        totalDayLandingsThisPage += dayLandings
        totalNightLandingsThisPage += nightLandings
        totalNightThisPage += timeNight
        totalIMCThisPage += timeIMC
        totalPICThisPage += timePIC
        totalSICThisPage += timeSIC
        totalDualThisPage += timeDual
        totalCFIThisPage += timeCFI

        _outf.write('%i & %s & %s & %s & %s & %s & %s & %s & %s & %s & & %i & %i & %d:%02d & %d:%02d & %d:%02d & %d:%02d & %d:%02d & %d:%02d & & & & %s %s \\\\' % (currentRowInTable+1,
            logDate.date().isoformat(), departureCode,
            rows[currentRowInTable]['Engine Start'], arrivalCode,
            rows[currentRowInTable]['Engine End'],
            rows[currentRowInTable]['Model'],
            rows[currentRowInTable]['Tail Number'],
            rows[currentRowInTable]['Category/Class'],
            rows[currentRowInTable]['Total Flight Time (HH:MM)'],
            dayLandings, nightLandings,
            math.floor(timeNight), round(timeNight*60%60),
            math.floor(timeIMC), round(timeIMC*60%60),
            math.floor(timePIC), round(timePIC*60%60),
            math.floor(timeSIC), round(timeSIC*60%60),
            math.floor(timeDual), round(timeDual*60%60),
            math.floor(timeCFI), round(timeCFI*60%60),
            rows[currentRowInTable]['Flight Properties'],
            rows[currentRowInTable]['Comments']))

    _outf.write('\hline')

    currentRowInTable += 1
#]

#[

thisPageHours, thisPageMinutes = divmod(totalFlightMinutesThisPage, 60)
lastPageHours, lastPageMinutes = divmod(totalFlightMinutesLastPage, 60)
totalHours, totalMinutes = divmod(totalFlightMinutesThisPage + totalFlightMinutesLastPage, 60)
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
categoryTotalThisPageStr = ''
for category in totalCategoryThisPage:
    categoryTotalThisPageStr += '%s: %i\\\\' % (category, totalCategoryThisPage[category])

categoryTotalLastPageStr = ''
for category in totalCategoryLastPage:
    categoryTotalLastPageStr += '%s: %i\\\\' % (category, totalCategoryLastPage[category])

categoryTotalStr = ''
for category in totalCategoryThisPage:
    if category in totalCategoryLastPage.keys():
        totalCategoryLastPage[category] += totalCategoryThisPage[category]
    else:
        totalCategoryLastPage[category] = totalCategoryThisPage[category]
    categoryTotalStr += '%s: %i\\\\' % (category, totalCategoryLastPage[category])

_outf.write('\multicolumn{7}{l|[1.5pt]}{\cellcolor{white}} & TOTAL THIS PAGE & \\pbox{\\textwidth}{%s} & %d:%02d & & %i & %i & %d:%02d & %d:%02d & %d:%02d & %d:%02d & %d:%02d & \\multicolumn{1}{l|[1.5pt]}{%d:%02d} & \\multicolumn{4}{c}{\\cellcolor{white}\\textbf{I certify that the entries in this log are true.}} \\\\' % (categoryTotalThisPageStr, thisPageHours, thisPageMinutes, totalDayLandingsThisPage, totalNightLandingsThisPage, math.floor(totalNightThisPage), round(totalNightThisPage*60%60), math.floor(totalIMCThisPage), round(totalIMCThisPage*60%60), math.floor(totalPICThisPage), round(totalPICThisPage*60%60), math.floor(totalSICThisPage), round(totalSICThisPage*60%60), math.floor(totalDualThisPage), round(totalDualThisPage*60%60), math.floor(totalCFIThisPage), round(totalCFIThisPage*60%60)))
_outf.write('\cline{8-19}')
_outf.write('\multicolumn{7}{l|[1.5pt]}{\cellcolor{white}} & TOTAL FROM PREVIOUS PAGES & \\pbox{\\textwidth}{%s} & %d:%02d & & %i & %i & %d:%02d & %d:%02d & %d:%02d & %d:%02d & %d:%02d & \\multicolumn{1}{l|[1.5pt]}{%d:%02d} & \\multicolumn{4}{c}{\\cellcolor{white}} \\\\' % (categoryTotalLastPageStr, lastPageHours, lastPageMinutes, totalDayLandingsLastPage, totalNightLandingsLastPage, math.floor(totalNightLastPage), round(totalNightLastPage*60%60), math.floor(totalIMCLastPage), round(totalIMCLastPage*60%60), math.floor(totalPICLastPage), round(totalPICLastPage*60%60), math.floor(totalSICLastPage), round(totalSICLastPage*60%60), math.floor(totalDualLastPage), round(totalDualLastPage*60%60), math.floor(totalCFILastPage), round(totalCFILastPage*60%60)))
_outf.write('\cline{8-23}')
_outf.write('\multicolumn{7}{l|[1.5pt]}{\cellcolor{white}} & TOTAL TIMES & \\pbox{\\textwidth}{%s} & %d:%02d & & %i & %i & %d:%02d & %d:%02d & %d:%02d & %d:%02d & %d:%02d & \\multicolumn{1}{l|[1.5pt]}{%d:%02d} & \\multicolumn{4}{c}{\\cellcolor{white}\\textbf{PILOT\'S SIGNATURE}} \\\\' % (categoryTotalStr, totalHours, totalMinutes, totalDayLandings, totalNightLandings, math.floor(totalNight), round(totalNight*60%60), math.floor(totalIMC), round(totalIMC*60%60), math.floor(totalPIC), round(totalPIC*60%60), math.floor(totalSIC), round(totalSIC*60%60), math.floor(totalDual), round(totalDual*60%60), math.floor(totalCFI), round(totalCFI*60%60)))

totalFlightMinutesLastPage += totalFlightMinutesThisPage
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