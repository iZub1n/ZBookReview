import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

confirmation=input("Are You Sure you want to add data from the given csv file ENTER Y/y to continue or any ket to abort: ")

if(confirmation.casefold()=="y"):
    with open('books.csv') as file:
        csv_reader = csv.reader(file)
        l = 0;
        for row in csv_reader:
            if l==0:
                l=l+1
            else:
                l=l+1
                print("adding... ",l)
                db.execute("INSERT INTO bookDB (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                 {"isbn": row[0], "title": row[1], "author": row[2], "year": int(row[3])})
        db.commit()