"""Insta4288 explore view."""

import flask
import insta4288
from insta4288.views.accounts import get_login_context


@insta4288.app.route('/explore/')
def show_explore():
    """Display /explore/ route."""
    logname, connection = get_login_context()

    if logname is None:
        return flask.redirect("/accounts/login/")

    cur = connection.execute(
        "SELECT username, filename "
        "FROM users "
        "WHERE username != ? "
        "AND username NOT IN ("
        "SELECT username2 FROM following WHERE username1 = ?"
        ")",
        (logname, logname)
    )
    not_following = cur.fetchall()

    context = {
        "logname": logname,
        "not_following": not_following,
    }
    return flask.render_template("explore.html", **context)
