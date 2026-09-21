"""Insta4288 post view."""

import arrow
import flask
import insta4288
from insta4288.views.accounts import get_login_context


@insta4288.app.route('/posts/<int:postid>/')
def show_post(postid):
    """Display /posts/<postid>/ route."""
    logname, connection = get_login_context()

    if logname is None:
        return flask.redirect("/accounts/login/")

    cur = connection.execute(
        "SELECT posts.*, users.filename AS owner_img_url "
        "FROM posts JOIN users ON posts.owner = users.username "
        "WHERE posts.postid = ?",
        (postid,)
    )
    post = cur.fetchone()

    if post is None:
        flask.abort(404)

    post["created"] = arrow.get(post["created"]).humanize()

    cur = connection.execute(
        "SELECT COUNT(*) AS likes "
        "FROM likes WHERE postid = ?",
        (postid,)
    )
    post["likes"] = cur.fetchone()["likes"]

    cur = connection.execute(
        "SELECT likeid FROM likes "
        "WHERE owner = ? AND postid = ?",
        (logname, postid)
    )
    post["liked"] = cur.fetchone() is not None

    cur = connection.execute(
        "SELECT commentid, owner, text "
        "FROM comments WHERE postid = ? "
        "ORDER BY commentid ASC",
        (postid,)
    )
    post["comments"] = cur.fetchall()

    context = {
        "logname": logname,
        "post": post,
    }
    return flask.render_template("post.html", **context)
