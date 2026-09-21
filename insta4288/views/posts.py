"""Insta4288 posts view."""

import flask
import insta4288
from insta4288.views.accounts import save_upload


@insta4288.app.route("/posts/", methods=["POST"])
def update_posts():
    """Create or delete a post."""
    if "username" not in flask.session:
        flask.abort(403)

    logname = flask.session["username"]
    operation = flask.request.form["operation"]
    connection = insta4288.model.get_db()

    if operation == "create":
        fileobj = flask.request.files["file"]

        if not fileobj.filename:
            flask.abort(400)

        uuid_basename = save_upload(fileobj)

        connection.execute(
            "INSERT INTO posts(filename, owner) VALUES (?, ?)",
            (uuid_basename, logname)
        )

    elif operation == "delete":
        postid = flask.request.form["postid"]

        cur = connection.execute(
            "SELECT filename, owner FROM posts WHERE postid = ?",
            (postid,)
        )
        post = cur.fetchone()

        if post is None or post["owner"] != logname:
            flask.abort(403)

        path = (
            insta4288.app.config["UPLOAD_FOLDER"] / post["filename"]
        )
        if path.exists():
            path.unlink()

        connection.execute(
            "DELETE FROM posts WHERE postid = ?",
            (postid,)
        )

    target = flask.request.args.get("target")
    if not target:
        target = f"/users/{logname}/"

    return flask.redirect(target)
