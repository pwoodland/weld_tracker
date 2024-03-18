from flask import Flask                                                                 # import the Flask class from the flask module
from flask import render_template                                                       # import render_template function
from flask import request                                                               # import the request object to be able to get form data
from flask import redirect
from flask import url_for
from flask import jsonify
from flask_wtf import FlaskForm                                                         # import the FlaskForm class to create and use forms
from wtforms import StringField, SubmitField                                            # import some basic form objects
import psycopg2                                                                         # import psycopg2 - how I connect and interact with postgresql
from forms import NewWeldForm                                                           # import NewWeldForm, CommentForm <-- for testing
from datetime import datetime

app = Flask(__name__)                                                                   # create the app Flask object
app.config["SECRET_KEY"] = "not_so_secret"                                              # something I have to do to protect my app


comments = []                                                                           # simple list to hold comments for testing
new_welds = []                                                                          # creating list for storing new weld data

@app.route('/', methods=["GET", "POST"])                                                                         # main route for the home page
def index():
    return render_template("index.html")

@app.route('/welds', methods=["GET", "POST"])                                           # adding the post method to be able to send data back to server
def welds():
    #create an instance of the new weld form
    new_weld_form = NewWeldForm()
    # establish the connection using the connect() function of psycopg2 module
    con = psycopg2.connect(
    database="weld_tracker",    # this is my weld tracker database
    user="postgres",            # this the connection username
    password="postgres",        # this is connection password
    host="localhost",           # this is my defaul host, localhost
    port="5432"                 # PostgreSQL 16 server is set to port 5432
    )

    cursor_obj = con.cursor()                           # creating a cursor object so I can use the functions in the class

    cursor_obj.execute("SELECT * FROM welds ORDER BY id;")          # using the execute function to execute an SQL command
    welds_data = cursor_obj.fetchall()                  # fetching all the records and saving into a variable called result
    # Need to add database connection and data pull to the route so its updated everytime the route gets loaded
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
        
        con = psycopg2.connect(
        database="weld_tracker",    # this is my weld tracker database
        user="postgres",            # this the connection username
        password="postgres",        # this is connection password
        host="localhost",           # this is my defaul host, localhost
        port="5432"                 # PostgreSQL 16 server is set to port 5432
        )
        cursor_obj = con.cursor()  
        cursor_obj.execute("""
                    INSERT INTO welds (spool_number, weld_id, weld_size, weld_schedule, weld_type, welder, date_welded, vt, vt_date, nde_number, nde_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (spool, weld, size, schedule, type, welder, weld_date, vt, vt_date, nde_number, nde_date))
        con.commit()
        cursor_obj.close()              # responsibly closing the cursoer
        con.close()                     # as well as the connection

        
        print(spool, weld, size, schedule, type, welder, weld_date, vt, vt_date, nde_number, nde_date)
        return redirect(url_for('welds'))
    cursor_obj.close()              # responsibly closing the cursoer
    con.close()                     # as well as the connection

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
### CONNECT TO DB
    
     # establish the connection using the connect() function of psycopg2 module
    con = psycopg2.connect(
    database="weld_tracker",    # this is my weld tracker database
    user="postgres",            # this the connection username
    password="postgres",        # this is connection password
    host="localhost",           # this is my defaul host, localhost
    port="5432"                 # PostgreSQL 16 server is set to port 5432
    )

    cursor_obj = con.cursor()                           # creating a cursor object so I can use the functions in the class
    # USE THE CURSOR TO EXECUTE SOME SQL
    cursor_obj.execute("""UPDATE welds
                       SET spool_number = %s, weld_id = %s, weld_size = %s, weld_schedule = %s, weld_type = %s, welder = %s, date_welded = %s, vt = %s,
                       vt_date = %s, nde_number = %s, nde_date = %s
                       WHERE id = %s;
                       """, (dicted_data["spool"], dicted_data["weld"], dicted_data["size"], dicted_data["thick"], dicted_data["type"], dicted_data["welder"], 
                             dicted_data["weld_date"], dicted_data["vt"], dicted_data["vt_date"], dicted_data["nde_number"], dicted_data["nde_date"], dicted_data["id"]))
    con.commit()                    # commit data to DB
    cursor_obj.close()              # responsibly closing the cursoer
    con.close()                     # as well as the connection

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
con = psycopg2.connect(
    database="weld_tracker",    # this is my weld tracker database
    user="postgres",            # this the connection username
    password="postgres",        # this is connection password
    host="localhost",           # this is my defaul host, localhost
    port="5432"                 # PostgreSQL 16 server is set to port 5432
)

cursor_obj = con.cursor()                           # creating a cursor object so I can use the functions in the class

cursor_obj.execute("SELECT * FROM spools;")         # doing the same for spools
spools_data = cursor_obj.fetchall()

cursor_obj.execute("SELECT * FROM hydros;")         # and finally for hydros (currently no data in db)
hydros_data = cursor_obj.fetchall()

cursor_obj.close()              # responsibly closing the cursoer
con.close()                     # as well as the connection



