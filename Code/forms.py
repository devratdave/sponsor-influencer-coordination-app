from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, BooleanField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, EqualTo, Length, Email, NumberRange, Optional
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_login import current_user
from models import Campaign


industries= ['Clothing Industry', 'FnB Industry', 'Technological Industry', 'Handloom Industry', 
			'Furniture Industry', 'Education Industry', 'Automobile Industry']
# Create A Search Form
class SearchForm(FlaskForm):
	searched = StringField("Searched", validators=[DataRequired()])
	submit = SubmitField("Submit")

# Create Login Form
class LoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Submit")

# Create a Sponsor User Form
class SponsorUserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	username = StringField("Username", validators=[DataRequired()])
	industry = SelectField('Type of Industry', choices=industries)
	about_me = StringField("About Me", validators=[Optional()])
	password = PasswordField('Password', validators=[DataRequired(), Length(8, message='Password should be atleast 8 characters')])
	password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords Must Match!')])
	submit = SubmitField("Submit")

# Create a Influencer User Form
class InfluencerUserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	username = StringField("Username", validators=[DataRequired()])
	about_me = StringField("About Me", validators=[Optional()])
	platforms= SelectMultipleField('Platforms', choices=[('Instagram', 'Instagram'), ('Facebook', 'Facebook'), ('Youtube', 'Youtube'), ('Twitter', 'Twitter'), ('Reddit', 'Reddit'), ('LinkedIn', 'LinkedIn'), ('Snapchat', 'Snapchat'), ('Thread', 'Thread')])
	password = PasswordField('Password', validators=[DataRequired(), Length(8, message='Password should be atleast 8 characters')])
	password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords Must Match!')])
	submit = SubmitField("Submit")

#Create a Campaign Form
class CampaignForm(FlaskForm):
	name= StringField('Campaign Name', validators=[DataRequired()])
	budget= IntegerField('Budget per Influencer', validators=[DataRequired(), NumberRange(0)])
	description= StringField('Campaign Description', validators=[Optional()])
	influencers_required= IntegerField('Influencer Required', validators=[DataRequired(), NumberRange(0)])
	private= BooleanField('Private Campaign', default=False, validators=[Optional()])
	submit = SubmitField("Submit")

#Create a Follower Form
class FollowersForm(FlaskForm):
	about_me= StringField('About Me', validators=[Optional()])
	Instagram= IntegerField('Instagram', validators=[NumberRange(0), Optional()])
	Facebook= IntegerField('Facebook', validators=[NumberRange(0), Optional()])
	Youtube= IntegerField('Youtube', validators=[NumberRange(0), Optional()])
	Twitter= IntegerField('Twitter', validators=[NumberRange(0), Optional()])
	Linkedin= IntegerField('LinkedIn', validators=[NumberRange(0), Optional()])
	Reddit= IntegerField('Reddit', validators=[NumberRange(0), Optional()])
	update = SubmitField("Update")


class CampaignSelect(FlaskForm):
	choice= QuerySelectField('Campaign Selection', query_factory=lambda: Campaign.query.filter_by(sponsor=current_user.id, completed= False).all(), get_label='name')
	requirements = StringField('Requirements for this user', validators=[Optional()])
	invite= SubmitField('Invite Influencer')

class EditCampaignForm(FlaskForm):
	name= StringField('Campaign Name', validators=[Optional()])
	description= StringField('Campaign Description', validators=[Optional()])
	influencers_required= IntegerField('How many more influencers are required?', validators=[Optional()])
	budget= IntegerField('New Budget per Influencer', validators=[NumberRange(0), Optional()])
	private = SelectField('Type of Campaign', choices=['', ('Private'), ('Public')], default=None, validators=[Optional()])
	submit= SubmitField('Edit Campaign')
