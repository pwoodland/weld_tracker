from flask import Flask                                                                 # import the Flask class from the flask module
from flask import render_template                                                       # import render_template function
from flask import request                                                               # import the request object to be able to get form data
from flask_wtf import FlaskForm                                                         # import the FlaskForm class to create and use forms
from wtforms import StringField, SubmitField                                            # import some basic form objects
import psycopg2                                                                         # import psycopg2 - how I connect and interact with postgresql
from forms import NewWeldForm, CommentForm                                              # import NewWeldForm, CommentForm <-- for testing

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
    
    # NEED TO WORK ON THIS TO GET INFO INTO THE LIST
    if new_weld_form.validate_on_submit():          
        #new_weld_form.new_weld_spool.data
        #new_weld_form.new_weld_weld.data
        #new_weld_form.new_weld_size.data
        #new_weld_form.new_weld_thick.data
        #new_weld_form.new_weld_type.data
        #new_weld_form.new_weld_welder.data
        #new_weld_form.new_weld_weld_date.data
        #new_weld_form.new_weld_vt.data
        #new_weld_form.new_weld_vt_date.data
        #new_weld_form.new_weld_nde_number.data
        #new_weld_form.new_weld_nde_date.data
    
        # ONLY WORKS OUTSIDE OF IF STATEMENT, same as "tutorial" code but the tutorial one works inside the if statement
        new_spool = new_weld_form.new_weld_spool.data
        new_welds.append(new_spool)
    print(new_welds)
     # forms tutorial related stuff
    welds_comment = CommentForm()                                                       # creating an instance of CommentForm called welds_comment
    if welds_comment.validate_on_submit():                                        
        new_comment = welds_comment.comment.data                                            # storing the input data into a variable
        comments.append(new_comment)                                                        # adding to global comments list 
    print(comments)                                                                     # print comments to see if I am getting inputs
    # forms tutorial related stuff done
    return render_template("welds.html", table_data = welds_data, comment_form = welds_comment, new_weld = new_weld_form) # new_weld is just template variable, not the new_weld list from above if statement


@app.route('/spools')
def spools():
    return render_template("spools.html", table_data = spools_data)

@app.route('/hydros')
def hydros():
    return render_template("hydros.html", table_data = hydros_data)


# establish the connection using the connect() function of psycopg2 module
con = psycopg2.connect(
    database="weld_tracker",    # this is my weld tracker database
    user="postgres",            # this the connection username
    password="postgres",        # this is connection password
    host="localhost",           # this is my defaul host, localhost
    port="5432"                 # PostgreSQL 16 server is set to port 5432
)

cursor_obj = con.cursor()                           # creating a cursor object so I can use the functions in the class

cursor_obj.execute("SELECT * FROM welds;")          # using the execute function to execute an SQL command

welds_data = cursor_obj.fetchall()                  # fetching all the records and saving into a variable called result

cursor_obj.execute("SELECT * FROM spools;")         # doing the same for spools
spools_data = cursor_obj.fetchall()

cursor_obj.execute("SELECT * FROM hydros;")         # and finally for hydros (currently no data in db)
hydros_data = cursor_obj.fetchall()

cursor_obj.close()              # responsibly closing the cursoer
con.close()                     # as well as the connection



