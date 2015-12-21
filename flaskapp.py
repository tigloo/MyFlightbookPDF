from flask import Flask
from flask import request
import tempfile

app = Flask(__name__)

@app.route('/')
def hello_world():
	return 'Hello World!'

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

