from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)

class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'

users = []
users.append(User(id=0, username='devuser', password='devuser'))
users.append(User(id=1, username='A', password='1'))
users.append(User(id=2, username='B', password='2'))
users.append(User(id=3, username='C', password='3'))


app = Flask(__name__)
app.secret_key = 'hello'

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user
        

@app.route('/login1', methods=['GET', 'POST'])
def login1():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']
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
    if not g.user:
        return redirect(url_for('login'))

    return render_template('profile.html')

@app.route('/')
def index():
    return render_template('login.html',txt="")