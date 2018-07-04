import os
import psycopg2
from flask import Flask, session, render_template, request, redirect
from flask import jsonify
from flask import url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from communicator import *
import requests

app = Flask(__name__)
api_key = 'JwDBt0sa68ErzbiliE9w'

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
    session.clear() # clears the session cookie from a previous user login
    return render_template("login.html")

@app.route("/home")
def home():
    """ Open Homepage or back to Login """
    #if a user is logged in, then take to home screen
    # else go back to the login screen
    if bool(session):
        return render_template("home.html")
    else:
        return redirect(url_for("index"))

@app.route("/login", methods=["GET","POST"])
def login():
    """Log In Method"""
    if request.method == 'POST':
        user_name = request.form['username']
        password = request.form['password']

        print (session)
        if check_login(user_name,password,db):
            session['username'] = user_name
            return redirect(url_for('home'))
        else:
            return "These aren't the droids you're looking for"
    # return to home page if user already logged in
    else:
        return redirect(url_for('home'))

@app.route("/registration", methods=["POST","GET"])
def registration():
    """Signs Up"""
    user_name = request.form['username']
    password = request.form['password']

    if register(user_name,password,db):
        return redirect(url_for('home'))
    else:
        return "You did not enter a username/password or this user already exists!"

@app.route("/newuser", methods=["GET","POST"])
def newuser():
    """Opens New User Page"""
    return render_template("newuser.html")

@app.route("/api/<int:isbn>", methods=["GET"])
def book_api(isbn):
    """return a json object with book information"""
    book_information = get_book_info(isbn,db)

    book_data = {}
    for info in book_information:
        isbn_ = (info['isbn']).encode('utf-8')
        book_data['isbn'] = isbn_
        book_data['author'] = (info['author']).encode('utf-8')
        book_data['title'] = (info['title']).encode('utf-8')
        book_data['year'] = (info['year']).encode('utf-8')

        res = requests.get("https://www.goodreads.com/book/review_counts.json", \
        params={"key": api_key, "isbns": isbn_})
        goodreads_book_info=res.json()
        book_data['average_rating'] = goodreads_book_info['books'][0]['average_rating']
        book_data['total_reviews'] = goodreads_book_info['books'][0]['reviews_count']

    return jsonify(book_data)

@app.route("/books/<int:isbn>", methods=["GET","POST"])
def book_page(isbn):
    """opens book page"""
    book_information = get_book_info(isbn,db) # pulls from PostgreSQL Database

    book_data = {} # This will pass a dictionary object to Book.hmtl
    for info in book_information:
        isbn_ = (info['isbn']).encode('utf-8')
        if not (isbn_).isdigit():
            book_data['isbn'] = '00000'
        else:
            book_data['isbn'] = isbn_
        book_data['author'] = (info['author']).encode('utf-8')
        book_data['title'] = (info['title']).encode('utf-8')
        book_data['year'] = (info['year']).encode('utf-8')

        # information which we called from the GoodReads API
        res = requests.get("https://www.goodreads.com/book/review_counts.json", \
        params={"key": api_key, "isbns": isbn_})
        goodreads_book_info=res.json()
        book_data['average_rating'] = goodreads_book_info['books'][0]['average_rating']
        book_data['total_reviews'] = goodreads_book_info['books'][0]['reviews_count']

    review_list = []
    review_information = get_reviews(isbn,db)
    for info in review_information:
        review_list.append([(info['username']).encode('utf-8'), \
        (info['review']).encode('utf-8')])

    return render_template("book.html",isbn=int(book_data['isbn']),\
    author=book_data['author'],title=book_data['title'], year=book_data['year'],\
    average_rating=book_data['average_rating'],\
    total_reviews=book_data['total_reviews'],reviews = review_list)

@app.route("/submit_review/<int:isbn>", methods=["GET","POST"])
def submit_review(isbn):
    """Submits a review to "reviews," our PostgreSQL Database"""
    review = request.form['text']

    if len(review) < 25:
        return "Please only submit reviews that are at least 140 characters"
    elif new_review(isbn,review,session['username'],db):
        return redirect(url_for('book_page',isbn=isbn))
    else:
        return "You have already submitted a review for this book"


@app.route("/results", methods=["POST"])
def search():
    """Search Results"""
    if request.method == 'POST':
        query1 = request.form['Searchbar1']
        query2 = request.form['Searchbar2']
        query3 = request.form['Searchbar3']
        results =  search_books(query1,query2,query3,db) # calls from communicator class

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
            list2.append('Author: ' + str((result['author']).encode('utf-8')))
            list2.append('Title: '+ str((result['title']).encode('utf-8')))
            list1.append(list2)
            list2 = []

    return render_template('results.html',results=list1)

@app.route("/logout", methods = ["POST"])
def logout():
    session.clear()
    return render_template("home.html")
