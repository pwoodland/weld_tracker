##################################################
### V0.05 UPDATED WELDS VIEW TO USE SQLALCHEMY ###
### NEXT UP: UPDATE SPOOLS AND HYDROS TABLE TO USE SQL ALCHEMY
##################################################

from flask import Flask, render_template, request, redirect, url_for, jsonify           # import the Flask class from the flask module
import psycopg2                                                                         # import psycopg2 - how I connect and interact with postgresql
from forms import NewWeldForm                                                           # import NewWeldForm, CommentForm <-- for testing
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select


###############################################
###     INITIALIZE APP AND DB OBJECTS       ###
###############################################


app = Flask(__name__)                                                                   # create the app Flask object
app.config["SECRET_KEY"] = "not_so_secret"                                              # something I have to do to protect my app

#######################
### SQLALCHEMY INIT ###
#######################
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@localhost:5432/weld_tracker"
db = SQLAlchemy(app)

###############################################
###           DATABASE MODELS               ###
###############################################

class Spools(db.Model):                                                                                        
    id = db.Column(db.Integer, primary_key = True)                                                              
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

###############################################
###   some connection managment functions   ###
###############################################

def connection():
    return psycopg2.connect(
    database="weld_tracker",    # this is my weld tracker database
    user="postgres",            # this the connection username
    password="postgres",        # this is connection password
    host="localhost",           # this is my defaul host, localhost
    port="5432"                 # PostgreSQL 16 server is set to port 5432
    )

def end_con(cursor, connection):
    cursor.close()
    connection.close()

##############################################
### data processing functions             #### 
##############################################
    
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

############################################################################################################################################################
###############################################
###             MAIN ROUTES                 ###
###############################################

### INDEX ###    
@app.route('/', methods=["GET", "POST"])                                                                         # main route for the home page
def index():
    return render_template("index.html")

### WELDS ###
@app.route('/welds', methods=["GET", "POST"])                                           # adding the post method to be able to send data back to server
def welds():
    #create an instance of the new weld form
    new_weld_form = NewWeldForm()

    ### gets all the records using Flask-SQLAlchemy
    welds_data = db.session.execute(db.select(Welds).order_by(Welds.id)).scalars().all()

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
        
        #create a new weld record and add it to the database using Flask-SQLAlchemy
        new_weld_data = Welds(
            spool_number=spool, weld_id=weld, weld_size=size, weld_schedule=schedule, weld_type=type, welder=welder, welded_date=weld_date,
            vt=vt, vt_date=vt_date, nde_number=nde_number, nde_date=nde_date
        )
        db.session.add(new_weld_data)
        db.session.commit()

        return redirect(url_for('welds'))
 
    return render_template("welds.html", welds = welds_data, new_weld = new_weld_form) # new_weld is template variable to be used in template

### SPOOLS ####
@app.route('/spools')
def spools():
    con = connection()
    cur = con.cursor()                         
    cur.execute("SELECT * FROM spools;")
    spools_data = cur.fetchall()
    end_con(cur, con)
    return render_template("spools.html", table_data = spools_data)

### HYDROS ###
@app.route('/hydros')
def hydros():
    con = connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM hydros;") 
    hydros_data = cur.fetchall()
    end_con(cur, con)
    return render_template("hydros.html", table_data = hydros_data)


###################################################
### UPDATE WELDS ASYNC API ENPOINT              ###
###################################################
@app.route('/welds/edit', methods=["POST"])
def updateWelds():
    
    request_data = request.get_json()                               # get data from server
    listed_data = request_data.split()                              # split it into a list
    dicted_data = listToEntity(listed_data)                         # convert to a dict
    print(dicted_data)

    weld_to_update = db.session.execute(select(Welds).filter_by(id=dicted_data["id"])).scalar_one()
    weld_to_update.spool_number = dicted_data["spool"]
    weld_to_update.weld_id = dicted_data["weld"]
    weld_to_update.weld_size = dicted_data["size"]
    weld_to_update.weld_schedule = dicted_data["thick"]
    weld_to_update.weld_type = dicted_data["type"]
    weld_to_update.welder = dicted_data["welder"]
    weld_to_update.welded_date = dicted_data["weld_date"]
    weld_to_update.vt = dicted_data["vt"]
    weld_to_update.vt_date = dicted_data["vt_date"]
    weld_to_update.nde_number = dicted_data["nde_number"]
    weld_to_update.nde_date = dicted_data["nde_date"]

    db.session.commit()
    db.session.flush()

    return jsonify("Post request worked!") # give the front end something


# Run development server locally                                              
if __name__ == '__main__':
    app.run(debug=True)