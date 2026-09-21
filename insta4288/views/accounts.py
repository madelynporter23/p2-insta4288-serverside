"""Insta4288 account views."""

import hashlib
import pathlib
import uuid
import flask
import insta4288


def hash_password(password):
    """Hash a password for storage."""
    algorithm = "sha512"
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode("utf-8"))
    password_hash = hash_obj.hexdigest()
    return "$".join([algorithm, salt, password_hash])


def check_password(password, password_db_string):
    """Check a password against a stored password."""
    algorithm, salt, stored_hash = password_db_string.split("$")
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode("utf-8"))
    password_hash = hash_obj.hexdigest()
    return password_hash == stored_hash


def save_upload(fileobj):
    """Save an uploaded file and return its generated filename."""
    filename = fileobj.filename
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"
    path = insta4288.app.config["UPLOAD_FOLDER"] / uuid_basename
    fileobj.save(path)
    return uuid_basename


def get_login_context():
    """Return logged-in username and database connection."""
    logname = flask.session.get("username")
    connection = insta4288.model.get_db()
    return logname, connection


@insta4288.app.route('/accounts/login/')
def show_login():
    """Display /accounts/login/ route."""
    return flask.render_template("login.html")


@insta4288.app.route('/accounts/create/')
def show_create():
    """Display /accounts/create/ route."""
    return flask.render_template("create.html")


@insta4288.app.route('/accounts/auth/')
def show_auth():
    """Display /accounts/auth/ route."""
    if "username" not in flask.session:
        flask.abort(403)

    return "", 200


@insta4288.app.route('/accounts/edit/')
def show_edit():
    """Display /accounts/edit/ route."""
    connection = insta4288.model.get_db()

    if "username" not in flask.session:
        return flask.redirect("/accounts/login/")

    logname = flask.session["username"]

    cur = connection.execute(
        "SELECT username, fullname, email, filename "
        "FROM users WHERE username = ?",
        (logname,)
    )
    user = cur.fetchone()

    context = {
        "logname": logname,
        "user": user,
    }
    return flask.render_template("edit.html", **context)


@insta4288.app.route('/accounts/password/')
def show_password():
    """Display /accounts/password/ route."""
    if "username" not in flask.session:
        return flask.redirect("/accounts/login/")

    logname = flask.session["username"]

    context = {
        "logname": logname,
    }
    return flask.render_template("password.html", **context)


@insta4288.app.route('/accounts/delete/')
def show_delete():
    """Display /accounts/delete/ route."""
    if "username" not in flask.session:
        return flask.redirect("/accounts/login/")

    logname = flask.session["username"]

    context = {
        "logname": logname,
    }
    return flask.render_template("delete.html", **context)


def login_account(connection):
    """Log in an existing account."""
    username = flask.request.form["username"]
    password = flask.request.form["password"]

    if not username or not password:
        flask.abort(400)

    cur = connection.execute(
        "SELECT password FROM users WHERE username = ?",
        (username,)
    )
    user = cur.fetchone()

    if user is None:
        flask.abort(403)

    if not check_password(password, user["password"]):
        flask.abort(403)

    flask.session["username"] = username


def create_account(connection):
    """Create a new account."""
    username = flask.request.form["username"]
    password = flask.request.form["password"]
    fullname = flask.request.form["fullname"]
    email = flask.request.form["email"]
    fileobj = flask.request.files["file"]

    if (
        not username
        or not password
        or not fullname
        or not email
        or not fileobj.filename
    ):
        flask.abort(400)

    cur = connection.execute(
        "SELECT username FROM users WHERE username = ?",
        (username,)
    )
    if cur.fetchone() is not None:
        flask.abort(409)

    uuid_basename = save_upload(fileobj)
    password_db_string = hash_password(password)

    connection.execute(
        "INSERT INTO users("
        "username, fullname, email, filename, password"
        ") VALUES (?, ?, ?, ?, ?)",
        (
            username,
            fullname,
            email,
            uuid_basename,
            password_db_string,
        )
    )

    flask.session["username"] = username


def edit_account(connection):
    """Edit the logged-in account."""
    logname = flask.session["username"]
    fullname = flask.request.form["fullname"]
    email = flask.request.form["email"]
    fileobj = flask.request.files["file"]

    if not fullname or not email:
        flask.abort(400)

    if fileobj.filename:
        cur = connection.execute(
            "SELECT filename FROM users WHERE username = ?",
            (logname,)
        )
        old_filename = cur.fetchone()["filename"]

        old_path = (
            insta4288.app.config["UPLOAD_FOLDER"] / old_filename
        )
        if old_path.exists():
            old_path.unlink()

        uuid_basename = save_upload(fileobj)

        connection.execute(
            "UPDATE users "
            "SET fullname = ?, email = ?, filename = ? "
            "WHERE username = ?",
            (fullname, email, uuid_basename, logname)
        )
    else:
        connection.execute(
            "UPDATE users "
            "SET fullname = ?, email = ? "
            "WHERE username = ?",
            (fullname, email, logname)
        )


def update_password(connection):
    """Update the logged-in account password."""
    logname = flask.session["username"]
    password = flask.request.form["password"]
    new_password1 = flask.request.form["new_password1"]
    new_password2 = flask.request.form["new_password2"]

    if not password or not new_password1 or not new_password2:
        flask.abort(400)

    cur = connection.execute(
        "SELECT password FROM users WHERE username = ?",
        (logname,)
    )
    user = cur.fetchone()

    if not check_password(password, user["password"]):
        flask.abort(403)

    if new_password1 != new_password2:
        flask.abort(401)

    password_db_string = hash_password(new_password1)

    connection.execute(
        "UPDATE users SET password = ? WHERE username = ?",
        (password_db_string, logname)
    )


def delete_account(connection):
    """Delete the logged-in account."""
    logname = flask.session["username"]

    cur = connection.execute(
        "SELECT filename FROM users WHERE username = ?",
        (logname,)
    )
    user = cur.fetchone()

    profile_path = (
        insta4288.app.config["UPLOAD_FOLDER"] / user["filename"]
    )
    if profile_path.exists():
        profile_path.unlink()

    cur = connection.execute(
        "SELECT filename FROM posts WHERE owner = ?",
        (logname,)
    )
    posts = cur.fetchall()

    for post in posts:
        post_path = (
            insta4288.app.config["UPLOAD_FOLDER"] / post["filename"]
        )
        if post_path.exists():
            post_path.unlink()

    connection.execute(
        "DELETE FROM users WHERE username = ?",
        (logname,)
    )

    flask.session.clear()


@insta4288.app.route('/accounts/', methods=['POST'])
def update_accounts():
    """Perform account operation."""
    operation = flask.request.form["operation"]
    connection = insta4288.model.get_db()

    if operation == "login":
        login_account(connection)
    elif operation == "create":
        create_account(connection)
    elif operation == "edit_account":
        edit_account(connection)
    elif operation == "update_password":
        update_password(connection)
    elif operation == "delete":
        delete_account(connection)

    target = flask.request.args.get("target")
    if not target:
        target = "/"

    return flask.redirect(target)
