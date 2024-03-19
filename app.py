from flask import Flask, render_template, request, redirect, url_for, jsonify           # import the Flask class from the flask module
import psycopg2                                                                         # import psycopg2 - how I connect and interact with postgresql
from forms import NewWeldForm                                                           # import NewWeldForm, CommentForm <-- for testing
from datetime import datetime


#####################################
### INITIALIZE APP AND DB OBJECTS ###
#####################################

app = Flask(__name__)                                                                   # create the app Flask object
app.config["SECRET_KEY"] = "not_so_secret"                                              # something I have to do to protect my app
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:postgres@localhost:5432/weld_tracker' 
db = SQLAlchemy(app)

###############################
### CREATING DATABSE MODELS ###
###############################

class Spools(db.Model):                                                                                         # creating a Spools sub-class of the db.Model class
    id = db.Column(db.Integer, primary_key = True)                                                              # primary key column
    line_number = db.Column(db.String(80), index = True, unique = False)
    drawing_number = db.Column(db.String(80), index = True, unique = False)
    revision_number = db.Column(db.String(5), index = True, unique = False)
    line_spec = db.Column(db.String(80), index = True, unique = False)
    spool_number = db.Column(db.String(80), index = True, unique = True)
    dwg_issued_date = db.Column(db.Date, index = True, unique = False)
    welded_date = db.Column(db.Date, index = True, unique = False)
    nde_date = db.Column(db.Date, index = True, unique = False)
    pwht_date = db.Column(db.Date, index = True, unique = False)
    hydro_date = db.Column(db.Date, index = True, unique = False)
    welds_spool = db.relationship('Welds', backref='spools', lazy=True)
    hydros_spool = db.relationship('Hydros', backref='spools', lazy=True)

class Welds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spool_number = db.Column(db.String(80), db.ForeignKey('spools.spool_number'), index = True, unique = True)
    weld_id = db.Column(db.String(5), index = True, unique = False)
    weld_size = db.Column(db.Integer)
    weld_schedule = db.Column(db.String(5))
    weld_type = db.Column(db.String(10))
    welder = db.Column(db.String(10))
    welded_date = db.Column(db.Date)
    vt = db.Column(db.String(5))
    vt_date = db.Column(db.Date)
    nde_number = db.Column(db.String(50))
    nde_date = db.Column(db.Date)

