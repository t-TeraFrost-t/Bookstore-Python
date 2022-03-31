from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField,DateField,HiddenField, DecimalField, IntegerField,TextAreaField, SelectField
from wtforms.validators import DataRequired,Optional ,Length, Email, EqualTo
from flask_wtf.file import FileField, FileAllowed

class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email/Username',validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class SearchForm(FlaskForm):
    search = StringField('Search',validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Search')

class GenerForm(FlaskForm):
    id = HiddenField("Hiden")
    name = StringField('Name',validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Add')

class BookForm(FlaskForm):
    isbn = StringField("Isbn",validators=[DataRequired(), Length(min=2,max=20)])
    name = StringField('Name',validators=[DataRequired(), Length(min=2)])
    autor = StringField('Autor',validators=[DataRequired(), Length(min=2)])
    price = DecimalField('Price',places = 2,validators=[DataRequired()])
    cover = FileField('Cover',validators=[FileAllowed(['jpg', 'png'])])
    amount = IntegerField('Amount',validators=[DataRequired()])
    description = TextAreaField('Description',validators=[])
    discount = DecimalField('Discount',default=0)
    gener = SelectField('Gener' , choices = [],coerce=int,validators=[DataRequired()])
    currency = SelectField('Currency', choices = [], coerce=int ,validators=[DataRequired()])    
    submit = SubmitField('Add')

class StaffForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Add Staff')

class UsernameUpdate(FlaskForm):
    username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    submit = SubmitField('Update Name/Email')

class PasswordUpdate(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update Password')

class ReportForm(FlaskForm):
    toDate =  DateField('To Date', description = 'To Date',validators=[Optional()])
    fromDate =  DateField('From Date', description = 'From Date',validators=[Optional()])
    user = StringField('Username',validators=[Optional()])
    userShow = SelectField('User' , choices=[('False', 'Hide'),('True', 'Show')],validators=[Optional()])
    status = SelectField('Status',choices=[],validators=[Optional()])
    statusShow = SelectField('Status' , choices=[('False', 'Hide'),('True', 'Show')],validators=[Optional()])
    paymentType = SelectField('Payment Type',choices=[],validators=[Optional()])
    paymentTypeShow = SelectField('Payment Type' , choices=[('False', 'Hide'),('True', 'Show')],validators=[Optional()])
    period = SelectField('Period' , choices=[('none', 'None'),('MM-DD', 'Day'),('IW','Weak'),('MM','Month'),(' ','Year')],validators=[Optional()])
    tocsv = SubmitField('Export')
    exportType = SelectField('Status' , choices=[('csv', 'CSV'),('xlsx', 'XLSX'),],validators=[Optional()])
    submit = SubmitField('Generate')
    
class RoleUpdate(FlaskForm):
    name = StringField('Email/Username',validators=[DataRequired()])
    submit = SubmitField('Add')

class AuditForm(FlaskForm):
    toDate =  DateField('To Date', description = 'To Date',validators=[Optional()])
    fromDate =  DateField('From Date', description = 'From Date',validators=[Optional()])
    name = StringField('Username',validators=[Optional()])
    submit = SubmitField('Generate')
