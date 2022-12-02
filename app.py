from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)
import hashlib

import simulator.pkg.src.pkg.main as simCode

class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'

import mysql.connector

#SQL Accessing info
with open("login") as rfile:
    login = [i.strip() for i in rfile.readlines()]
mydb = mysql.connector.connect(
  host="localhost",
  user=login[0],
  password=login[1],
  database=login[2]
)

mycursor = mydb.cursor()
mycursor.execute("SELECT * FROM "+login[3])
myresult = mycursor.fetchall()

users = []
#devuser:devuser
#A:1
for i in myresult:
    users.append(User(id=i[0],username=i[1],password=i[2]))



app = Flask(__name__)
app.secret_key = 'hello'

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user
        
@app.route('/codesubmit', methods =["GET", "POST"])
def codesubmit():
    if request.method == "POST":
        return render_template("codesubmit.html")
        code = request.form.get("code_")
        result = simCode.testCode(code)
        return render_template("yay.html", run_time=result)
@app.route('/compilecode', methods =["GET", "POST"])
def compilecode():
    if request.method == "POST":
        code = request.form.get("code_")
        result = simCode.testCode(code)
        return render_template("yay.html", run_time=result)



@app.route('/leaderboard', methods =["GET", "POST"])
def leaderboard():
    if request.method == "POST":
        return render_template("leaderboard.html")
    return render_template("leaderboard.html")

@app.route('/register', methods =["GET", "POST"])
def register():
    if request.method == "POST":
        return render_template("register.html")
    return render_template("register.html")

@app.route('/back2home', methods =["GET", "POST"])
def back2home():
    if request.method == "POST":

        if 'user_id' not in session:
            return redirect(url_for('login1'))

        return redirect(url_for('profile'))



@app.route('/login1', methods=['GET', 'POST'])
def login1():
    
    if 'user_id' in session:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = hashlib.sha224(request.form['password'].encode()).hexdigest() 

        try:        
            user = [x for x in users if x.username == username][0]
            if user and user.password == password:
                session['user_id'] = user.id
                return redirect(url_for('profile'))

            return render_template('login.html',txt="Wrong username/password")
        except IndexError:
            return render_template('login.html',txt="Wrong username/password")



    return render_template('login.html',txt="")
@app.route('/logout1', methods=['GET', 'POST'])
def logout1():
    session.pop('user_id', None)
    g.user = None
    return render_template('login.html',txt="Logged out")



@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login1'))

    return render_template('profile.html')



@app.route('/')
def index():
    return render_template('login.html',txt="")