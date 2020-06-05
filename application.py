import os
import requests

from flask import Flask, render_template, redirect, request, flash, session, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime

app = Flask(__name__)
app.secret_key = "hello"

#gReadsAPI = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "2V41nUoJ1R4abmzct4A", "isbns": "9781632168146"})

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
    if "user" in session:
        return redirect(url_for("login"))
    return render_template("welcome.html")

@app.route("/homepage", methods=["POST","GET"])
def login():
    if "user" not in session:
        if request.method=="POST":
            if request.form['action']=='Lgn':
                username = request.form.get("uname")
                password = request.form.get("pswd")
                
                u = db.execute("SELECT * FROM account WHERE username = :usernameNew" , {"usernameNew": usernameNew}).fetchone()
                
                if (username or password) is None:
                    return render_template("error.html", message="Login or Password is empty")

                if u is None or (u.password)!=password:
                    return render_template("error.html", message="Username or Password is incorrect")

                timeStamp = (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                db.execute("UPDATE account SET last_login = :updateLoginTime WHERE username= :username", {"username": username, "updateLoginTime": timeStamp})
                db.commit()
                session["user"] = username

            if request.form['action']=='CreateAcc':
                username = request.form.get("uname")
                usernameNew = request.form.get("unameNew")
                passwordNew = request.form.get("pswdNew")
                passwordNewRe = request.form.get("pswdNewRe")

                if (usernameNew.isspace() or passwordNew.isspace() or passwordNewRe.isspace()):
                    return render_template("error.html", message="One of the fields is empty")

                usernameFind = db.execute("SELECT * FROM account WHERE username = :usernameNew" , {"usernameNew": usernameNew}).fetchone()
                if usernameFind is not None:
                    return render_template("error.html", message="Username Already Exists")

                if passwordNew!=passwordNewRe:
                    return render_template("error.html", message="Passwords don't match")

                if ' ' in passwordNew or ' ' in usernameNew:
                    return render_template("error.html",message="Space in one of the Parameters")

                timeStamp = (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                db.execute("INSERT INTO account (username, password, created_on, last_login) VALUES  (:usernameNew, :passwordNew, :timeStampSQL, :timeStampSQL)",
                    {"usernameNew": usernameNew, "passwordNew": passwordNew, "timeStampSQL": timeStamp, "timeStampSQL": timeStamp})
                db.commit()
                session["user"] = usernameNew
            return render_template("homepage.html")
        else:
            return redirect("/")
    else:
        return render_template("homepage.html")

@app.route("/logout", methods=["POST","GET"])
def logout():
    session.pop("user", None)
    return redirect("/")


@app.route("/u", methods=["POST","GET"])
def u():
    if "user" not in session:
        return redirect("/")
    
    user =  db.execute("SELECT * FROM account WHERE username = :username" , {"username": session["user"]}).fetchone()
    return render_template("u.html",user=user)

@app.route("/search", methods=["POST","GET"])
def searchResults():
    if "user" not in session:
        return redirect("/")
    search_query = request.form.get("searchQuery")
    if search_query is None:
        return redirect("/")
    search_query = search_query.strip()
    if search_query == "":
        return render_template("error.html", message="You must provide a book.")

    search_query = "%"+search_query.lower()+"%"

    # \ is for continue to next line
    rows = db.execute("SELECT * FROM bookDB WHERE LOWER(isbn) LIKE :query OR \
                        LOWER(title) LIKE :query OR \
                        LOWER(author) LIKE :query OR \
                        LOWER(year) LIKE :query LIMIT 100",
                        {"query": search_query})

    if rows.rowcount == 0:
        return render_template("error.html", message=search_query)

    space=""
    if rows.rowcount>100:
        space = "Some Results Not Included due to Space Constraints, Be More Specific if Desired Result was not found"

    results = rows.fetchall()
    return render_template("searchresults.html", results=results, space=space)

@app.route("/search/<book_isbn>", methods=['GET'])
def book(book_isbn):
    if "user" not in session:
        return redirect("/")
    book = db.execute("SELECT * FROM bookDB WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
    if book is None:
        return render_template("error.html", message="Book wasn't found.")

    gReadsAPI = gReads(book_isbn)

    reviews = db.execute("SELECT * FROM reviews WHERE r_isbn = :isbn",
                            {"isbn": book_isbn}).fetchall()

    return render_template("book.html", book=book, gReadsAPI=gReadsAPI, reviews=reviews)


@app.route("/search/<book_isbn>/addReview", methods=['POST'])
def addReview(book_isbn):
    if "user" not in session:
        return redirect("/")
    book = db.execute("SELECT * FROM bookDB WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
    if book is None:
         return render_template("error.html", message="Error While adding review.")

    return render_template("review.html", book=book)


@app.route("/search/<book_isbn>/addreview/", methods=['POST'])
def addedReview(book_isbn):
    if "user" not in session:
        return redirect("/")

    text= request.form.get("reviewBox")
    rating= request.form.get("rad")
    if text is None or text.isspace():
        return render_template("error.html", message="No written review.")

    alreadyReviewed = db.execute("SELECT * FROM reviews WHERE  r_isbn= :isbn AND r_username= :username",
                        {"isbn": book_isbn, "username": session["user"]}).fetchone()
    if alreadyReviewed is not None:
        return render_template("error.html", message="You have already reviewed this book")

    db.execute("INSERT INTO reviews (r_isbn, r_username, review, rating) VALUES (:r_isbn, :r_username, :review, :rating)",
                             {"r_isbn": book_isbn, "r_username": session["user"], "review": text, "rating": int(rating)})
    
    userInfo =  db.execute("SELECT * FROM account WHERE username= :username", {"username": session["user"]}).fetchone()
    db.execute("UPDATE account SET booksreviewed = :brc WHERE username= :username", {"username": session["user"], "brc": userInfo.booksreviewed+1})
    db.commit()
    
    urlHome="/search/"+book_isbn
    return redirect(urlHome)

@app.route("/api/<book_isbn>", methods=['GET'])
def api_call(book_isbn):
    if "user" not in session:
        return render_template("error.html",message="Sign-In required to access API")
    
    book = db.execute("SELECT * FROM bookDB WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
    if book is None:
        return jsonify({"Error": "Book Not in Database"}), 404
    
    reviewsCount = db.execute("SELECT * FROM reviews WHERE r_isbn = :isbn", {"isbn": book_isbn})
    gReadsAPI = gReads(book_isbn)
    result = {"title": book.title, "author": book.author, "year": book.year, "isbn": book.isbn, "review_count": gReadsAPI['books'][0]['ratings_count'] ,"average_score": gReadsAPI['books'][0]['average_rating'] }
    return jsonify(result)


def gReads(book_isbn):
    gReadsvar = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "2V41nUoJ1R4abmzct4A", "isbns": book_isbn})
    return gReadsvar.json()

if __name__ == "__main__":
    app.run