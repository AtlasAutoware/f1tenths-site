from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from multiprocessing import Value
import hashlib
import sys
import simulator.pkg.src.pkg.main as simCode
import re
from datetime import datetime
class User:
    def __init__(self, id, username, password,email):
        self.id = id
        self.username = username
        self.password = password #do you really think we would store the password here?

        self.email = email

    def __repr__(self):
        return f'<User: {self.username}>'

class Run:
    def __init__(self, id, runtime, time, username):
        self.id = id
        self.runtime = runtime
        self.time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.username = username
        
    def __repr__(self):
        return f'<Run: {self.id}>'

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
print(myresult)
users = []
j = Value('i',1)
for i in myresult:
    
    with j.get_lock():
        users.append(User(id=i[0],username=i[1],password=i[2],email=i[3]))
        j.value += 1;

mycursor = mydb.cursor()
#print("select runs.id, runtime, time, username from "+ login[4] + " join "+ login[3] +" on userid = "+login[3]+".id")
mycursor.execute("select runs.id, runtime, time, username from "+ login[4] + " join "+ login[3] +" on userid = "+login[3]+".id")
myresult = mycursor.fetchall()
print(myresult)
runs = []
for i in myresult:
    runs.append(Run(id=i[0],runtime=i[1],time=i[2],username=i[3]))
     





app = Flask(__name__)
app.secret_key = 'hello'

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        print(users)
        try:
            user = [x for x in users if x.id == session['user_id']][0]
            g.user = user
            print(g.user)
        except IndexError:
            session.pop('user_id', None)
            g.user = None

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
        if(str(result) == "Crash"):
            result1 = "99999.99999"
        else:
            result1 = '%.3f' % float(result)
        now = datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        
        mydb.reconnect()
        mycursor = mydb.cursor()
        #print()
        mycursor.execute("insert into runs (runtime,time,userid) values ('"+result1+"', '"+now+"', '"+str(g.user.id)+"'"+")")
        runs.sort(key=lambda x: x.runtime, reverse=False)
    
        mydb.commit()
        return render_template("yay.html", run_time=result)
        
            
   

@app.route('/leaderboard', methods =["GET", "POST"])
def leaderboard():
    if request.method == "POST":
        return render_template("leaderboard.html", runs=runs)
    return render_template("leaderboard.html", runs=runs)

@app.route('/register', methods =["GET", "POST"])
def register():
    if request.method == "POST":
        return render_template("register.html", txt="")
        
    return render_template("register.html", txt="")
@app.route('/register1', methods =["GET", "POST"])
def register1():
    #print('Hello world!', file=sys.stderr)
    if request.method == "POST":
        return render_template("register.html", txt="Emails/passwords do not match")
    return render_template("register.html", txt="Emails/passwords do not match")
@app.route('/register2', methods =["GET", "POST"])
def register2():
    #print('Hello world!', file=sys.stderr)
    if request.method == "POST":
        return render_template("register.html", txt="Bad username/password/email")
    return render_template("register.html", txt="Bad username/password/email")
@app.route('/registered', methods=["GET","POST"])
def registered():
    if request.method == "POST":
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        usn = r'^[a-zA-Z0-9_-]*$'
        
        if(not re.fullmatch(usn,request.form['username']) or request.form['username']=='' or not re.fullmatch(regex,request.form['email1']) or not re.fullmatch(regex,request.form['email2'])):
            return redirect(url_for('register2'))
        
        if(request.form['email1'] == request.form['email2'] and request.form['password1'] == request.form['password2']):
            
            with j.get_lock():
                u1 = request.form['username']
                p1 = hashlib.sha224(request.form['password1'].encode()).hexdigest()
                e1 = request.form['email2']
                users.append(User(id=j.value,username=u1,password= p1,email= e1))

                j.value += 1
                mydb.reconnect()
                mycursor = mydb.cursor()
                #print("insert into login (username,pwhash,email) values ('"+u1+"', '"+p1+"', '"+e1+"'"+")")
                #try:
                mycursor.execute("insert into login (username,pwhash,email) values ('"+u1+"', '"+p1+"', '"+e1+"'"+")")
                
            
                mydb.commit()
                return redirect(url_for('login2'))
            
            
                mydb.session.rollback()
                return render_template("error.html", theerror = "MySQL unable to save")
        
            #except:
            #    mycursor.rollback()
            #    return redirect(url_for('login3'))
            #myresult = mycursor.fetchall()
            
        if(request.form['email1'] != request.form['email2'] or request.form['password1'] != request.form['password2']):
            return redirect(url_for('register1'))
        return redirect(url_for('register'))
    return redirect(url_for('register'))
@app.route('/back2home', methods =["GET", "POST"])
def back2home():
    if request.method == "POST":

        if 'user_id' not in session:
            return redirect(url_for('login1'))

        return redirect(url_for('profile'))

@app.route('/login2',methods=['GET','POST'])
def login2():
    return render_template('login.html',txt="Created user")
@app.route('/login3',methods=['GET','POST'])
def login3():
    return render_template('login.html',txt="Error making user: try again")

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



@app.route('/profile', methods=['GET','POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login1'))

    return render_template('profile.html')



@app.route('/')
def index():
    return redirect(url_for('profile'))