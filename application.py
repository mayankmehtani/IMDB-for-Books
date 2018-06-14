import os
import psycopg2

from flask import Flask, session, render_template, request
from flask import url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from communicator import *

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    """Home Page"""
    return render_template("login.html")

@app.route("/home", methods=["GET","POST"])
def login():
    if request.method == 'POST':
        user_name = request.form['username']
        password = request.form['password']

        if check_login(user_name,password,db):
            return render_template("home.html")
    return "These aren't the droids you're looking for"

@app.route("/search/results", methods=["GET","POST"])
def search():
    """search results"""
    if request.method == 'POST':
        query1 = request.form['Searchbar1']
        query2 = request.form['Searchbar2']
        query3 = request.form['Searchbar3']
        results =  search_books(query1,query2,query3,db)

        list1 = []
        list2 = []
        for result in results:
            list2.append((result['isbn']).encode('utf-8'))
            list2.append((result['author']).encode('utf-8'))
            list2.append((result['title']).encode('utf-8'))
            list1.append(list2)
            list2 =[]

    return render_template('results.html',results=list1)
