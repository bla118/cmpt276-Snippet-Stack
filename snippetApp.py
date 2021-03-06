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

###########################################
# table: <snippet_id>                     #
#                                         #
#+----------+----------+-------+---------+#
#| reply_id | contents | likes | user_id |#
#+----------+----------+-------+---------+#
#| 1        | "hello"  |   3   | stalin4 |#
#| 2        | "cool"   |   0   | hitler4 |#
###########################################

# creates the table above
# inserts comments to the above table
# example: insert_comments_for_snippet("s_2222", (contents, user_id))
def insert_comments_for_snippet(snippet_id, insert_data):
    with sqlite3.connect('Snippets.db') as conn:
        cursor = conn.cursor()
        # create table if table does not exist
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {snippet_id} (reply_id INTEGER PRIMARY KEY, 
                                                contents text NOT NULL, 
                                                likes integer NOT NULL, 
                                                user_id text NOT NULL);''')

        # insert values
        cursor.execute(f'''INSERT INTO {snippet_id} (contents, likes, user_id) VALUES (?, 0, ?);''', insert_data)

# only deletes all the comments to a snippet
# does not delete the snippet itself
# call this when the snippet owner deletes snippet
def delete_comments_for_snippet(snippet_id):
    with sqlite3.connect('Snippets.db') as conn:
        cursor = conn.cursor()
        # delete table if table does exists
        cursor.execute(f'''DROP TABLE IF EXISTS {snippet_id};''')

######################## TEST FUNCTION ################################
# tests the above 2 functions
# set display=True for debugging
def test_insert_and_delete_comments_for_snippet(display=True):
  snippet_id = "s_122"

  user_id = "admin"
  comment = "<pre><code>print(\"hello\")</pre></code>"

  insert_comments_for_snippet(snippet_id, (comment, user_id))

  with sqlite3.connect('Snippets.db') as conn:
      cursor = conn.cursor()
      data = cursor.execute(f'''SELECT * FROM {snippet_id} WHERE reply_id = 1;''').fetchone()
      if display:
        print("reply_id:", data[0])
        print("contents:", data[1])
        print("likes:", data[2])
        print("user_id:", data[3])
      
      if comment == data[1] and user_id == data[3]:
        print("INSERT PASSED.")

  delete_comments_for_snippet(snippet_id)

  with sqlite3.connect('Snippets.db') as conn:
      cursor = conn.cursor()
      try:
        data = cursor.execute(f'''SELECT * FROM {snippet_id} WHERE reply_id = 1;''').fetchone()
      except:
        print("DELETE PASSED.")


########### the above functions have been tested ######################

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
    ''' Handles user login by finding matching username and password record from teh Users database '''
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
                # print(response)
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
        if (len(password) < 6 or len(username) < 6):
            print("Password and username must be at least 6 characters long")
            return redirect(url_for("create_account"))
        with sqlite3.connect('Users.db') as conn:
            cursor = conn.cursor()   
            cursor.execute("SELECT * FROM Users WHERE username=?", [username])
            response = cursor.fetchone()
            if (response):
                print("User already exists")
                return redirect(url_for("login"))
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
    ''' Creates a new snippet in the database '''
    if request.method == 'GET':
        if not g.user:
            return redirect(url_for("login"))
    data = request.data.decode('ascii')
    data = json.loads(data)
    with sqlite3.connect('Snippets.db') as conn:
        try:
            cursor = conn.cursor()
            private = 1 if data['private'] else 0
            cursor.execute("INSERT INTO Snippets(name, language, code, author, private) VALUES (?,?,?,?,?)", 
            [data['name'].lower(), data['language'].lower(), data['code'], g.user, private])
            return jsonify(message="Successfully created new snippet"), 201
        except Exception:
            return jsonify(message="Error"), 400


@app.route('/api/fetch_snippet', methods=['GET', 'POST'])
def fetch_snippet():
    ''' Fetches matching snippets from database by langauge and snippet name. Unlike other endpoints, this one takes a Js fetch request instead of Flask form '''
    if request.method == 'GET':
        if not g.user:
            return redirect(url_for("login"))
    data = request.data.decode('ascii')
    data = json.loads(data)
    try:
        language = data['language'].lower()
        search_key = data['search_key'].lower()
        private = 1 if data['private'] else 0
        with sqlite3.connect('Snippets.db') as conn:
            cursor = conn.cursor()
            # if private flag in form is checked, return only snippets created by this user
            if private:
                cursor.execute("SELECT * FROM Snippets WHERE author=? AND language=? AND name LIKE ? LIMIT 10",
                [g.user, language, f'%{search_key}%'])
            # otherwise, return all matching public snippets by other users AND matching snippets by this user
            else:
                # too lazy to write, just copy/pasted the above query and unioned...
                cursor.execute("SELECT * FROM Snippets WHERE language=? AND name LIKE ? AND (private <> 1 OR private IS NULL) UNION SELECT * FROM Snippets WHERE author=? AND language=? AND name LIKE ? LIMIT 10",
                [language, f'%{search_key}%', g.user, language, f'%{search_key}%'])
            data = cursor.fetchall()
            return json.dumps(data)
    except Exception:
        return jsonify(message="Error"), 400


@app.route('/api/delete_snippet', methods=['GET', 'POST'])
def delete_snippet():
    ''' Deletes a snippet from database by id. Only works from the search results page. Users are only allowed to delete snippets created by themselves '''
    if request.method == 'GET':
        if not g.user:
            return redirect(url_for("login"))
    data = request.data.decode('ascii')
    data = json.loads(data)
    try:
        identifier = data['idToDel']
        with sqlite3.connect('Snippets.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Snippets WHERE id=? AND author=?", [int(identifier), g.user])
            res = cursor.fetchone()
            if res:
                cursor.execute("DELETE FROM Snippets WHERE id=? AND author=?", [int(identifier), g.user])
            else:
                return jsonify(message="Cannot delete snippet created by others"), 401
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
        with sqlite3.connect('Snippets.db') as conn:
            cursor = conn.cursor()
            # the status of the user request is set to pending by default
            cursor.execute("INSERT INTO Requests(user, description, language, status) VALUES(?,?,?,?)", [user, description.lower(), language.lower(), 'pending'])
        return redirect(url_for("home"))
    except Exception:
        return jsonify(message="Error"), 400


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
    # app.run()
