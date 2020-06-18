from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess secret key'  # 전역적으로 사용하는 secret key

csrf = CSRFProtect(app)  # wtf에서 제공하는 FlaskForm을 사용하지 않을 경우 global하게 csrf 보호
bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()  # when DI? proxy
    if form.validate_on_submit():  # return bool(request) and request.method in SUBMIT_METHODS
        legacy_name = session.get('name')
        if legacy_name != form.name.data:
            flash('Your name is changed', category="success")
            session['name'] = form.name.data
        else:
            flash('Looks like you already have that name!', category="warning")
        return redirect(url_for('index')) # Post/Redirect/Get (PRG) pattern
    return render_template('index.html', form=form, name=session.get('name')) # .get()은 찾을 수 없는 경우 None을 return하여 Error 방지
