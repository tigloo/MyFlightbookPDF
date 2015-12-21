from flask import Flask, send_file
from flask import request
import tempfile
import os
import logbook

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

        # Create a temporary output file
        texFileName = tempfile.mkstemp()[1]

        texFile = file(texFileName, 'w')
        logbook.csvToTex(inFile, texFile)
        texFile.close()

        #os.remove(texFileName)

        texFile = file(texFileName, 'r')
        return texFile.read()

    return ''

if __name__ == '__main__':
    app.run(debug='True')
