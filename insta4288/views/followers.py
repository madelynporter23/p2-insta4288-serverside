"""Insta4288 followers view."""

import flask
import insta4288


@insta4288.app.route('/users/<username>/followers/')
def show_followers(username):
    """Display /users/<username>/followers/ route."""
    if "username" not in flask.session:
        return flask.redirect("/accounts/login/")

    logname = flask.session["username"]
    connection = insta4288.model.get_db()

    cur = connection.execute(
        "SELECT COUNT(*) AS count "
        "FROM users WHERE username = ?",
        (username,)
    )
    if cur.fetchone()["count"] == 0:
        flask.abort(404)

    cur = connection.execute(
        "SELECT users.username, users.filename "
        "FROM following "
        "JOIN users ON following.username1 = users.username "
        "WHERE following.username2 = ?",
        (username,)
    )
    followers = cur.fetchall()

    for follower in followers:
        cur = connection.execute(
            "SELECT username1 FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (logname, follower["username"])
        )
        follower["logname_follows_username"] = (
            cur.fetchone() is not None
        )

    context = {
        "logname": logname,
        "username": username,
        "followers": followers,
    }
    return flask.render_template("followers.html", **context)
