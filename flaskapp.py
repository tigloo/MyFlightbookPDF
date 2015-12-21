from flask import Flask
from flask import request
import tempfile
import os

# __file__ refers to the file settings.py 
APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')

app = Flask(__name__)

@app.route('/')
def root():
	#return app.send_file('mainform.html')
	return 'APP_ROOT says: %s<br/>Config says: %s' % (APP_ROOT, app.Config['root_path'])

@app.route('/compile', methods=['POST'])
def compile():
	if request.method == 'POST':
		# Get input file
		inFile = request.files['csvfile']

		# Create a temporary output file
		texFile = tempfile.NamedTemporaryFile('w+b',-1,'','tmp',None,False)

		texFile.close()
		texFile.delete()

	return 'Help'

if __name__ == '__main__':
	app.run()

