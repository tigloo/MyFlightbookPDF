from flask import Flask, send_file
from flask import request
from flask import Response
import tempfile
import os
import shutil
from subprocess import call
import logbook

# This is the path to pdflatex INCLUDING a trailing slash
PATH_TO_PDFLATEX = ''

# __file__ refers to the file settings.py 
APP_ROOT = os.path.dirname(os.path.abspath(__file__))  # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')

app = Flask(__name__)


@app.route('/')
def root():
    return send_file('mainform.html')


@app.route('/compile', methods=['POST'])
def compile():
    if request.method == 'POST':
        # Get input file
        inFile = request.files['csvfile']

        # Create temporary directory
        tmpDir = tempfile.mkdtemp()

        # Create temporary output file names
        texFileName = tmpDir + '/output.tex'
        pdfFileName = tmpDir + '/output.pdf'

        # Generate LateX output
        texFile = file(texFileName, 'w')
        logbook.csvToTex(inFile, texFile)
        texFile.close()

        # Compile to PDF
        call(["%spdflatex" % (PATH_TO_PDFLATEX), "-output-directory=%s" % (tmpDir), texFileName])

        pdfFile = file(pdfFileName, 'r')
        result = pdfFile.read()
        pdfFile.close()

        shutil.rmtree(tmpDir)

        return Response(result, mimetype='application/pdf')

    return ''

if __name__ == '__main__':
    app.run(debug='False')
