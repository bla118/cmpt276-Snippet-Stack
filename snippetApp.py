from flask import Flask, jsonify, request, render_template, session, g, redirect, url_for, flash
import os
import json
import sqlite3

app = Flask(__name__)
app.secret_key = "somesecretasskey"
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


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


@app.route("/")
def start():
    session.clear()
    return redirect(url_for("login"))


@app.route("/login", methods=['POST','GET'])
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


@app.route("/home")
def home():
    if not g.user:
        return redirect(url_for("login"))
    return render_template("index.html", username=session['user_id'])


@app.route("/create")
def create():
    if not g.user:
        return redirect(url_for("login"))
    return render_template("create.html")


@app.route("/search")
def search():
    if not g.user:
        return redirect(url_for("login"))
    return render_template("search.html")


@app.route("/api/create_snippet", methods=['GET', 'POST'])
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
            [data['name'], data['language'], data['code']])
            return jsonify(message="Successfully created new snippet"), 201
        except Exception:
            return jsonify(message="Error"), 400


@app.route("/api/fetch_snippet", methods=['GET', 'POST'])
def fetch_snippet():
    if request.method == 'GET':
        if not g.user:
            return redirect(url_for("login"))
    # print(json.loads(request.data))
    data = request.data.decode('ascii')
    data = json.loads(data)
    try:
        language = data['language']
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


@app.route("/api/delete_snippet", methods=['GET', 'POST'])
def delete_snippet():
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

@app.route("/createAccount")
def createAccount():
    return render_template("createAccount.html")

@app.route("/active")
def activePage():
    return render_template("active.html")

@app.route("/home")
def homePage():
    return render_template("home.html")

@app.route("/notyetimplemented")
def notyetimplementedPage():
    return render_template("notyetimplemented.html")