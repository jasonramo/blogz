import datetime
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:admin@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True  #provides the sql commands in the terminal
db = SQLAlchemy(app)
app.secret_key = 'mB3kPa934nwmi2o'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(800))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['index', 'signup', 'login', 'blogs']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/', methods=['GET'])
def index():
    users = User.query.all()
    return render_template('index.html', title='BLOGZ!', users=users)

@app.route('/login', methods=['POST','GET'])
def login():
    email = ''
    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged In")
            return redirect('/newpost')
        else:
            flash('Password doesn\'t match, or user does not exist.', 'error')

    return render_template('login.html', email=email)        

@app.route('/signup', methods=['POST','GET'])
def signup():
    email = ''
    password = ''
    verify = ''

    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists, please use another email.', 'error')
        elif len(email) < 3 and len(password) < 3:
            flash('Email or password too short. Please choose at least four (4) characters.', 'error')
        elif password != verify:
            flash('Passwords do not match', 'error')
        elif not existing_user and password == verify:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/newpost')

    return render_template('signup.html', email=email)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    user_id = User.query.filter_by(email=session['email']).first()
    if request.method == 'POST':
        new_post_title = request.form['title']
        new_post_body = request.form['body']
        new_post = Blog(new_post_title, new_post_body, user_id)

        if new_post_title == "" or new_post_body == "":
            flash("You've left a mandatory field blank. Please fill in both fields to post your entry", 'error')
            return render_template('newpost.html', title="BLOGZ!", new_post_title=new_post_title, new_post_body=new_post_body)
        else:    

            db.session.add(new_post)
            db.session.commit()
            db.session.refresh(new_post)
            url = '/blogs?id=' + str(new_post.id) #+ the user id stuff
            return redirect(url)

    return render_template('newpost.html',title="BLOGZ!")


@app.route('/blogs', methods=['GET'])
def blogs():
    all_blog_posts = []
    user_view = ''
    email = ''
    if request.args:
        id = request.args.get('id')
        email = request.args.get('user')
        if id:
            all_blog_posts.append(Blog.query.get(id))
            user_view = 'individual'
        elif email:
            owner = User.query.filter_by(email=email).first()
            all_blog_posts = Blog.query.filter_by(owner=owner).all()
    else:
        all_blog_posts = Blog.query.all()
    return render_template('blogs.html', title='BLOGZ!', posts=all_blog_posts, user_view=user_view)

@app.route('/logout')
def logout():
    del session['email']
    flash('Logged Out')
    return redirect('/')

if __name__ == '__main__':            
    app.run()