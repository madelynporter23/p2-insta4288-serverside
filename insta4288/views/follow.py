"""Insta4288 following POST view."""
import flask
import insta4288


@insta4288.app.route("/following/", methods=["POST"])
def update_following():
    """Follow or unfollow a user."""
    if "username" not in flask.session:
        flask.abort(403)

    logname = flask.session["username"]
    operation = flask.request.form["operation"]
    username = flask.request.form["username"]
    connection = insta4288.model.get_db()

    cur = connection.execute(
        "SELECT username1 FROM following "
        "WHERE username1 = ? AND username2 = ?",
        (logname, username)
    )
    following = cur.fetchone()

    if operation == "follow":
        if following is not None:
            flask.abort(409)

        connection.execute(
            "INSERT INTO following(username1, username2) "
            "VALUES (?, ?)",
            (logname, username)
        )

    elif operation == "unfollow":
        if following is None:
            flask.abort(409)

        connection.execute(
            "DELETE FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (logname, username)
        )

    target = flask.request.args.get("target")
    if not target:
        target = "/"

    return flask.redirect(target)
