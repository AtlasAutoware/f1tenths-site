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

users = []
#devuser:devuser
#A:1
users.append(User(id=0, username='devuser', password='6684282bf0c558ae99560ccd9eea5c3ba9d36767132a11a8298bdc6fcb0d368d623fd1305f2c6ac2782a5356d425fc664661c3f9503e7b37c9c2401a05d8130c'))
users.append(User(id=1, username='A', password='4dff4ea340f0a823f15d3f4f01ab62eae0e5da579ccb851f8db9dfe84c58b2b37b89903a740e1ee172da793a6e79d560e5f7f9bd058a12a280433ed6fa46510a'))



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

@app.route('/login1', methods=['GET', 'POST'])
def login1():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = hashlib.sha512(request.form['password'].encode()).hexdigest() 

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