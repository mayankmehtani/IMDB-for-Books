import os
import psycopg2
from flask import Flask, session, render_template, request, redirect
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
    """Login Page"""
    return render_template("login.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET","POST"])
def login():
    """Log In Method"""
    if request.method == 'POST':
        user_name = request.form['username']
        password = request.form['password']

        if check_login(user_name,password,db):
            return redirect(url_for('home'))
        else:
            return "These aren't the droids you're looking for"

@app.route("/registration", methods=["GET","POST"])
def registration():
    """Signs Up"""
    if request.method == 'POST':
        user_name = request.form['username']
        password = request.form['password']

        if register(user_name,password,db):
            return redirect(url_for('home'))
        else:
            return "You did not enter a username/password or this user already exists!"

    return "This was done by getting"

@app.route("/newuser", methods=["GET","POST"])
def newuser():
    """Opens New User Page"""
    return render_template("newuser.html")

@app.route("/books/<int:isbn>", methods=["GET","POST"])
def book_page(isbn):
    """opens book page"""
    book_information = get_book_info(isbn,db)

    book_data = {}
    for info in book_information:
        isbn_ = (info['isbn']).encode('utf-8')
        if not (isbn_).isdigit():
            book_data['isbn'] = '00000'
        else:
            book_data['isbn'] = isbn_
        book_data['author'] = (info['author']).encode('utf-8')
        book_data['title'] = (info['title']).encode('utf-8')

    review_list = []
    review_information = get_reviews(isbn,db)
    for info in review_information:
        review_list.append([(info['username']).encode('utf-8'), \
        (info['review']).encode('utf-8')])

    return render_template("book.html",isbn=int(book_data['isbn']),\
    author=book_data['author'],title=book_data['title'], reviews = review_list)

@app.route("/results", methods=["GET","POST"])
def search():
    """Search Results"""
    if request.method == 'POST':
        query1 = request.form['Searchbar1']
        query2 = request.form['Searchbar2']
        query3 = request.form['Searchbar3']
        results =  search_books(query1,query2,query3,db) # calls from communicator class
        print (results)

        isbn_list = []
        authors = []
        titles = []

        list1 = []
        list2 = []
        for result in results:
            isbn_result = str((result['isbn']).encode('utf-8'))

            if not isbn_result.isdigit():
                isbn_result = isbn_result[0:len(isbn_result)-1]

            list2.append( int(isbn_result) )
            list2.append((result['author']).encode('utf-8'))
            list2.append((result['title']).encode('utf-8'))
            list1.append(list2)
            list2 = []

    return render_template('results.html',results=list1)
