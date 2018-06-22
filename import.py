import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL")) #connect to SQL server
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)

    header = True
    for isbn,title,author,year in reader:
        if not header:
            db.execute("INSERT INTO books (isbn,title,author,year) VALUES (:isbn,:title,:author,:year)",{"isbn":isbn,"title":title,"author":author,"year":year} )
        header = False
    db.commit()

if __name__ == "__main__":
    main()
