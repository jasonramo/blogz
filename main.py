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

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/')
def index():
    return redirect('/blogs')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        new_post_title = request.form['title']
        new_post_body = request.form['body']
        new_post = Blog(new_post_title, new_post_body)

        if new_post_title == "" or new_post_body == "":
            flash("You've left a mandatory field blank. Please fill in both fields to post your entry", 'error')
            return render_template('newpost.html', title="Build A Blog", new_post_title=new_post_title, new_post_body=new_post_body)
        else:    

            db.session.add(new_post)
            db.session.commit()
            url = '/blogs?id=' + str(new_post.id)
            return redirect(url)

    return render_template('newpost.html',title="Build A Blog")


@app.route('/blogs', methods=['POST', 'GET'])
def blogs():
    individual_id = request.args.get('id')
    if (individual_id):
        post = Blog.query.get(individual_id)
        return render_template('individual.html', title='Build A Blog', post=post)
    else:
        all_posts = Blog.query.all()
        return render_template('blogs.html', title='Build A Blog', posts=all_posts)

if __name__ == '__main__':            
    app.run()