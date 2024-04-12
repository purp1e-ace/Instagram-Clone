"""
Insta485 index (main) view.

URLs include:
/
This is the endpoint for all things accounts!!!!!
"""

import uuid
import hashlib
import os
import flask
import insta485
from insta485.views.helper import get_uuidbasename


@insta485.app.route('/accounts/', methods=['POST'])
def accounts_manip():
    """For accounts."""
    operation = flask.request.form.get('operation')

    if operation == 'login':
        return login()
    if operation == 'create':
        return make_create()
    if operation == 'delete':
        return delete()
    if operation == 'edit_account':
        return edit_account()
    if operation == 'update_password':
        return update_password()
    return None


def login():
    """Login."""
    # operation = flask.request.form.get('operation')
    username = flask.request.form.get('username')
    password = flask.request.form.get('password')
    # target = flask.request.args.get('target')

    # """Checking if the username and password fields are empty"""
    if username == "" or password == "":
        flask.abort(400)

    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT password "
        "FROM users "
        "WHERE username = ?",
        (username,)
    )

    # """Getting the hashed password in the database"""
    log = cur.fetchone()

    # """Checking if the username exists in the database"""
    if log is None:
        flask.abort(403)
    # hashed_password = log['password']

    # """Getting the salt."""
    # database_salt = hashed_password.split('$')[1]

    # """hashing the password!!!"""
    # algorithm = 'sha512'

    # hash_obj = hashlib.new(algorithm)
    # password_salted = database_salt + password
    # hash_obj.update(password_salted.encode('utf-8'))
    # password_hash = hash_obj.hexdigest()
    # password_db_string = "$".join([algorithm, database_salt, password_hash])

    # """Checking if the password matches"""
    if password_is_correct(username, password):
        # """shit matches account exists and password matches"""

        # """Login the user"""
        flask.session['username'] = username
        # """Redirect to URL"""
        return flask.redirect('/')

    # """the password is wrong or the user does not exist"""
    return flask.abort(403)


def make_create():
    """Create account."""
    fullname = flask.request.form.get('fullname')
    username = flask.request.form.get('username')
    password_raw = flask.request.form.get('password')
    email = flask.request.form.get('email')
    fileobj = flask.request.files["file"]
    target = flask.request.args.get('target') or '/'

    # """ check for empty fields """
    if fullname == '' or username == '' or password_raw == '' \
            or email == '' or fileobj == '':
        flask.abort(400)

    password = my_hash(password_raw)

    # """ check if account already exists """
    connection = insta485.model.get_db()

    cur = connection.execute(
        "SELECT COUNT(*) FROM users WHERE username = ?",
        (username,)
    )
    # If user already exist
    if cur.fetchone() == 1:
        flask.abort(409)

    filename = get_uuid_filename(fileobj)

    # """ Input the user data into the database """
    cur = connection.execute(
        "INSERT INTO users (username, fullname, email, filename, password)"
        " VALUES (?, ?, ?, ?, ?)",
        (username, fullname, email, filename, password)
    )

    # """ Login the user """
    flask.session['username'] = username
    # """Redirect to URL"""
    return flask.redirect(target)


def delete():
    """Account delete."""
    target = flask.request.args.get('target') or '/'

    if not flask.session['username']:
        return flask.abort(403)
    logname = flask.session['username']

    connection = insta485.model.get_db()

    # """ Getting users posts """
    cur = connection.execute(
        "SELECT filename FROM posts WHERE owner = ?",
        (logname,)
    )
    post_filenames = cur.fetchall()

    # Write down old file name before updating.
    cur = connection.execute(
        "SELECT filename FROM users WHERE username = ?",
        (logname,)
    )
    filename = cur.fetchone()
    cur = connection.execute(
        "DELETE FROM users WHERE username = ?",
        (logname,)
    )

    # Remove old image file.
    # os.remove(insta485.app.config["UPLOAD_FOLDER"] / filename)
    upload_folder = insta485.app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, filename['filename'])
    os.remove(file_path)

    # """ Deleteing users posts """
    for post_filename in post_filenames:
        upload_folder = insta485.app.config["UPLOAD_FOLDER"]
        file_path = os.path.join(upload_folder, post_filename['filename'])
        os.remove(file_path)

    # clear the user’s session
    del flask.session['username']

    return flask.redirect(target)


