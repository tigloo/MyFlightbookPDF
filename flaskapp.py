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
    if(os.path.isfile(PATH_TO_LATEX + 'texliveonfly') == False):
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

        #
        # Initialize and set logbook configuration
        #
        logbook.initConfiguration()

        logbook.setConfigurationOption(logbook.CONF_PILOT_NAME, request.form['pilot_name'])
        logbook.setConfigurationOption(logbook.CONF_PILOT_ADDRESS1, request.form['address1'])
        logbook.setConfigurationOption(logbook.CONF_PILOT_ADDRESS2, request.form['address2'])
        logbook.setConfigurationOption(logbook.CONF_PILOT_ADDRESS3, request.form['address3'])
        logbook.setConfigurationOption(logbook.CONF_PILOT_LICENSE_NR, request.form['license_nr'])

        logbook.setConfigurationOption(logbook.CONF_UTCONLY, 'utconly' in request.form)
        logbook.setConfigurationOption(logbook.CONF_FRACTIONS, 'fractions' in request.form)

        # Validate locale
        selectedLocale = 'en_US'
        if request.form['locale'] in LOCALES:
            selectedLocale = request.form['locale'].encode('utf-8')

        # Generate LateX output
        texFile = file(texFileName, 'w')
        logbook.csvToTex(PATH_TO_TEMPLATES, inFile, selectedLocale, file(templateFileName), texFile)
        texFile.close()

        # Compile to PDF
        if len(PATH_TO_LATEX) > 1:
            call(["%stexliveonfly" % (PATH_TO_LATEX), "--texlive_bin=%s" % (PATH_TO_LATEX), "--compiler=xelatex", "--arguments=--output-directory=%s" % (tmpDir), texFileName])
        else:
            call(["%stexliveonfly" % (PATH_TO_LATEX), "--compiler=xelatex", "--arguments=--output-directory=%s" % (tmpDir), texFileName])

        pdfFile = file(pdfFileName, 'r')
        result = pdfFile.read()
        pdfFile.close()

        shutil.rmtree(tmpDir)

        return Response(result, mimetype='application/pdf')

    return ''

if __name__ == '__main__':
    app.run(debug='True')
