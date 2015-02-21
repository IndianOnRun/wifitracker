from flask import render_template, request
from app import app
import os
from functools import wraps

# Mock stuff.
import mock_database

# Database imports.
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect, MetaData
import database

# TODO: Remove this shit.
engine = None
session = None

# Wrappers.
def databaseUploadRequired(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print app.config['DATABASE']
        if not os.path.isfile(app.config['DATABASE']):
            return render_template('databaseNotUploaded.html', title="Uh-oh!")
        initializeDatabaseIfNotInitialized()
        return f(*args, **kwargs)
    return decorated_function

def initializeDatabaseIfNotInitialized():
    global engine
    if engine is None:
    	engine = database.buildEngine(app.config['DATABASE'])
    	print "engine built!"
    	m = MetaData()
    	m.reflect(engine)
    	for table in m.tables.values():
    		print table.name
    		for c in table.c:
    			print c.name

        database.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        global session
        session = Session()
        print "session set up"


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

# TODO: Add in the ability to have parameters to further drill down the views.
@app.route('/packetView')
@databaseUploadRequired
def packetView():
    title = 'Packet-by-Packet View'
    template = 'packetView.html'
    packets = session.query(database.Packet)
    return render_template(template, title=title, packets=packets)

@app.route('/densityGraph')
@databaseUploadRequired
def densityGraph():
    title = 'Density Graph'
    template = 'densityGraph.html'
    packets = mock_database.getPackets(10)

    # Attempt to get the real database.
    initializeDatabaseIfNotInitialized();



    return render_template(template, title=title, packets=packets)

@app.route('/loadDatabase', methods=['GET', 'POST'])
def uploadDatabase():
	uploadCompleteTitle = 'Upload Complete!'
	uploadCompleteTemplate = 'uploadComplete.html'

	uploadTitle = 'Upload a SQLite Database'
	uploadTemplate = 'loadDatabase.html'

	# Handle the file upload request.
	if request.method == 'POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			filename = "packetDatabase.db"
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			print "wooho"
			return render_template(uploadCompleteTemplate, title=uploadCompleteTitle)
		return render_template(uploadTemplate, title=uploadTitle, error="There was a problem uploading the file.")

	# Default to showing the upload.
	return render_template(uploadTemplate, title=uploadTitle)

'''
####################
##HELPER FUNCTIONS##
####################
'''
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# TODO: Add a page which visualizes the density of a user's presence by day of the week and time.