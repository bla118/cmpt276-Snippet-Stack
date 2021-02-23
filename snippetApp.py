from flask import Flask, jsonify, request, render_template, session, g, redirect, url_for, flash
import os
import json
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(20)
basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        with sqlite3.connect('Users.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE username=?", [session['user_id']]) 
            response = cursor.fetchone()
            if (response):
                username = response[1]
                g.user = username
                print(g.user)
            else:
                return jsonify(message="Error")


@app.route('/')
def start():
    session.clear()
    return redirect(url_for("login"))


@app.route('/active')
def activePage():
    return render_template("active.html")


@app.route('/notyetimplemented')
def notyetimplementedPage():
    return render_template("notyetimplemented.html")


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)
        # session.clear()
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('Users.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE username=? AND password=?", [username, password]) 
            response = cursor.fetchone()
            if (response):
                print(response)
                session['user_id'] = username
                print("You are logged in")
                return render_template("index.html", username=session['user_id'])
            print("Invalid credentials")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route('/register', methods=['POST', 'GET'])
def register():
    ''' Handles form action from user registration page. Upon successful registration, user will be automatically logged in and directed to home'''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_status = "regular"
        confirmed_password = request.form['confirm-password']
        if (password != confirmed_password):
            print("Passwords do not match")
            return redirect(url_for("create_account"))
        with sqlite3.connect('Users.db') as conn:
            cursor = conn.cursor()   
            cursor.execute("SELECT * FROM Users WHERE username=?", [username])
            response = cursor.fetchone()
            if (response):
                print("User already exists")
                return redirect(url_for("create_account"))
            cursor.execute("INSERT INTO Users(username, password, status) VALUES (?,?,?)", [username, password, user_status]) 
            session['user_id'] = username
            print("Successfully registered new user")
            print("You are logged in")
            return render_template("index.html", username=session['user_id'])
    return render_template("login.html")



@app.route('/home')
def home():
    if not g.user:
        return redirect(url_for("login"))
    return render_template("index.html", username=session['user_id'])


@app.route('/create')
def create():
    if not g.user:
        return redirect(url_for("login"))
    return render_template("create.html")


@app.route('/search')
def search():
    if not g.user:
        return redirect(url_for("login"))
    return render_template("search.html")


@app.route('/api/create_snippet', methods=['GET', 'POST'])
def add_snippet():
    if request.method == 'GET':
        if not g.user:
            return redirect(url_for("login"))
    data = request.data.decode('ascii')
    data = json.loads(data)
    with sqlite3.connect('Snippets.db') as conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Snippets(name, language, code) VALUES (?,?,?)", 
            [data['name'], data['language'].lower(), data['code']])
            return jsonify(message="Successfully created new snippet"), 201
        except Exception:
            return jsonify(message="Error"), 400


@app.route('/api/fetch_snippet', methods=['GET', 'POST'])
def fetch_snippet():
    if request.method == 'GET':
        if not g.user:
            return redirect(url_for("login"))
    # print(json.loads(request.data))
    data = request.data.decode('ascii')
    data = json.loads(data)
    try:
        language = data['language'].lower()
        search_key = data['search_key']
        with sqlite3.connect('Snippets.db') as conn:
            cursor = conn.cursor()
            # cursor.execute("SELECT COUNT(*) FROM Test")
            # print("Total entries: ", cursor.fetchone())
            cursor.execute("SELECT * FROM Snippets WHERE Language=? AND name LIKE ? LIMIT 10",
            [language, f'%{search_key}%'])
            data = cursor.fetchall()
            return json.dumps(data)
    except Exception:
        return jsonify(message="Error"), 400


@app.route('/api/delete_snippet', methods=['GET', 'POST'])
def delete_snippet():
    ''' Deletes a snippet from database by id. Only works from the search results page '''
    if request.method == 'GET':
        if not g.user:
            return redirect(url_for("login"))
    data = request.data.decode('ascii')
    data = json.loads(data)
    try:
        identifier = data['idToDel']
        with sqlite3.connect('Snippets.db') as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Snippets WHERE id=?", [int(identifier)])
            return jsonify(message="Successfully deleted snippet")
    except Exception:
        return jsonify(message="Error"), 400


@app.route('/createAccount')
def create_account():
    return render_template("createAccount.html")


@app.route('/request_snippet')
def request_snippet_page():
    ''' Entry point for request snippet page '''
    print(g.user)
    return render_template('requestSnippet.html')


@app.route('/api/request_snippet', methods=['POST'])
def request_snippet():
    ''' Accepts an authenticated user request for a new snippet and inserts it into the database '''
    if not g.user:
        return jsonify(message="Not logged in")
    try:
        description = request.form['description']
        language = request.form['language']
        user = g.user
        with sqlite3.connect('Users.db') as conn:
            cursor = conn.cursor()
            # the status of the user request is set to pending by default
            cursor.execute("INSERT INTO Requests(user, description, language, status) VALUES(?,?,?,?)", [user, description, language, 'pending'])
        return jsonify(message="Successfully created new snippet request")
    except Exception:
        return jsonify(message="Error"), 400


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
    # app.run()
