import flask
from flask import Flask,render_template,request,session,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import datetime
import json
import os
import math
from werkzeug.utils import secure_filename


with open('config.json','r') as c:
    parameters=json.load(c)['parameters']


local_server=True
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = parameters['file_uploader_location']
app.secret_key = 'the random string'
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = parameters['gmail_user'],
    MAIL_PASSWORD=  parameters['gmail_password']
)
mail=Mail(app)
if local_server:

            app.config["SQLALCHEMY_DATABASE_URI"] = parameters["local_uri"]
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = parameters["production_uri"]
db = SQLAlchemy(app)

class Contacts(db.Model):
    S_No= db.Column(db.Integer, primary_key=True)
    Name= db.Column(db.String(20), nullable=False)
    Phone_no = db.Column(db.String(12), nullable=False)
    Email = db.Column(db.String(20),  nullable=False)
    Message = db.Column(db.String(150),  nullable=False)
    Date = db.Column(db.String(20),nullable=True)


class Posts(db.Model):
    s_no= db.Column(db.Integer, primary_key=True)
    Title= db.Column(db.String(20), nullable=False)
    Slug = db.Column(db.String(25), nullable=False)
    Content = db.Column(db.String(150),  nullable=False)
    Date = db.Column(db.String(20),nullable=True)
    tag_line= db.Column(db.String(150), nullable=False)


@app.route('/')
def home():
    flash("Welcome to the CodeDeltas website","primary")
    posts = Posts.query.filter_by().all()
    last=math.ceil(len(posts)/int(parameters['No_of_posts']))
    #[0:parameters['No_of_posts']]
    page=request.args.get('page')
    if(not str(page).isnumeric()):
        page=1
    page=int(page)
    posts = posts[(page - 1) * int(parameters['No_of_posts']):(page - 1) * int(parameters['No_of_posts']) + int(
            parameters['No_of_posts'])]
        # pagination logic
       # first page
    if (page==1):
        old="#"
        next="/?page="+ str(page+1)
    elif (page==last):
        old="/?page="+ str(page-1)
        next="#"
    else:
        old="/?page="+ str(page-1)
        next="/?page="+ str(page+1)




    return render_template('index.html',parameters=parameters,posts=posts,old=old,next=next)

@app.route('/aboutUs')
def about():
    return render_template('about.html' ,parameters=parameters)

@app.route('/login' , methods=['GET', 'POST'])
def log():
    if ("u_name" in session and session['u_name'] == parameters['admin_user']):
        posts = Posts.query.all()
        return render_template('dashboard.html',parameters=parameters, posts=posts)

    if request.method == "POST":
          user_name=request.form.get('u_name')
          pass_word=request.form.get('pass_code')
          if(user_name==parameters['admin_user'] and pass_word==parameters['admin_password']):
            # setting the session variable
            session['u_name'] = user_name
            posts=Posts.query.all()
            return render_template('dashboard.html', parameters=parameters,posts=posts)
          else:
              return redirect('/login')
    else:
        return render_template('login.html', parameters=parameters)

@app.route('/post/<string:post_slug>',methods=["GET"])
def post_fetch(post_slug):
    post=Posts.query.filter_by(Slug=post_slug).first()
    return render_template('post.html' ,parameters=parameters,post=post)

@app.route('/edit/<string:s_no>',methods=["GET","POST"])
def edit(s_no):
    if ("u_name" in session and session['u_name'] == parameters['admin_user']):
        if request.method=="POST":
            box_title=request.form.get('title')
            box_tag=request.form.get('tag')
            box_content=request.form.get('content')
            box_slug=request.form.get('slug')
            daTE=datetime.now()
            if s_no=='0':
                post=Posts(Title=box_title,Slug=box_slug,tag_line=box_tag,Content=box_content,Date=daTE)
                db.session.add(post)
                db.session.commit()

            else:
                post=Posts.query.filter_by(s_no=s_no).first()
                post.Title=box_title
                post.Slug=box_slug
                post.tag_line=box_tag
                post.Content=box_content
                post.Date=daTE
                db.session.commit()
                return redirect('/edit/'+s_no)
        post=Posts.query.filter_by(s_no=s_no).first()
        return render_template('edit.html',parameters=parameters,post=post,s_no=s_no)

@app.route('/upload', methods=["GET","POST"])
def upload():
    if ("u_name" in session and session['u_name'] == parameters['admin_user']):
         if request.method=="POST":
             f_1=request.files['file_1']
             f_1.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f_1.filename)))
             return "File Uploaded Successfully!"

@app.route('/logout')
def logout():

    session.pop('u_name')
    return render_template('/login.html',parameters=parameters)

@app.route("/delete/<string:s_no>" , methods=["GET","POST"])
def delete(s_no):
    if ("u_name" in session and session['u_name'] == parameters['admin_user']):
        post=Posts.query.filter_by(s_no=s_no).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/login")




@app.route('/contact', methods=["GET","POST"])
def contact():
     if(request.method=="POST"):
        name=request.form.get("name")
        email=request.form.get("email")
        phone=request.form.get("phone")
        message=request.form.get("msg")

        entry=Contacts(Name=name, Phone_no=phone,Email=email,Message=message,Date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients=[parameters['gmail_user']],
                          body=message + "\n" + phone
                          )
        flash("Thanks for filling the form. We will get back to you soon","success")




     return render_template('contact.html',parameters=parameters)


app.run(debug=True)

