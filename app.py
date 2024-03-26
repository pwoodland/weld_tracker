####################################################
### V0.08 MASS CSV ENTRY FOR WELDS AND SPOOLS    ###
### NEXT UP: NOT SURE YET, MABYE SOME STYLING?   ###
####################################################

from flask import Flask, render_template, request, redirect, url_for, jsonify           # import the Flask class from the flask module
import psycopg2                                                                         # import psycopg2 - how I connect and interact with postgresql
from forms import NewWeldForm, NewSpoolForm, MassWeldForm, MassSpoolForm                               
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
# remove once hydros is updated to SQLAlchemy
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
###     data processing functions          ### 
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
    
def listToWeld(listOfStrings):
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

def listToSpool(listOfStrings):
    entity = {
    "id": int(listOfStrings[0]),
    "line": listOfStrings[1].upper(),
    "drawing": listOfStrings[2].upper(),
    "revision": (listOfStrings[3]),
    "spec": listOfStrings[4].upper(),
    "spool": listOfStrings[5].upper(),
    "dwg_date": checkIfNoneDate(listOfStrings[6]),
    "weld_date": checkIfNoneDate(listOfStrings[7]),
    "nde_date": checkIfNoneDate(listOfStrings[8]),
    "pwht_date": checkIfNoneDate(listOfStrings[9]),
    "hydro_date": checkIfNoneDate(listOfStrings[10])
    }
    return entity

### turning csv mass entry form into list of CSV welds
def csvToListOfCSV(csv):
    csv_split = csv.split("\r")
    csv_list = []
    for string in csv_split:
        csv_list.append(string.strip("\n"))
    return csv_list

### separate list of CSVs
def splitCSVLists(csv_list):
    list_of_lists = []
    for list in csv_list:
        list_of_lists.append(list.split(","))
    return list_of_lists

### turn the lists into welds
def listsToWeldObjs(lists):
    entities = []
    for list in lists:
        entities.append({
            "spool": list[0].upper(),
            "weld": list[1].upper(),
            "size": int(list[2]),
            "thick": list[3].upper(),
            "type": list[4].upper()
        })
    
    return entities

def listsToSpoolObjs(lists):
    entities = []
    for list in lists:
        entities.append({
            "line": list[0].upper(),
            "drawing": list[1].upper(),
            "rev": list[2].upper(),
            "spec": list[3].upper(),
            "spool": list[4].upper()
        })
    return entities


### mass welds into database
def commitMassWelds(welds):
    for weld in welds:
        weld_data = Welds(spool_number=weld["spool"], weld_id=weld["weld"], weld_size=weld["size"],
                          weld_schedule=weld["thick"], weld_type=weld["type"])
        db.session.add(weld_data)
        db.session.commit()
    pass

### mass spools into database
def commitMassSpools(spools):
    for spool in spools:
        spool_data = Spools(line_number=spool["line"], drawing_number=spool["drawing"], revision_number=spool["rev"],
                            line_spec=spool["spec"], spool_number=spool["spool"])
        db.session.add(spool_data)
        db.session.commit()
    pass


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
    mass_welds_form = MassWeldForm()
    ### gets all the records using Flask-SQLAlchemy
    welds_data = db.session.execute(db.select(Welds).order_by(Welds.spool_number, Welds.weld_id)).scalars().all()

    # mass weld form submission
    if mass_welds_form.validate_on_submit():
        csv_data = mass_welds_form.welds_text_area.data
        mass_welds = listsToWeldObjs(splitCSVLists(csvToListOfCSV(csv_data)))
        commitMassWelds(mass_welds)

        return redirect(url_for('welds'))

    # new weld form submission
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
 
    return render_template("welds.html", welds = welds_data, new_weld = new_weld_form, csv_welds = mass_welds_form) # new_weld is template variable to be used in template

