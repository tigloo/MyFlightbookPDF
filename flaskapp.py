# -*- coding: utf-8 -*-

from flask import Flask, send_file
from flask import request
from flask import Response
import tempfile
import os
import shutil
from subprocess import call
import logbook
import sys
import logging
import StringIO

LOCALES = [u"bg_BG", u"cs_CZ", u"da_DK", u"de_DE", u"el_GR", u"en_US", u"es_ES", u"et_EE", u"fi_FI", u"fr_FR",
           u"hr_HR", u"hu_HU", u"it_IT", u"lt_LT", u"lv_LV", u"nl_NL", u"no_NO", u"pl_PL", u"pt_PT", u"ro_RO",
           u"ru_RU", u"sk_SK", u"sl_SI", u"sv_SE", u"tr_TR", u"zh_CN"]

# This is the path to latex INCLUDING a trailing slash
PATH_TO_LATEX = ''
PATH_TO_TEMPLATES = ''
if 'OPENSHIFT_REPO_DIR' in os.environ.keys():
    PATH_TO_TEMPLATES = os.environ['OPENSHIFT_REPO_DIR']
    PATH_TO_LATEX = os.environ['OPENSHIFT_REPO_DIR'] + 'openshift-origin-cartridge-texlive-master/bin/x86_64-linux/'
    if(os.path.isfile(PATH_TO_LATEX + 'lualatex') == False):
        # Seemingly we do not run on OpenShift, so assume that pdfLateX is in the path
        PATH_TO_LATEX = ''

# __file__ refers to the file settings.py 
APP_ROOT = os.path.dirname(os.path.abspath(__file__))  # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')

app = Flask(__name__)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

@app.route('/')
def root():
    return send_file('mainform.html')


@app.route('/compile', methods=['POST'])
def compile():
    global LOCALES

    if request.method == 'POST':
        # Get uploaded input file
        inFile = request.files['csvfile']

        # Create temporary directory
        tmpDir = tempfile.mkdtemp()

        # Temporarily write uploaded input file to disk because Flask's Unicode handling seems broken
        # This is a dirty hack because Unicode decoding should work within memory, too
        tmpFile = open('%s/tmpdata.csv' % (tmpDir), 'w')
        tmpFile.write(inFile.read())
        tmpFile.close()

        # Re-assign inFile to point to the cached upload
        inFile = open('%s/tmpdata.csv' % (tmpDir), 'rb')

        # Create temporary output file names
        texFileName = tmpDir + '/output.tex'
        pdfFileName = tmpDir + '/output.pdf'
        templateFileName = PATH_TO_TEMPLATES + 'logbook_template.tex.py'

        pilotDetails = {}
        pilotDetails[u'name'] = request.form['pilot_name']
        pilotDetails[u'address1'] = request.form['address1']
        pilotDetails[u'address2'] = request.form['address2']
        pilotDetails[u'address3'] = request.form['address3']
        pilotDetails[u'licenseNr'] = request.form['license_nr']

        # Validate locale
        selectedLocale = 'en_US'
        if request.form['locale'] in LOCALES:
            selectedLocale = request.form['locale'].encode('utf-8')

        # Generate LateX output
        texFile = file(texFileName, 'w')
        logbook.csvToTex(PATH_TO_TEMPLATES, inFile, pilotDetails, selectedLocale, file(templateFileName), texFile)
        texFile.close()

        # Compile to PDF
        call(["%slualatex" % (PATH_TO_LATEX), "--interaction=nonstopmode", "--output-directory=%s" % (tmpDir), texFileName])

        pdfFile = file(pdfFileName, 'r')
        result = pdfFile.read()
        pdfFile.close()

        shutil.rmtree(tmpDir)

        return Response(result, mimetype='application/pdf')

    return ''

if __name__ == '__main__':
    app.run(debug='True')
