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

@app.route('/movies')
def movies_list():
    """Show list of movies"""

    movies = Movie.query.order_by(Movie.title).all()


    return render_template("movie_list.html", movies=movies)

@app.route('/movies/<movie_id>')
def display_movie_details(movie_id):
    """Display info about selected movie."""

    movie = Movie.query.filter(Movie.movie_id==movie_id).one()

    return render_template("movie_info.html", movie=movie)

@app.route('/users/<user_id>')
def display_user_details(user_id):
    """Display information about selected user."""

    user = User.query.filter(User.user_id==user_id).one()
    age = user.age
    zipcode = user.zipcode
    ratings = user.ratings
    

    return render_template('user_info.html', 
                            user=user, 
                            age=age,
                            zipcode=zipcode,
                            ratings=ratings,
                            user_id=user_id)

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

# This is not yet working, unsure why, see AJAX call in movie_info.html
@app.route('/add_rating', methods=['POST'])
def add_rating():
    """Checks if user has previously rated, adds or updates accordingly"""

    rating = request.form.get("rating")
    movie_id = request.form.get("movie")
    user = User.query.filter(User.email==session['user']).one()
    user_id = user.user_id
    new_rating = Rating(movie_id=movie_id, user_id=user_id, score=rating)

    try:
        existing_rating = Rating.query.filter(Rating.user_id==user_id, Rating.movie_id==movie_id).one()
        db.session.delete(existing_rating)
        db.session.add(new_rating)
        db.session.commit()
    except:
        db.session.add(new_rating)
        db.session.commit()

    return "True"




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

    user_id = (User.query.filter(User.email == email).one()).user_id


    return redirect('/users/'+str(user_id))

@app.route('/logout')
def logout():
    """User is logged out of session"""

    session['user'] = ''

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
