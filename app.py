"""Blogly application."""

from flask import Flask, request, render_template, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, Users, Post, Tag, PostTag

app = Flask(__name__)

app.app_context().push()

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///blogly"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

app.config["SECRET_KEY"] = "secret_key596@viki.com"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


@app.route("/")
def redirect_route():
    """Redirects to the users list."""

    return redirect("/users")


@app.route("/users")
def users_list():
    """Show list of all users."""

    users = Users.query.all()
    return render_template("list.html", users=users)


@app.route("/users/new")
def users_new():
    """Shows a form to create a new user."""

    return render_template("add_user.html")


@app.route("/users/new", methods=["POST"])
def add_user():
    """Adds a new user to the list of users."""
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    url = request.form["url"] or None

    if not first_name or not last_name:
        flash("All fields are required.", "error")
        return redirect("/users/new")

    user = Users(first_name=first_name, last_name=last_name, image_url=url)
    db.session.add(user)
    db.session.commit()
    flash("User added successfully.", "success")
    return redirect("/users")


@app.route("/users/<int:user_id>")
def profile(user_id):
    user = Users.query.get_or_404(user_id)

    return render_template("info.html", user=user)


@app.route("/users/<int:user_id>/edit")
def edit(user_id):
    user = Users.query.get_or_404(user_id)

    return render_template("edit.html", user=user)


@app.route("/users/<int:user_id>/edit", methods=["POST"])
def edit_user(user_id):
    """Adds a new user to the list of users."""

    user = Users.query.get_or_404(user_id)

    user.first_name = request.form["first_name"]
    user.last_name = request.form["last_name"]
    user.image_url = request.form["url"] or None

    if not user.first_name or not user.last_name:
        flash("All fields are required.", "error")
        return redirect(f"/users/{user_id}/edit")

    db.session.commit()
    flash("User updated successfully.", "success")
    return redirect("/users")


@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_profile(user_id):
    user = Users.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect("/users")


################################################################


@app.route("/users/<int:user_id>/posts/new")
def new_post(user_id):
    """Renders a form to add a post for that user."""

    user = Users.query.get_or_404(user_id)
    post = Post.query.all()
    tag = Tag.query.all()
    return render_template("new_post.html", user=user, tags = tag, post = post)


@app.route("/users/<int:user_id>/posts/new", methods=["POST"])
def create_post(user_id):
    """Renders a form to add a post for that user."""

    user = Users.query.get_or_404(user_id)
    tag_ids = [int(num) for num in request.form.getlist("tag")]
    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    new_post = Post(
        title=request.form["title"], content=request.form["content"], user=user, tags = tags
    )
    db.session.add(new_post)
    db.session.commit()

    flash("Post created successfully.", "success")

    return redirect(f"/users/{user_id}")


@app.route("/posts/<int:post_id>")
def show_post(post_id):
    post = Post.query.get_or_404(post_id)

    return render_template("post.html", post=post)


@app.route("/posts/<int:post_id>/edit")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    tag = Tag.query.all()
    return render_template("edit_post.html", post=post, tags = tag)


@app.route("/posts/<int:post_id>/edit", methods=["POST"])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    post.title = request.form["title"]
    post.content = request.form["content"]

    tag_ids = [int(num) for num in request.form.getlist("tag")]
    post.tag = Tag.query.filter(Tag.id.in_(tag_ids)).all() 
    
    db.session.add(post)
    db.session.commit()
    flash("Post updated successfully.", "success")
    return redirect(f"/posts/{post_id}")


@app.route("/posts/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()

    return redirect(f"/users/{post.user_id}")


#######################################################################

@app.route('/tags')
def get_tags():
    """Returns a list of tags."""

    tags = Tag.query.all()
    return render_template("tags.html", tags=tags)


@app.route('/tags/new')
def new_tags():
    tag = Tag.query.all()
    post = Post.query.all()
    return render_template("new_tag.html", tag=tag, post = post)

@app.route('/tags/new' , methods=['POST'])
def create_tags():
    name = request.form['tag']
    post_ids = [int(num) for num in request.form.getlist("post")]
    posts = Post.query.filter(Post.id.in_(post_ids)).all()
    new_tag = Tag(name = name, posts = posts)
    db.session.add(new_tag)
    db.session.commit()
    flash("Successfully created tag", "success")
    return redirect("/tags")



@app.route("/tags/<int:tag_id>")
def show_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    return render_template("show_tag.html", tag=tag)


@app.route("/tags/<int:tag_id>/edit")
def get_edit_page(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    post = Post.query.all()
    return render_template("edit_tag.html", tag=tag, post=post)



@app.route("/tags/<int:tag_id>/edit", methods=['POST'])
def edit_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)

    tag.name = request.form['tag']
    post_ids = [int(num) for num in request.form.getlist("post")]
    tag.post = Post.query.filter(Post.id.in_(post_ids)).all()

    db.session.commit()
    flash("Tag updated successfully", "success")

    return redirect("/tags")


@app.route("/tags/<int:tag_id>/delete", methods=['POST'])
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()

    return redirect('/tags')