### SPOOLS ####
@app.route('/spools', methods=["GET", "POST"])
def spools():
    new_spool_form = NewSpoolForm()
    mass_spools_form = MassSpoolForm()
    spools_data = db.session.execute(db.select(Spools).order_by(Spools.spool_number)).scalars().all()

    # mass spools form submission
    if mass_spools_form.validate_on_submit():
        csv_data = mass_spools_form.spools_text_area.data
        mass_spools = listsToSpoolObjs(splitCSVLists(csvToListOfCSV(csv_data)))
        commitMassSpools(mass_spools)

        return redirect(url_for('spools'))

    # new spool form submission
    if new_spool_form.validate_on_submit():
        line_number = new_spool_form.new_spool_line_number.data.upper()
        dwg_number = new_spool_form.new_spool_dwg_number.data.upper()
        rev_number = new_spool_form.new_spool_rev_number.data.upper()
        line_spec = new_spool_form.new_spool_line_spec.data.upper()
        spool = new_spool_form.new_spool_spool.data.upper()
        if new_spool_form.new_spool_dwg_date.data == "":
            dwg_date = None
        else:
            dwg_date = new_spool_form.new_spool_dwg_date.data
        if new_spool_form.new_spool_welded_date.data == "":
            welded_date = None
        else:
            welded_date = new_spool_form.new_spool_welded_date.data
        if new_spool_form.new_spool_nde_date.data == "":
            nde_date = None
        else:
            nde_date = new_spool_form.new_spool_nde_date.data
        if new_spool_form.new_spool_pwht_date.data == "":
            pwht_date = None
        else:
            pwht_date = new_spool_form.new_spool_pwht_date.data
        if new_spool_form.new_spool_hydro_date.data == "":
            hydro_date = None
        else:
            hydro_date = new_spool_form.new_spool_hydro_date.data

        new_spool_data = Spools(line_number=line_number, drawing_number=dwg_number, revision_number=rev_number, line_spec=line_spec, spool_number=spool,
                                dwg_issued_date=dwg_date, welded_date=welded_date, nde_date=nde_date, pwht_date=pwht_date, hydro_date=hydro_date)

        db.session.add(new_spool_data)
        db.session.commit()

        return redirect(url_for('spools'))

    return render_template("spools.html", spools = spools_data, new_spool = new_spool_form, csv_spools=mass_spools_form)

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
###     UPDATE WELDS ASYNC API ENDPOINT         ###
###################################################
@app.route('/welds/edit', methods=["POST"])
def updateWelds():
    
    request_data = request.get_json()                               # get data from server
    listed_data = request_data.split()                              # split it into a list
    dicted_data = listToWeld(listed_data)                           # convert to a dict
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

#####################
### UPDATE SPOOLS ###
#####################
@app.route('/spools/edit', methods=["POST"])
def updateSpools():

    request_data = request.get_json()                               # get data from server
    listed_data = request_data.split()                              # split it into a list
    dicted_data = listToSpool(listed_data)                          # convert to a dict
    print(dicted_data)

    spool_to_update = db.session.execute(select(Spools).filter_by(id=dicted_data["id"])).scalar_one()
    spool_to_update.line_number = dicted_data["line"]
    spool_to_update.drawing_number = dicted_data["drawing"]
    spool_to_update.revision_number = dicted_data["revision"]
    spool_to_update.line_spec = dicted_data["spec"]
    spool_to_update.spool_number = dicted_data["spool"]
    spool_to_update.dwg_issued_date = dicted_data["dwg_date"]
    spool_to_update.welded_date = dicted_data["weld_date"]
    spool_to_update.nde_date = dicted_data["nde_date"]
    spool_to_update.pwht_date = dicted_data["pwht_date"]
    spool_to_update.hydro_date = dicted_data["hydro_date"]

    db.session.commit()
    db.session.flush()

    return jsonify("Post request worked!")


###############################################
###        DELETE WELDS API ENDPOINT        ###
###############################################
@app.route('/welds/delete', methods=["DELETE"])
def deleteWeld():
    request_data = request.get_json()                               # get data from server
    listed_data = request_data.split()                              # split it into a list
    dicted_data = listToWeld(listed_data)                           # convert to a dict
    print(dicted_data)

    weld_to_delete = db.session.execute(select(Welds).filter_by(id=dicted_data["id"])).scalar_one()
    db.session.delete(weld_to_delete)
    db.session.commit()
    db.session.flush()

    return jsonify(f"Successfully deleted weld {dicted_data["weld"]} from spool {dicted_data["spool"]}!")


###############################################
###        DELETE SPOOL API ENDPOINT        ###
###############################################
@app.route('/spools/delete', methods=["DELETE"])
def deleteSpool():
    request_data = request.get_json()                               # get data from server
    listed_data = request_data.split()                              # split it into a list
    dicted_data = listToSpool(listed_data)                          # convert to a dict
    print(dicted_data)

    spool_to_delete = db.session.execute(select(Spools).filter_by(id=dicted_data["id"])).scalar_one()
    db.session.delete(spool_to_delete)
    db.session.commit()
    db.session.flush()
    
    return jsonify(f"Successfully deleted spool {dicted_data["spool"]}!")

# Run development server locally                                              
if __name__ == '__main__':
    app.run(debug=True)