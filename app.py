"""Blogly application."""

from flask import Flask, request, render_template,  redirect, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, Users

app = Flask(__name__)

app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = "secret_key596@viki.com"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all() 

@app.route('/')
def redirect_route():
    """Redirects to the users list."""

    return redirect('/users')


@app.route('/users')
def users_list():
    """Show list of all users."""
    
    users = Users.query.all()
    return render_template('list.html', users=users)


@app.route('/users/new')
def users_new():
    """Shows a form to create a new user."""

    return render_template('add_user.html')


@app.route('/users/new', methods=['POST'])
def add_user():
    """Adds a new user to the list of users."""
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    url = request.form['url'] or None


    if not first_name or not last_name:
       flash('All fields are required.', 'error')
       return redirect('/users/new')

    user = Users(first_name=first_name, last_name=last_name, image_url=url)
    db.session.add(user)
    db.session.commit()
    flash('User added successfully.', 'success')
    return redirect('/users')


@app.route('/users/<int:user_id>')
def profile(user_id):
    
    user = Users.query.get_or_404(user_id)

    return render_template('info.html', user=user)


@app.route('/users/<int:user_id>/edit')
def edit(user_id):
    
    user = Users.query.get_or_404(user_id)

    return render_template('edit.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=['POST'])
def edit_user(user_id):
    """Adds a new user to the list of users."""

    user = Users.query.get_or_404(user_id)
    
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['url'] or None

    if not user.first_name or not user.last_name:
        flash('All fields are required.', 'error')
        return redirect(f'/users/{user_id}/edit')
    
    db.session.commit()
    flash('User updated successfully.', 'success')
    return redirect('/users')



@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_profile(user_id):
    user = Users.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect('/users')


