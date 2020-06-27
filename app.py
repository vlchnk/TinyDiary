from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

# app.logger.info(username) - log

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tinydiary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = "acsdopm*SCm9a8scm283mc09C<u2m"


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_post = db.Column(db.String, nullable=True)
    title = db.Column(db.String(15), nullable=True)
    intro = db.Column(db.String(100), nullable=True)
    text = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String, unique=True, nullable=True)
    email = db.Column(db.String, unique=True, nullable=True)
    password = db.Column(db.String, nullable=True)
    status = db.Column(db.Boolean, default=False)
    session = db.Column(db.String, unique=True, nullable=True)

    def __repr__(self):
        return 'Article %r>' % self.id


@app.route('/')
def index():
    try:
        uid = Article.query.filter_by(session=session['uid']).first()
        if uid.status:
            return redirect(url_for('show_user_profile', user=uid.username))
        else:
            return render_template('index.html')
    except:
        return render_template('index.html')


@app.route('/error/<int:error>')
def error_func(error):
    app.logger.info(error)
    try:
        uid = Article.query.filter_by(session=session['uid']).first()
        if uid.status:
            return redirect(url_for('show_user_profile', user=uid.username))
        else:
            return render_template('index.html')
    except:
        if error == 1:
            app.logger.info(error)
            text_error = 'Email/Username has already been taken.'
            return render_template('index.html', error=text_error)
        elif error == 2:
            text_error = 'Your email or password were incorrect.'
            return render_template('index.html', error=text_error)
        else:
            text_error = "Sorry, we do not work."
            return render_template('index.html', error=text_error)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        session['uid'] = str(uuid.uuid4())
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        status = True
        session_user = session['uid']
        
        try: 
            article = Article(username=username, email=email, password=password, session=session_user, status=status)
            db.session.add(article)
            db.session.commit()
            return redirect(url_for('show_user_profile', user=username))
        except:
            error = 1
            return redirect('/error/1')
    else:
        # Show settings panel this user
        return redirect('/')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        session['uid'] = str(uuid.uuid4())
        username = request.form['username']
        password = request.form['password']
        status = True
        session_user = session['uid']
        
        article = Article.query.filter_by(username=username).first()
        try:
            if article.username == username and article.password == password:
                article.session = session_user
                article.status = True
                db.session.commit()
                return redirect(url_for('show_user_profile', user=username))
            else:
                return redirect('/error/2')
        except:
            return redirect('/error/2')
    else:
        # Show settings panel this user
        return redirect('/')


@app.route('/<string:user>')
def show_user_profile(user):
    try:
        uid = Article.query.filter_by(session=session['uid']).first()
        if uid.status and user == uid.username:
            article = Article.query.order_by(Article.date.desc()).filter_by(user_post=user).all() #rticle.query.order_by(Article.date.desc()).get(user) - выборка по юзернейму
            return render_template('posts.html', article=article, user=user)
        else:
            return redirect(url_for('index'))
    except:
        return redirect(url_for('index'))


@app.route('/<string:user>/settings', methods=['POST','GET'])
def show_user_settings(user):
    try:
        uid = Article.query.filter_by(session=session['uid']).first()
        if uid.status and request.method == 'POST':
            article = Article.query.filter_by(username=user).first()
            article.email = request.form['email']
            article.password = request.form['password']

            db.session.commit()
            return redirect(url_for('show_user_profile', user=user))
        elif uid.status and request.method == 'GET' and user == uid.username:
            article = Article.query.filter_by(username=user).first()
            # Show settings panel this user
            return render_template('settings.html', article=article, user=user)
        else:
            return redirect(url_for('index'))
    except:
        return redirect(url_for('index'))


@app.route('/<string:user>/create', methods=['POST', 'GET'])
def create_new_post(user):
    if request.method == 'POST':
        try:
            uid = Article.query.filter_by(session=session['uid']).first()
            if uid.status:
                title = request.form['title']
                intro = request.form['intro']
                text = request.form['text']

                article = Article(user_post=user, title=title, intro=intro, text=text)

                db.session.add(article)
                db.session.commit()
                return redirect(url_for('show_user_profile', user=user))
            else:
                return redirect(url_for('index'))
        except:
            return redirect('/')
    else:
        try:
            uid = Article.query.filter_by(session=session['uid']).first()
            app.logger.info('1')
            if uid.status and user == uid.username:
                app.logger.info('2')
                return render_template('create.html', user=user)
            else:
                app.logger.info('3')
                return redirect(url_for('index'))
        except:
            app.logger.info('4')
            return redirect('/')


@app.route('/<string:user>/<int:id>')
def show_post(user,id):
    try:
        uid = Article.query.filter_by(session=session['uid']).first()
        article = Article.query.filter_by(id=id).first()
        if uid.status and article.user_post == user and uid.username == user:
            article = Article.query.filter_by(id=id).first()
            return render_template('post.html', article=article, user=user)
        else:
            return redirect('/')
    except:
        return redirect("/")


@app.route('/<string:user>/<int:id>/del')
def del_post(user,id):
    try:
        uid = Article.query.filter_by(session=session['uid']).first()
        if uid.status and uid.username == user:
            article = Article.query.filter_by(id=id).first()
            db.session.delete(article)
            db.session.commit()
            return redirect(url_for('show_user_profile', user=user))
        else:
            return redirect('/')
    except:
        return redirect('/')

@app.route('/<string:user>/<int:id>/edit', methods=['POST', 'GET'])
def edit_post(user,id):
    try:
        uid = Article.query.filter_by(session=session['uid']).first()
        if uid.status and request.method == 'POST':
            article = Article.query.get(id)
            article.title = request.form['title']
            article.intro = request.form['intro']
            article.text = request.form['text']

            db.session.commit()
            return redirect(url_for('show_post', user=user, id=id))
        elif uid.status and request.method == 'GET' and uid.username == user:
            article = Article.query.get(id)
            # Show settings panel this user
            return render_template('edit.html', article=article, user=user)
        else:
            return redirect(url_for('index'))
    except:
        return redirect('/')


@app.route('/<string:user>/logout')
def user_logout(user):
    try:
        uid = Article.query.filter_by(session=session['uid']).first()
        if uid.status and uid.username == user:
            uid.query.update({'status': False})
            db.session.commit()
            return redirect(url_for('index'))
        else:
            return redirect('/')
    except:
        return redirect('/')


if __name__ == '__main__':
    app.run() #host='0.0.0.0'