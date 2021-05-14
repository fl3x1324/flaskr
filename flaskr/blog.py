from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

GET_POSTS = ("SELECT p.id, title, body, created, author_id, username "
             "FROM post p JOIN user u ON p.author_id = u.id "
             "ORDER BY created DESC")
GET_POST = ("SELECT p.id, title, body, created, author_id, username "
            "FROM post p JOIN user u ON p.author_id = u.id "
            "WHERE p.id = ?")
CREATE_POST = ("INSERT INTO post (title, body, author_id) "
               "VALUES(?,?,?)")
UPDATE_POST = ('UPDATE post SET title = ?, body = ? '
               'WHERE id = ?')
DELETE_POST = 'DELETE FROM post WHERE id = ?'


@bp.route("/")
def index():
    db = get_db()
    posts = db.execute(GET_POSTS).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route("/create", methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title, body = get_form_data(request.form)
        err = None

        if not title:
            err = "Title is required."
        if err is not None:
            flash(err)
        else:
            db = get_db()
            db.execute(
                CREATE_POST,
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for("blog.index"))
    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    if request.method == 'POST':
        title, body = get_form_data(request.form)
        err = None
        if not title:
            err = "Title is required."
        if err is not None:
            flash(err)
        else:
            db = get_db()
            db.execute(UPDATE_POST, (title, body, id))
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = get_post(id)
    db = get_db()
    db.execute(DELETE_POST, (id,))
    db.commit()
    return redirect(url_for('blog.index'))


def get_form_data(form):
    return (form['title'], form['body'])


def get_post(id, check_author=True):
    post = get_db().execute(GET_POST, (id,)).fetchone()
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    return post
