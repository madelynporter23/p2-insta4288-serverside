"""Insta4288 following view."""

import flask
import insta4288


@insta4288.app.route('/users/<username>/following/')
def show_following(username):
    """Display /users/<username>/following/ route."""
    if "username" not in flask.session:
        return flask.redirect("/accounts/login/")

    connection = insta4288.model.get_db()
    logname = flask.session["username"]

    cur = connection.execute(
        "SELECT username FROM users WHERE username = ?",
        (username,)
    )
    if cur.fetchone() is None:
        flask.abort(404)

    cur = connection.execute(
        "SELECT users.username, users.filename "
        "FROM following "
        "JOIN users ON following.username2 = users.username "
        "WHERE following.username1 = ?",
        (username,)
    )
    following = cur.fetchall()

    for followed_user in following:
        cur = connection.execute(
            "SELECT username1 FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (logname, followed_user["username"])
        )
        followed_user["logname_follows_username"] = (
            cur.fetchone() is not None
        )

    context = {
        "logname": logname,
        "username": username,
        "following": following,
    }
    return flask.render_template("following.html", **context)
