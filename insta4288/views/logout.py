"""Insta4288 logout view."""
import flask
import insta4288


@insta4288.app.route("/accounts/logout/", methods=["POST"])
def logout():
    """Log out the user."""
    flask.session.clear()
    return flask.redirect("/accounts/login/")
