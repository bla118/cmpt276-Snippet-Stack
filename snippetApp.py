from flask import Flask, jsonify, request, render_template, session, g, redirect, url_for, flash
import os
import json
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(20)
basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

snippets = []
replies = []
class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

class Snippet:
    def __init__(self, data, request_user):
        self.id = data[0]
        self.name = data[1]
        self.language = data[2]
        self.code = data[3]
        self.user = data[4]
        self.likes = data[6]
        self.request_user = request_user
        # self.ispublic = public

    def belongsToUser(self):
        return self.user == self.request_user

    def isPublic(self):
        return self.ispublic

class Reply:
    def __init__(self, id, contents, user, likes, request_user):
        self.id = id
        self.contents = contents
        self.user_id = user
        self.likes = likes
        self.request_user = request_user

    def belongsToUser(self):
        return self.user_id == self.request_user

def get_snippet_list(data, user):
    snippets = []
    for d in data:
        if d:
            snippets.append(Snippet(d, user))

    return snippets

def get_comments_list(data, user):
    comments = []
    for d in data:
        if d:
            comments.append(Reply(d, user))
    return comments

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

@app.route('/about')
def about():
    return render_template("about.html")

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


@app.route('/snippetDisplay')
def snippetDisplay():
    if not g.user:
        return redirect(url_for("login"))
    return render_template("snippetDisplay.html", snippets=snippets)

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
            cursor.execute("INSERT INTO Snippets(name, language, code, author, private, likes) VALUES (?,?,?,?,?,?)", 
            [data['name'].lower(), data['language'].lower(), data['code'], g.user, private, 0])
            return jsonify(message="Successfully created new snippet"), 201
        except Exception:
            return jsonify(message="Error"), 400


@app.route('/api/fetch_snippet', methods=['GET', 'POST'])
def fetch_snippet():
    ''' Fetches matching snippets from database by langauge and snippet name. Unlike other endpoints, this one takes a Js fetch request instead of Flask form '''
    if request.method == 'GET':
        if not g.user:
            return redirect(url_for("login"))
        return render_template("home.html", username=g.user)
        
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
            dataset = {'data':data, 'user':g.user}

            print(dataset)

            return json.dumps(dataset)
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


@app.route('/api/comment_snippet', methods=['POST'])
def comment_snippet():
    ''' Receives a JSON object of user id, snippet id (the snippet being commented on) and comment text and inserts them into the Comments table '''
    if not g.user:
        return redirect(url_for("login"))

    data = request.data.decode('ascii')
    data = json.loads(data)
    try:
        username = data['username']
        snippet_id = int(data['snippet_id'])
        comment_text = data['comment_text']
        with sqlite3.connect('Snippets.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Comments(snippet_id, commenting_user, comment_text) VALUES(?,?,?)", [snippet_id, username, comment_text])
            comment_id = cursor.execute("SELECT MAX(rowid) FROM Comments;").fetchone()[0]
            print(comment_id)
            return json.dumps(comment_id)
    except Exception as e:
        print(e)
        return jsonify(message="Error"), 400

@app.route('/api/edit_comment', methods=['POST'])
def edit_comment():
    if not g.user:
        return redirect(url_for("login"))
        
    data = request.data.decode('ascii')
    data = json.loads(data)
    try:
        print(data)
        snippet_id = int(data['comment_id'])
        edited_code = data['edited_comment']
        with sqlite3.connect('Snippets.db') as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE Comments SET comment_text = ? where rowid = ?", [edited_code, snippet_id])
            return jsonify(message="Successfully updated snippet")
    except Exception as e:
        print(e)
        return jsonify(message="Error"), 400


@app.route('/api/get_comments_for_snippet', methods=['POST'])
def get_comments_for_snippet():
    ''' Receives a JSON object of snippet id and fetches all comments made on this snippet '''
    if not g.user:
        return redirect(url_for("login"))

    data = request.data.decode('ascii')
    data = json.loads(data)
    try:
        print(data)
        snippet_id = int(data['snippet_id'])
        with sqlite3.connect('Snippets.db') as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT c.rowid, c.commenting_user, c.comment_text FROM Comments c JOIN Snippets s ON c.snippet_id = s.id WHERE c.snippet_id = ?", [snippet_id])
            res = cursor.fetchall()
            
            print(res)
            return json.dumps(res)
    except Exception as e:
        print(e)
        return jsonify(message="Error"), 400


@app.route('/api/like_snippet', methods=['POST'])
def like_snippet():
    ''' Receives a JSON object of snippet id, adds a like to that snippet and returns the new like count in JSON format. Unliking a post or cancelling a like is currently not supported'''
    if not g.user:
        return redirect(url_for("login"))
        
    data = request.data.decode('ascii')
    data = json.loads(data)
    try:
        snippet_id = int(data['snippet_id'])
        with sqlite3.connect('Snippets.db') as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE Snippets SET likes = likes + 1 where id = ?", [snippet_id])
            cursor.execute("SELECT likes FROM Snippets WHERE id = ?", [snippet_id])
            new_like_count = cursor.fetchone()
            return json.dumps(new_like_count)
    except Exception as e:
        print(e)
        return jsonify(message="Error"), 400


@app.route('/api/edit_snippet', methods=['POST'])
def edit_snippet():
    if not g.user:
        return redirect(url_for("login"))
        
    data = request.data.decode('ascii')
    data = json.loads(data)
    try:
        snippet_id = int(data['snippet_id'])
        edited_code = data['edited_code']
        with sqlite3.connect('Snippets.db') as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE Snippets SET code = ? where id = ?", [edited_code, snippet_id])
            return jsonify(message="Successfully updated snippet")
    except Exception as e:
        print(e)
        return jsonify(message="Error"), 400


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
    # app.run()