class Hydros(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    line_number = db.Column(db.String(80), index = True, unique = False)
    drawing_number = db.Column(db.String(80), index = True, unique = False)
    revision_number = db.Column(db.String(5), index = True, unique = False)
    line_spec = db.Column(db.String(80), index = True, unique = False)
    spool_number = db.Column(db.String(80), db.ForeignKey('spools.spool_number'), index = True, unique = True)
    test_pressure_min = db.Column(db.String(100))
    test_pressure_max = db.Column(db.String(100))



def connection():
    return psycopg2.connect(
    database="weld_tracker",    # this is my weld tracker database
    user="postgres",            # this the connection username
    password="postgres",        # this is connection password
    host="localhost",           # this is my defaul host, localhost
    port="5432"                 # PostgreSQL 16 server is set to port 5432
    )

@app.route('/', methods=["GET", "POST"])                                                                         # main route for the home page
def index():
    return render_template("index.html")

@app.route('/welds', methods=["GET", "POST"])                                           # adding the post method to be able to send data back to server
def welds():
    #create an instance of the new weld form
    new_weld_form = NewWeldForm()

    # establish connection and pull weld data
    con = connection()
    cur = con.cursor()                                  # creating a cursor object so I can use the functions in the class
    cur.execute("SELECT * FROM welds ORDER BY id;")     # using the execute function to execute an SQL command
    welds_data = cur.fetchall()                         # fetching all the records and saving into a variable called result

    if new_weld_form.validate_on_submit():    
        spool = new_weld_form.new_weld_spool.data.upper()
        weld = new_weld_form.new_weld_weld.data.upper()
        size = new_weld_form.new_weld_size.data
        schedule = new_weld_form.new_weld_thick.data.upper()
        type = new_weld_form.new_weld_type.data.upper()
        # keep welder as None if empty string
        if new_weld_form.new_weld_welder.data == "":
            welder = None
        else:
            welder = new_weld_form.new_weld_welder.data
        weld_date = new_weld_form.new_weld_weld_date.data
        if new_weld_form.new_weld_vt.data == "":
            vt = None
        else:
            vt = new_weld_form.new_weld_vt.data
        vt_date = new_weld_form.new_weld_vt_date.data
        if new_weld_form.new_weld_nde_number.data == "":
            nde_number = None
        else:
            nde_number = new_weld_form.new_weld_nde_number.data
        nde_date = new_weld_form.new_weld_nde_date.data
        
        con = connection()
        cur = con.cursor()  
        cur.execute("""
                    INSERT INTO welds (spool_number, weld_id, weld_size, weld_schedule, weld_type, welder, welded_date, vt, vt_date, nde_number, nde_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (spool, weld, size, schedule, type, welder, weld_date, vt, vt_date, nde_number, nde_date))
        con.commit()
        cur.close()              # responsibly closing the cursoer
        con.close()              # as well as the connection

        return redirect(url_for('welds'))
    cur.close()              # responsibly closing the cursoer
    con.close()              # as well as the connection

    return render_template("welds.html", table_data = welds_data, new_weld = new_weld_form) # new_weld is template variable to be used in template

def checkIfNone(toCheck):
    if toCheck == "None" or toCheck == "none":
        return None
    else:
        return toCheck.upper()

def checkIfNoneDate(toCheck):
    if toCheck == "None" or toCheck == "none":
        return None
    else:
        return datetime.strptime(toCheck, "%Y-%m-%d").date()

def listToEntity(listOfStrings):
    entity = {
    "id": int(listOfStrings[0]),
    "spool": listOfStrings[1].upper(),
    "weld": listOfStrings[2].upper(),
    "size": int(listOfStrings[3]),
    "thick": listOfStrings[4].upper(),
    "type": listOfStrings[5].upper(),
    "welder": checkIfNone(listOfStrings[6]),
    "weld_date": checkIfNoneDate(listOfStrings[7]),
    "vt": checkIfNone(listOfStrings[8]),
    "vt_date": checkIfNoneDate(listOfStrings[9]),
    "nde_number": checkIfNone(listOfStrings[10]),
    "nde_date": checkIfNoneDate(listOfStrings[11])
    }
    return entity

### START OF UPDATE WELDS 
@app.route('/welds/edit', methods=["POST"])
def updateWelds():
    # get data from server
    request_data = request.get_json()
    # split it into a list
    listed_data = request_data.split()
    # convert to a dict
    dicted_data = listToEntity(listed_data)
  
    # establish the connection using the connect() function of psycopg2 module
    con = connection()
    cur = con.cursor()                           # creating a cursor object so I can use the functions (primarily execute) in the class
    # USE THE CURSOR TO EXECUTE SOME SQL
    cur.execute("""UPDATE welds
                       SET spool_number = %s, weld_id = %s, weld_size = %s, weld_schedule = %s, weld_type = %s, welder = %s, welded_date = %s, vt = %s,
                       vt_date = %s, nde_number = %s, nde_date = %s
                       WHERE id = %s;
                       """, (dicted_data["spool"], dicted_data["weld"], dicted_data["size"], dicted_data["thick"], dicted_data["type"], dicted_data["welder"], 
                             dicted_data["weld_date"], dicted_data["vt"], dicted_data["vt_date"], dicted_data["nde_number"], dicted_data["nde_date"], dicted_data["id"]))
    con.commit()             # commit data to DB
    cur.close()              # responsibly closing the cursoer
    con.close()              # as well as the connection

    return jsonify("Post request worked!")

@app.route('/spools')
def spools():
    return render_template("spools.html", table_data = spools_data)

@app.route('/hydros')
def hydros():
    return render_template("hydros.html", table_data = hydros_data)

### Basic database connection stuff
### need to connect at each route or else the updated information doesn't get rendered

# establish the connection using the connect() function of psycopg2 module
con = connection()

cur = con.cursor()                           # creating a cursor object so I can use the functions in the class

cur.execute("SELECT * FROM spools;")         # doing the same for spools
spools_data = cur.fetchall()

cur.execute("SELECT * FROM hydros;")         # and finally for hydros (currently no data in db)
hydros_data = cur.fetchall()

cur.close()              # responsibly closing the cursoer
con.close()              # as well as the connection