def edit_account():
    """Account edit."""
    target = flask.request.args.get('target') or '/'

    # check if user is logged in
    if 'username' not in flask.session:
        return flask.abort(403)
    logname = flask.session['username']

    fileobj = flask.request.files.get("file")
    fullname = flask.request.form.get('fullname')
    email = flask.request.form.get('email')

    connection = insta485.model.get_db()

    # If a file is uploaded.
    if fileobj:
        filename = get_uuid_filename(fileobj)
        # Write down old file name before updating.
        cur = connection.execute(
            "SELECT filename FROM users WHERE username = ?",
            (logname,)
        )
        cur.fetchone()
        # Remove old image file.
        upload_folder = insta485.app.config["UPLOAD_FOLDER"]
        file_path = os.path.join(upload_folder, filename)
        os.remove(file_path)

        # Update account info.
        cur = connection.execute(
            "UPDATE users SET filename = ?, fullname = ?, email = ? "
            "WHERE username = ?",
            (filename, fullname, email, logname)
        )
    # Ohterwise, only update fullname and email.
    else:
        cur = connection.execute(
            "UPDATE users SET fullname = ?, email =? "
            "WHERE username = ?",
            (fullname, email, logname)
        )
    return flask.redirect(target)


def update_password():
    """Update password."""
    target = flask.request.args.get('target') or '/'

    # check if user is logged in
    if 'username' not in flask.session:
        return flask.abort(403)
    logname = flask.session['username']

    password = flask.request.form.get("password")
    new_password1 = flask.request.form.get('new_password1')
    new_password2 = flask.request.form.get('new_password2')

    # If any of these fields are empty then abort
    if not (password and new_password1 and new_password2):
        flask.abort(400)

    # Verify password against the user’s password hash in the databas.
    if not password_is_correct(logname, password):
        flask.abort(403)

    # Verify both new passwords match.
    if not new_password1 == new_password2:
        flask.abort(401)

    # """Hashing the new password!!!"""
    new_password = my_hash(new_password1)

    connection = insta485.model.get_db()
    connection.execute(
        "UPDATE users SET password = ? WHERE username = ?",
        (new_password, logname)
    )
    return flask.redirect(target)


def password_is_correct(username, password):
    """Check password."""
    # """Get the salt."""
    password_db_string = get_password(username)
    salt = password_db_string.split('$')[1]

    # """Hashing the password!!!"""
    hashed_password = my_hash(password, salt)

    return password_db_string == hashed_password


def my_hash(password, salt=None):
    """Filename hashing."""
    algorithm = 'sha512'
    if not salt:
        salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string


def get_password(username):
    """Get password helper function."""
    # """Helpfer function for getting a stored password"""

    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT password "
        "FROM users "
        "WHERE username = ?",
        (username,)
    )

    # """Getting the hashed password in the database"""
    hashed_password = cur.fetchone()

    # """Checking if the username exists in the database"""

    if hashed_password is None:
        flask.abort(403)
    hashed_password = hashed_password['password']

    # """Getting the password."""
    return hashed_password


def get_uuid_filename(fileobj):
    """Things."""
    filename = fileobj.filename

    # Compute base name (filename without directory).  We use a UUID to avoid
    # clashes with existing files, and ensure that
    # the name is compatible with the
    # filesystem. For best practive, we ensure
    # uniform file extensions (e.g.
    # lowercase).
    # stem = uuid.uuid4().hex
    # suffix = pathlib.Path(filename).suffix.lower()
    # uuid_basename = f"{stem}{suffix}"
    uuid_basename = get_uuidbasename(filename)

    # Save to disk
    path = insta485.app.config["UPLOAD_FOLDER"] / uuid_basename
    fileobj.save(path)
    print('saved', uuid_basename)
    return uuid_basename
