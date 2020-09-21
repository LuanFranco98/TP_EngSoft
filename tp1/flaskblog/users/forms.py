from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from flaskblog.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                        validators=[DataRequired(),Length(min=2,max=20)])

    email = StringField('Email', validators=[DataRequired(),Email()])

    password = PasswordField('Password', validators=[DataRequired()])

    confirmpassword = PasswordField('Confirm Password',
                            validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken.Please chose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already taken.Please chose a different one.')



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])

    password = PasswordField('Password', validators=[DataRequired()])

    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                        validators=[DataRequired(),Length(min=2,max=20)])

    email = StringField('Email', validators=[DataRequired(),Email()])

    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])
    
    submit = SubmitField('Update')

  
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is already taken.Please chose a different one.')
    
    
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is already taken.Please chose a different one.')

class AddDatabaseForm(FlaskForm):
    dataset = FileField('Add a new Dataset from your database.Note that we are only accepting .csv files and the separators must be commas.',validators=[FileAllowed(['csv'])])

    submit = SubmitField('Add Dataset')

class Graph_Creation_Form(FlaskForm):
    graph_type = StringField("Please inform us if you want a bar or a line chart.Write BAR for a bar plot or LINE for a line plot",validators=[DataRequired()])
    
    dataset_X_name = StringField("For the X AXIS, Please inform us the name of the file that contains the data you wan't to see", validators=[DataRequired()])

    column_X_name = StringField("In that file, which column contains the data of the X AXIS?", validators=[DataRequired()])
    
    dataset_Y_name = StringField("For the Y AXIS, Please inform us the name of the file that contains the data you wan't to see", validators=[DataRequired()])

    column_Y_name = StringField("In that file, which column contains the data of the Y AXIS?", validators=[DataRequired()])
    
    submit = SubmitField('Submit')



