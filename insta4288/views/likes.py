"""Insta4288 likes view."""
import flask
import insta4288


LOGGER = flask.logging.create_logger(insta4288.app)


@insta4288.app.route("/likes/", methods=["POST"])
def update_likes():
    """Create or delete a like."""
    if "username" not in flask.session:
        flask.abort(403)

    logname = flask.session["username"]
    operation = flask.request.form["operation"]
    postid = flask.request.form["postid"]

    LOGGER.debug("operation = %s", operation)
    LOGGER.debug("postid = %s", postid)

    connection = insta4288.model.get_db()

    cur = connection.execute(
        "SELECT likeid FROM likes "
        "WHERE owner = ? AND postid = ?",
        (logname, postid)
    )
    like = cur.fetchone()

    if operation == "like":
        if like is not None:
            flask.abort(409)
        connection.execute(
            "INSERT INTO likes(owner, postid) VALUES (?, ?)",
            (logname, postid)
        )
    elif operation == "unlike":
        if like is None:
            flask.abort(409)
        connection.execute(
            "DELETE FROM likes "
            "WHERE owner = ? AND postid = ?",
            (logname, postid)
        )

    target = flask.request.args.get("target")
    if not target:
        target = "/"
    return flask.redirect(target)
