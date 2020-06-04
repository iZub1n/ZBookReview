# ZBookReview
Used APIs, SQL, Flask and Python to make a book review website, info was pulled in from goodreads. Users can create accounts to access the website
Importy.py is to import books in csv format to the psql database

application.py is the main file with all the functions and routes

Other: nav bar allows to log out, go to homepage and look at user profile and stats

Templates folder - 
  layout.html - main layout page
  error.html - a page for displaying errors
  success.html - page to show success, maily used for debugging
  welcome.html - a page to create an account or login
  homepage.html - main page after login with a nav bar and search bar
  searchresults.html - shows all the results found in datatabase and provides hyperlinks to seperate book pages
  book.html - url is related to isbn, shows info on book annd user ratings and reviews. Also has the option to add a review
  review.html - redirects from book.html if user wants to add a review. Allows the user to write and rate out of 5
  u.html - a YOU/U page for showing user stats such as account age, last login and books reviewed
  
FUTURE PLANS - allow users to edit their reviews. Allow users to directly go to their reviews from the 'u' page and also allow  users to view each others profiles.
