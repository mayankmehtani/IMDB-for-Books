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
    results = database.execute("Select * from books where (isbn like :isbn) or (author like :author) \
    or (title like :title)",{"isbn":isbn_query,"author":author_query,"title":title_query})

    return results
