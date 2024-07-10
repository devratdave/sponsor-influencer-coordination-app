from app import db, app, login_manager
from flask_login import UserMixin
import datetime

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    __tablename__='users'
    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String, nullable= False)
    username= db.Column(db.String, nullable= False, unique= True)
    password= db.Column(db.String, nullable= False)
    type= db.Column(db.String, nullable= False, default='influencer')
    about_me = db.Column(db.String, nullable= True)
    flagged= db.Column(db.Boolean, default= False)
    sponsor= db.relationship('Sponsor', backref='user')
    influencer= db.relationship('Influencer', backref='user')

class Sponsor(db.Model):
    __tablename__: 'sponsor_info'
    id= db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer, db.ForeignKey(User.id))
    industry= db.Column(db.String)
    invitor= db.relationship('Sponsor_invites', backref='sponsor')

class Influencer(db.Model):
    __tablename__= 'influencer_info'
    id= db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer, db.ForeignKey(User.id))
    platform= db.Column(db.String, nullable= False)
    followers= db.Column(db.Integer, nullable= False, default=0)
    invitor= db.relationship('Influencer_invites', backref='influencer')
    invitee= db.relationship('Sponsor_invites', backref='influencer')

class Campaign(db.Model):
    __tablename__='campaigns'
    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String, nullable= False, unique=True)
    description= db.Column(db.String)
    sponsor= db.Column(db.Integer, db.ForeignKey(Sponsor.id))
    budget= db.Column(db.Integer, default=0)
    influencers_required= db.Column(db.Integer, default=1)
    influencers_acquired= db.Column(db.Integer, default=0)
    completed= db.Column(db.Boolean, default= False)
    flagged= db.Column(db.Boolean, default= False)
    private= db.Column(db.Boolean, default= False)
    creation_date= db.Column(db.DateTime, default= datetime.datetime.utcnow)
    influencer_invites= db.relationship('Influencer_invites', backref='campaign')
    sponsor_invites= db.relationship('Sponsor_invites', backref='campaign')

class Sponsor_invites(db.Model):
    __tablename__= 'sponsor_invites'
    id= db.Column(db.Integer, primary_key=True)
    campaign_id= db.Column(db.Integer, db.ForeignKey(Campaign.id))
    invitor_id= db.Column(db.Integer, db.ForeignKey(Sponsor.id))
    invitee_id= db.Column(db.Integer, db.ForeignKey(Influencer.id))
    negotiation_amount= db.Column(db.Integer, nullable=True)
    requirements= db.Column(db.String, nullable= True)
    accepted= db.Column(db.Boolean, default= False)
    rejected= db.Column(db.Boolean, default= False)
    negotiated= db.Column(db.Boolean, default=False)
    created= db.Column(db.DateTime, default= datetime.datetime.utcnow)

class Influencer_invites(db.Model):
    __tablename__='influencer_invites'
    id= db.Column(db.Integer, primary_key=True)
    campaign_id= db.Column(db.Integer, db.ForeignKey(Campaign.id))
    invitor_id= db.Column(db.Integer, db.ForeignKey(Influencer.id))
    offer= db.Column(db.Integer, default= 0)
    created= db.Column(db.DateTime, default= datetime.datetime.utcnow)
    accepted= db.Column(db.Boolean, default= False)
    responded= db.Column(db.Boolean, default= False)

with app.app_context():
    db.create_all()
    admin_exists= User.query.filter_by().first()
    if admin_exists:
        if admin_exists.username == 'admin@store':
            pass
    else:
        user= User(name= "Store Admin", username= "admin@store",
            password="admin@store", type="admin")
        user2= User(name= "Devrat Dave", username= "devratdave",
                          password= "devratdave", type= "Influencer", about_me= "I am a 22 year old influencer with a fluency in english and hindi. I have prior sponsorship experience.")
        user3= User(name= "Abhi Dave", username= "abhidave",
                          password= "abhidave", type= "Influencer", about_me= "I am a 20 year old influencer with a fluency in odinvs and pfivnf. I have prior sponsorship experience.")
        user4= User(name= "Sponsor Agency", username= "sponsoragency",
                    password="sponsoragency", type= "Sponsor", about_me= "We are a... company with 30 years in the industry")
        user5= User(name= "Sponsor Agency 2", username= "sponsoragency2",
                    password="sponsoragency2", type= "Sponsor", about_me= "We are a oufbvpivnpwcnpomcps company with 30 years in the industry")
        db.session.add(user)
        db.session.add(user2)
        db.session.add(user3)
        db.session.add(user4)
        db.session.add(user5)
        db.session.commit()
        influencer1_1= Influencer(user_id= user2.id, platform="Instagram", followers=10000)
        influencer1_2= Influencer(user_id= user2.id, platform="Facebook", followers=15000)
        influencer2_1= Influencer(user_id= user3.id, platform="Youtube", followers=2000)
        influencer2_2= Influencer(user_id= user3.id, platform="Twitter", followers=7000)
        sponsor1= Sponsor(user_id= user4.id, industry="Clothing Industry")
        sponsor2= Sponsor(user_id= user5.id, industry="FnB Industry")
        db.session.add(influencer1_1)
        db.session.add(influencer1_2)
        db.session.add(influencer2_1)
        db.session.add(influencer2_2)
        db.session.add(sponsor1)
        db.session.add(sponsor2)
        campaign1_1= Campaign(name= "Bedsheet Promotion", description="You will need to promote bedsheets for us.",
                            sponsor=user4.id, budget=2000, influencers_required=1)
        campaign1_2= Campaign(name= "Tshirt Promotion", description="You will need to promote tshirts for us.",
                            sponsor=user4.id, budget=3000, influencers_required=1)
        campaign2_1= Campaign(name= "Restaurant Promotion", description="You will need to promote our restuarant.",
                            sponsor=user5.id, budget=5000, influencers_required=1) 
        db.session.add(campaign1_1)
        db.session.add(campaign1_2)
        db.session.add(campaign2_1)
        db.session.commit()
