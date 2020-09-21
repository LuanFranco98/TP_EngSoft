from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db, bcrypt
from flaskblog.models import User, Post, Dataset
from flaskblog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
                            AddDatabaseForm, Graph_Creation_Form)
from flaskblog.users.utils import save_picture , save_dataset

import plotly.express as px
import pandas as pd

users = Blueprint('users', __name__)



@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('users.login'))

    return render_template('register.html', title= 'Register', form=form )


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email= form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful.Please check email and password.','danger')

    return render_template('login.html', title= 'Login',form= form )

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))



@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
            
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!','success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    database = Dataset.query.filter_by(owner=current_user).all()


    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form, database=database)

@users.route("/add_database", methods=['GET', 'POST'])
@login_required
def add_database(): 
    form = AddDatabaseForm()
    if form.validate_on_submit():
        if form.dataset.data:
            dataset_file = save_dataset(form.dataset.data)
            dataset = Dataset(dataset_file=dataset_file,owner=current_user)
            db.session.add(dataset)
            db.session.commit()
            flash('You dataset has been uploded!','success')
        return redirect(url_for('users.add_database'))

    return render_template('add_database.html', title='Add Database', form=form)    


@users.route("/data_visualization", methods=['GET', 'POST'])
@login_required
def data_visualization():
    database = Dataset.query.filter_by(owner=current_user).all()
    if len(database) == 0:
        flash('You need to add a database first!', 'danger')
        return redirect(url_for('users.add_database'))

    #kinda dumb way of making sure everithing is alright
    ok = True

    class Graph_info:
        def __init__(self, graph_type,column_name, x_values, column2_name, y_values):
            self.graph_type = graph_type

            self.x_column_name = column_name
            self.x_values = x_values

            self.y_column_name = column2_name
            self.y_values = y_values

    graph_type = X_dataset_name= X_column_name = Y_dataset_name = Y_column_name = ''
    
    # form for graph X axis
    
    form = Graph_Creation_Form()
    
    graph_type = str(form.graph_type.data)
    dataset_X_name = str(form.dataset_X_name.data)
    column_X_name = str(form.column_X_name.data)
    dataset_Y_name = str(form.dataset_Y_name.data)
    column_Y_name = str(form.column_Y_name.data)
    
    #checking if infos are correct to avoid errors
    df_X = None
    df_Y = None

    if graph_type not in ['BAR', 'LINE']:
        print('funciona porra')
        ok = False

    if ok and ((dataset_X_name or dataset_Y_name) not in database):
        print('caralhooooooo')
        ok = False
    else:
        try:
            df_X = pd.read_csv(dataset_X_name)
        except:
            print('bbbbbbbbbbbbbbbbb')
            pass

        try:
            df_Y = pd.read_csv(dataset_Y_name)
        except:
            print('aaaaaaaaaaaaaaaaaaa')
            pass

    
    if ok:
        if column_X_name not in df_X.columns.columns.tolist():
            ok = False
            print('buceta ')
        else:
            try:
                df_X = df_X[column_X_name].tolist()
            except:
                print('disgraca pelada ')
                pass

        if column_Y_name not in df_Y.columns.tolist():
            ok = False
            print('cabeca de porco ')
        else:
            try:
                df_Y = df_Y[column_Y_name].tolist()
            except:
                print('cu de apertar linguica ')
                pass
    
    if ok and (df_Y is not None) and (df_X is not None):
        graph_info = Graph_info(graph_type, column_X_name, df_X, column_Y_name, df_Y)
        render_template('graphs.html', title='Data Visualization', graph_info=graph_info)
    else:
        flash("Something didn't go as planned, please double-check your data",'danger')
    
    return render_template('data_visualization.html', title='Data Visualization', form = form)

    

   