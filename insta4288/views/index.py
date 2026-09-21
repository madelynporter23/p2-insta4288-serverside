"""
Insta4288 index (main) view.

URLs include:
/
"""

import arrow
import flask
import insta4288


@insta4288.app.route('/')
def show_index():
    """Display / route."""
    logname = flask.session.get("username")

    if logname is None:
        return flask.redirect("/accounts/login/")

    connection = insta4288.model.get_db()

    cur = connection.execute(
        "SELECT posts.postid, posts.filename, posts.owner, posts.created, "
        "users.filename AS owner_img_url "
        "FROM posts "
        "JOIN users ON posts.owner = users.username "
        "WHERE posts.owner = ? "
        "OR posts.owner IN ("
        "SELECT username2 FROM following WHERE username1 = ?"
        ") "
        "ORDER BY posts.postid DESC",
        (logname, logname)
    )
    posts = cur.fetchall()

    for post in posts:
        post["created"] = arrow.get(post["created"]).humanize()

        cur = connection.execute(
            "SELECT COUNT(*) AS likes "
            "FROM likes WHERE postid = ?",
            (post["postid"],)
        )
        post["likes"] = cur.fetchone()["likes"]

        cur = connection.execute(
            "SELECT likeid FROM likes "
            "WHERE owner = ? AND postid = ?",
            (logname, post["postid"])
        )
        post["liked"] = cur.fetchone() is not None

        cur = connection.execute(
            "SELECT owner, text FROM comments "
            "WHERE postid = ? ORDER BY commentid ASC",
            (post["postid"],)
        )
        post["comments"] = cur.fetchall()

    context = {
        "logname": logname,
        "posts": posts,
    }
    return flask.render_template("index.html", **context)
