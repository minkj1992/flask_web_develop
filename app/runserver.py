import os
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess secret key'  # 전역적으로 사용하는 secret key
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

csrf = CSRFProtect(app)  # wtf에서 제공하는 FlaskForm을 사용하지 않을 경우 global하게 csrf 보호
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    # User 모델에 role 속성을 추가, 관계의 반대 방향을 정의, Role 모델이 외래키 대신 오브젝트에 접근하도록 role_id 대신 사용
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500


def is_name_already_taken(name):
    return session['name'] == name


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()  # when DI? proxy
    if form.validate_on_submit():  # return bool(request) and request.method in SUBMIT_METHODS

        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            session['name'] = form.name.data
        else:
            session['known'] = True
            if is_name_already_taken(form.name.data):
                flash('You typed same name as before', category="warning")
            else:
                flash('Your name is successfully changed', category="success")
                session['name'] = form.name.data

        return redirect(url_for('index'))  # Post/Redirect/Get (PRG) pattern
    return render_template('index.html', form=form,
                           name=session.get('name', False),
                           known=session.get('known', False))
