from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField
from wtforms.validators import DataRequired, Length

# Feeds class stores the details and appends day to day informations and feeds.
class feeds:
    def __init__(self,feedTitle,summary,time,imageUrl,category,author,link,dispTime,logo):
        self.feedTitle=feedTitle
        self.summary=summary
        self.time=time
        self.imageUrl=imageUrl
        self.category=category
        self.author=author
        self.link=link
        self.dispTime=dispTime
        self.logo=logo

class ContactForm(FlaskForm):
    name = StringField('Name', [
        DataRequired()])
    email = StringField('Email', [
        # Email(message=('Not a valid email address.')),
        DataRequired()])
    password = TextField('Message', [
        DataRequired(),
        Length(min=4, message=('Your message is too short.'))])
    submit = SubmitField('Submit')