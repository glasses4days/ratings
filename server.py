"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()

    return render_template("user_list.html", users=users)

@app.route('/sign_up', methods=["POST"])
def sign_up():
    """Check if user exists in users table."""

    email = request.form.get("email")

    try: 
        User.query.filter(User.email == email).one()
        return render_template("login.html", email=email)
    except:
        #add email to our database and render sign_up.html

        return render_template('sign_up.html', email=email)

@app.route('/add_new_user', methods=["POST"])
def add_new_user():
    """Unpack user input and add to users table"""

    email = request.form.get("email")
    password = request.form.get("password")
    age = request.form.get("age")
    zipcode = request.form.get("zipcode")

    user = User(email=email, password=password,
                age=age, zipcode=zipcode)


    db.session.add(user)
    db.session.commit()

    return redirect('/users')

@app.route('/check_password', methods=['POST'])
def check_password():
    """Check if user-entered password is correct"""

    password = request.form.get('password')
    email = request.form.get('email')

    try:
        User.query.filter(User.password == password, User.email == email).one()
        return "True"
    except:
        return "False"

@app.route('/login_session', methods=["POST"])
def login_session():
    """Log in user, flash successful login message and redirect to home."""

    email = request.form.get('email')
    password = request.form.get('password')
    session['user'] = email
    flash('Successfully logged in as ' + session['user'])


    return redirect('/')

@app.route('/logout')
def logout():
    """User is logged out of session"""

    session.clear()

    flash('Logged out punk')

    return redirect('/')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
