import os
import psycopg2

from flask import Flask, session, render_template, request
from flask import url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

def check_login(user_name,password1,database):
    """checks a users' login credentials"""
    results = database.execute("SELECT * FROM users WHERE username = :username", {"username": user_name})

    # returns True if such a user exists with these credentials
    for entry in results:
        return (entry[0] == user_name and entry[1] == password1)
    return False

def search_books(isbn_query,author_query,title_query,database):
    """searches through our books database"""
    isbn_query = '%{0}%'.format(isbn_query)
    author_query ='%{0}%'.format(author_query)
    title_query = '%{0}%'.format(title_query)

    # something not possible if the user did not enter an isbn value
    if isbn_query == "%%":
        isbn_query = '9999999999999999999'

    # something not possible if the user did not enter an author
    if author_query == "%%":
        author_query = 'With a foreward by 999941234rr'

    # something definitely not possible if the user did not enter a title to search for
    if title_query == '%%':
        author_query = "The Curious Case of Donald Trump"

    results = database.execute("Select * from books where (isbn like :isbn) or (author like :author) \
    or (title like :title)",{"isbn":isbn_query,"author":author_query,"title":title_query})
    return results

def get_book_info(isbn,database):
    """returns information on a book (e.g. Author, Title, ISBN, DATE)"""
    isbn_query = '%{0}%'.format(isbn)
    results = database.execute("SELECT * FROM books WHERE (isbn like :isbn)",{"isbn":isbn_query})
    return results

def get_reviews(isbn,database):
    """returns all reviews"""
    isbn_query = '%{0}%'.format(isbn)
    results = database.execute("SELECT * FROM reviews WHERE (book_isbn like :book_isbn)",{"book_isbn":isbn_query})
    return results
