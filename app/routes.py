from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import *
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse

import pandas as pd
import app.lib.network_viz as nv


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('index'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('explorer'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/explorer', methods=['GET', 'POST'])
@login_required
def explorer():
    form = UploadForm()
    if request.method == 'POST' and form.validate_on_submit():
        data_file = request.files['data_file']
        if data_file:
            df = pd.read_csv(data_file)
            script, div = nv.visualize(df, 'Strategy')
        return render_template('explorer.html', bokeh_script=script, bokeh_div=div)
    return render_template('uploader.html', form=form)