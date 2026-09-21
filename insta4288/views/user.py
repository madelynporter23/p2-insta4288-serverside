"""Insta4288 user view."""

import flask
import insta4288
from insta4288.views.accounts import get_login_context


@insta4288.app.route('/users/<username>/')
def show_user(username):
    """Display /users/<username>/ route."""
    logname, connection = get_login_context()

    if logname is None:
        return flask.redirect("/accounts/login/")

    cur = connection.execute(
        "SELECT fullname FROM users WHERE username = ?",
        (username,)
    )
    user = cur.fetchone()

    if user is None:
        flask.abort(404)

    cur = connection.execute(
        "SELECT postid, filename "
        "FROM posts WHERE owner = ? "
        "ORDER BY postid DESC",
        (username,)
    )
    posts = cur.fetchall()

    cur = connection.execute(
        "SELECT COUNT(*) AS followers "
        "FROM following WHERE username2 = ?",
        (username,)
    )
    followers = cur.fetchone()["followers"]

    cur = connection.execute(
        "SELECT COUNT(*) AS following "
        "FROM following WHERE username1 = ?",
        (username,)
    )
    following = cur.fetchone()["following"]

    cur = connection.execute(
        "SELECT username1 FROM following "
        "WHERE username1 = ? AND username2 = ?",
        (logname, username)
    )
    logname_follows_username = cur.fetchone() is not None

    context = {
        "logname": logname,
        "username": username,
        "fullname": user["fullname"],
        "posts": posts,
        "total_posts": len(posts),
        "followers": followers,
        "following": following,
        "logname_follows_username": logname_follows_username,
    }
    return flask.render_template("user.html", **context)
