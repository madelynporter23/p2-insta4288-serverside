"""Insta4288 comments view."""

import flask
import insta4288


@insta4288.app.route("/comments/", methods=["POST"])
def update_comments():
    """Create or delete a comment."""
    if "username" not in flask.session:
        flask.abort(403)

    connection = insta4288.model.get_db()
    logname = flask.session["username"]
    operation = flask.request.form["operation"]

    if operation == "create":
        create_comment(connection, logname)
    elif operation == "delete":
        delete_comment(connection, logname)

    target = flask.request.args.get("target")
    if not target:
        target = "/"

    return flask.redirect(target)


def create_comment(connection, logname):
    """Create a comment."""
    postid = flask.request.form["postid"]
    text = flask.request.form["text"]

    if not text:
        flask.abort(400)

    connection.execute(
        "INSERT INTO comments(owner, postid, text) "
        "VALUES (?, ?, ?)",
        (logname, postid, text)
    )


def delete_comment(connection, logname):
    """Delete a comment."""
    commentid = flask.request.form["commentid"]

    cur = connection.execute(
        "SELECT owner FROM comments WHERE commentid = ?",
        (commentid,)
    )
    comment = cur.fetchone()

    if comment is None or comment["owner"] != logname:
        flask.abort(403)

    connection.execute(
        "DELETE FROM comments WHERE commentid = ?",
        (commentid,)
    )
