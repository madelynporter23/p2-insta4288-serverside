"""Insta4288 uploaded image view."""
import flask
import insta4288


@insta4288.app.route('/uploads/<filename>')
def download_file(filename):
    """Display /uploads/<filename> route."""
    if "username" not in flask.session:
        flask.abort(403)

    return flask.send_from_directory(
        insta4288.app.config['UPLOAD_FOLDER'],
        filename
    )
