from app import app, db
from flask import render_template, redirect, url_for, flash, request
from forms import industries, SponsorUserForm, InfluencerUserForm, EditCampaignForm, LoginForm, CampaignSelect, SearchForm, CampaignForm, FollowersForm
from models import User, Sponsor, Influencer, Sponsor_invites, Influencer_invites, Campaign
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import desc
import datetime

@app.context_processor
def base():
    form= SearchForm()
    return dict(form=form)

## Sposnor Signup Route
@app.route('/sponsor_signup', methods=['GET', 'POST'])
def sponsor_signup():
    form= SponsorUserForm()
    if form.validate_on_submit():
        ## Validates if other users exist with the same username, email
        username_verification= User.query.filter_by(username= form.username.data).first()
        if username_verification:
                flash('This username is taken')
                return redirect(url_for('sponsor_signup'))
        
        ## Creates a user object and adds it into the database
        else:
            user= User(name= form.name.data, 
                    username= form.username.data,
                    password= form.password.data,
                    about_me= form.about_me.data,
                    type= 'Sponsor')
            
            db.session.add(user)
            
            user= User.query.filter_by(username=form.username.data).first()
            sponsor= Sponsor(
                user_id= user.id,
                industry= form.industry.data
            )
            db.session.add(sponsor)
            db.session.commit()
            
            flash('Account created succesfully')
            login_user(user)
            return redirect(url_for('sponsor_home'))

    return render_template('sponsor_signup.html', form=form)

## Influencer Signup Route
@app.route('/influencer_signup', methods=['GET', 'POST'])
def influencer_signup():
    form= InfluencerUserForm()
    if form.validate_on_submit():
        ## Validates if other users exist with the same username, email
        username_verification= User.query.filter_by(username= form.username.data).first()
        platform_list= form.platforms.data

        if username_verification:
                flash('This username is taken')
                return redirect(url_for('influencer_signup'))
        
        ## Creates a user object and adds it into the database
        else:
            user= User(name= form.name.data, 
                    username= form.username.data,
                    password= form.password.data,
                    about_me = form.about_me.data,
                    type= 'Influencer')
            
            db.session.add(user)
            
            user= User.query.filter_by(username=form.username.data).first()
            for data in platform_list:
                
                influencer= Influencer(
                    user_id= user.id,
                    platform= data
                )
                db.session.add(influencer)
            db.session.commit()
            flash('Account created succesfully')
            login_user(user)
            return redirect(url_for('influencer_home'))

    return render_template('influencer_signup.html', form=form)

## Login Route
@app.route('/', methods=['GET', 'POST'])
def login():
    form= LoginForm()
    if form.validate_on_submit():
        user= User.query.filter_by(username= form.username.data).first()
        if user:
            if user.password==form.password.data:
                if user.type =='admin':
                    login_user(user)
                    flash('Welcome Back Admin')
                    return redirect(url_for('admin_home'))
                elif user.type == 'Sponsor':
                    if user.flagged:
                        flash('You have been flagged by the admins due to inappropriate behaviour. You can not recieve any requests or send any invites until you get unflagged')
                    login_user(user)
                    flash('Welcome Back Sponsor')
                    return redirect(url_for('sponsor_home'))
                elif user.type == 'Influencer':
                    if user.flagged:
                        flash('You have been flagged by the admins due to inappropriate behaviour. You can not recieve any invites or send any requests until you get unflagged')
                    login_user(user)
                    flash('You\'ve succesfully logged in. Welcome!')
                    return redirect(url_for('influencer_home'))
            else:
                flash('You\'ve entered the wrong credentials, try again')
                return redirect(url_for('login'))
        else:
            flash('The user doesn\'t exist')
            return redirect(url_for('influencer_signup'))

    return render_template('login.html', form=form)


## Sponsor Home Route
@app.route('/sponsor_home', methods=['GET', 'POST'])
@login_required
def sponsor_home():
    if current_user.type == 'Sponsor':
        form= CampaignSelect()
        influencers= User.query.filter_by(type = "Influencer", flagged = False).all()
        influencer_platforms= Influencer.query.filter_by().all()
        influencer_id= request.form.get('view_influencer') 

        if influencer_id:
            return redirect(url_for('access_influencer', influencer_id=influencer_id))  

        return render_template('sponsor_home.html', influencers=influencers, influencer_platforms= influencer_platforms, form=form)
    else:
        logout_user()
        flash("You're not authorized to access this page, please login again")
        return redirect(url_for('login'))
        


##Influencer Home
@app.route('/influencer_home', methods = ['GET', 'POST'])
@login_required
def influencer_home():
    if current_user.type == "Influencer":
        
        campaigns = Campaign.query.filter_by(completed=False, flagged=False).order_by(desc(Campaign.creation_date)).all()
        sponsors= User.query.filter_by(type='Sponsor', flagged = False).all()
        sponsor_details= Sponsor.query.filter_by().all()
        if request.method=='POST':
            send_request= request.form.get('send_request')
            campaign_id= request.form.get('view_campaign')
            if campaign_id:
                return redirect(url_for('access_campaign', campaign_id=campaign_id))
            elif send_request:                
                invite_verification = Sponsor_invites.query.filter_by(campaign_id=send_request, invitee_id= current_user.id).first()
                request_verification = Influencer_invites.query.filter_by(invitor_id=current_user.id, campaign_id=send_request).first()

                if invite_verification:
                    flash("You have already been invited for this campaign by the sponsor, check your invites section for the invite.")
                    return redirect(url_for('influencer_invites'))
                if current_user.flagged == True:
                    flash('You can NOT send requests to campaigns as you have been flagged by the admins due to inappropriate behaviour.')
                    return redirect(url_for('influencer_home'))
                campaign= Campaign.query.filter_by(id=send_request).first()
                if campaign.flagged == True:
                    flash('Sorry, this campaign has been flagged by the admins and can NOT receive any new requests')
                if invite_verification:
                    flash("You have already been invited for this campaign by the sponsor, check your invites section for the invite.")
                    return redirect(url_for('influencer_invites'))
                elif(request_verification): 
                    flash("You have already sent a request for this campaign, check your requests section for the request.")
                    return redirect(url_for('influencer_requests'))
                else:
                    campaign= Campaign.query.filter_by(id=send_request).first()
                    influencer_request= Influencer_invites(campaign_id=send_request, invitor_id= current_user.id, offer=campaign.budget)
                    db.session.add(influencer_request)
                    db.session.commit()
                    flash("You have succesfully sent a request for this campaign, check your requests section for the request.")
                    return redirect(url_for('influencer_requests'))

        return render_template('influencer_home.html', campaigns=campaigns, sponsors=sponsors, sponsor_details=sponsor_details)
    else:
        logout_user()
        flash("You're not authorized to access this page, please login again")
        return redirect(url_for('login'))


##Influencer Profile
@app.route('/influencer_profile', methods=['GET', 'POST'])
@login_required
def influencer_profile():
    if current_user.type == 'Influencer':
        form= FollowersForm()
        sponsor_invites= Sponsor_invites.query.filter_by(invitee_id=current_user.id, accepted=True).order_by(desc(Sponsor_invites.created)).all()
        influencer_invites= Influencer_invites.query.filter_by(invitor_id=current_user.id, accepted=True).order_by(desc(Influencer_invites.created)).all()
        campaigns= Campaign.query.filter_by().all()
        platforms= Influencer.query.filter_by(user_id=current_user.id).all()
        if request.method == 'POST' or form.validate_on_submit():
            view_campaign= request.form.get('view_campaign')

            if view_campaign:
                return redirect(url_for('access_campaign', campaign_id=view_campaign))
            if form.about_me.data:
                current_user.about_me = form.about_me.data
            for platform in platforms:
                previous_data= platform.followers
                if platform.platform =='Instagram':  
                    platform.followers = form.Instagram.data or previous_data
                elif platform.platform =='Facebook':
                    platform.followers = form.Facebook.data or previous_data
                elif platform.platform =='Youtube':                
                    platform.followers = form.Youtube.data or previous_data
                elif platform.platform =='Twitter':
                    platform.followers = form.Twitter.data or previous_data
                elif platform.platform =='Linkedin':
                    platform.followers = form.Linkedin.data or previous_data
                elif platform.platform =='Reddit':                
                    platform.followers = form.Reddit.data or previous_data
                elif platform.platform =='Snapchat':                
                    platform.followers = form.Reddit.data or previous_data
                elif platform.platform =='Thread':                
                    platform.followers = form.Reddit.data or previous_data
                platform.platform
            db.session.commit()
            flash('Profile updated succesfully.')
            return redirect(url_for('influencer_profile'))
        return render_template('influencer_profile.html', platforms=platforms, form=form, sponsor_invites=sponsor_invites, influencer_invites=influencer_invites, campaigns=campaigns)
    else:
        logout_user()
        flash("You're not authorized to access this page, please login again")
        return redirect(url_for('login'))
    

##Sponsor Profile
@app.route('/sponsor_profile', methods=['GET', 'POST'])
@login_required
def sponsor_profile():
    if current_user.type == 'Sponsor':
        campaigns= Campaign.query.filter_by(sponsor=current_user.id).order_by(desc(Campaign.creation_date)).all()
        sponsor_invites= Sponsor_invites.query.filter_by(invitor_id= current_user.id, accepted= True).all()
        influencer_invites= Influencer_invites.query.filter_by(responded= True, accepted= True).all()
        users= User.query.filter_by().all()
        if request.method == 'POST':
            campaign_id= request.form.get('view_campaign')
            return redirect(url_for('access_campaign', campaign_id=campaign_id))
        return render_template('sponsor_profile.html', campaigns=campaigns, sponsor_invites=sponsor_invites, influencer_invites=influencer_invites, users=users)
    else:
        logout_user()
        flash("You're not authorized to access this page, please login again")
        return redirect(url_for('login'))


## Create Campaigns route
@app.route('/create_campaign', methods= ['GET', 'POST'])
@login_required
def create_campaign():
    if current_user.type == 'Sponsor':
        form= CampaignForm()
        if form.validate_on_submit():
            if current_user.flagged == True:
                flash('You can NOT create any new campaigns because you have been flagged by the admins due to some inappropriate behaviour.')
                return redirect(url_for('sponsor_home'))
            campaign= Campaign(name= form.name.data,
                               budget= form.budget.data,
                               description= form.description.data,
                               influencers_required= form.influencers_required.data,
                               private= form.private.data,
                               sponsor= current_user.id)
            db.session.add(campaign)
            db.session.commit()
            return redirect(url_for('sponsor_home'))
        return render_template('create_campaign.html', form=form)
    else:
        logout_user()
        flash("You're not authorized to access this page, please login again")
        return redirect(url_for('login'))


## Influencer Requests
@app.route('/influencer_requests', methods=['GET', 'POST'])
@login_required
def influencer_requests():
    if current_user.type == 'Influencer':
        influencer_requests= Influencer_invites.query.filter_by(invitor_id=current_user.id).order_by(desc(Influencer_invites.created)).all()
        campaigns= Campaign.query.filter_by().all()
        if request.method == 'POST':
            campaign_id= request.form.get('view_campaign')
            return redirect(url_for('access_campaign', campaign_id=campaign_id))
        return render_template('influencer_requests.html', campaigns=campaigns, influencer_requests=influencer_requests)
    else:
        logout_user()
        flash("You're not authorized to access this page, please login again")
        return redirect(url_for('login'))


## Influencer Invites
@app.route('/influencer_invites', methods= ['GET', 'POST'])
@login_required
def influencer_invites():
    if current_user.type == 'Influencer':
        influencer_invites= Sponsor_invites.query.filter_by(invitee_id=current_user.id).order_by(desc(Sponsor_invites.created)).all()
        campaigns= Campaign.query.filter_by().all()
        if request.method == 'POST':
            invite_accept= request.form.get('accept')
            invite_reject= request.form.get('reject')
            negotiation_amount= request.form.get('negotiation_amount')
            campaign_id= request.form.get('campaign_id')
            view_campaign = request.form.get('view_campaign')
            invite= Sponsor_invites.query.filter_by(invitee_id= current_user.id, campaign_id=invite_accept or invite_reject or campaign_id).first()
            campaign= Campaign.query.filter_by(id= invite_accept or invite_reject).first()
            if view_campaign:
                return redirect(url_for('access_campaign', campaign_id=view_campaign))
            elif invite_accept:
                if campaign.influencers_required == campaign.influencers_acquired or campaign.completed:
                    flash('This campaign recruit has been completed')
                    return redirect(url_for('influencer_invites'))
                invite.accepted = True
                campaign.influencers_acquired += 1
                db.session.commit()
                if campaign.influencers_required == campaign.influencers_acquired:
                    campaign.completed = True
                    db.session.commit()
                    flash('You have succesfully accepted the invite. You are not part of the campaign.')
                    return redirect(url_for('influencer_invites'))
            elif invite_reject:
                flash('You have rejected this campaign invite.')
                invite.rejected= True
                
                db.session.commit()
            elif negotiation_amount:
                invite.negotiation_amount= negotiation_amount
                invite.negotiated = True
                
                db.session.commit()
                flash("You have sent the negotiation amount.")
                return redirect(url_for('influencer_home'))


        return render_template('influencer_invites.html', influencer_invites=influencer_invites, campaigns=campaigns)
    else:
        logout_user()
        flash("You're not authorized to access this page, please login again")
        return redirect(url_for('login'))


## Sponsor Invites
@app.route('/sponsor_invites', methods=['GET', 'POST'])
@login_required
def sponsor_invites():
    if current_user.type == 'Sponsor':
        sponsor_invites= Sponsor_invites.query.filter_by(invitor_id=current_user.id).order_by(desc(Sponsor_invites.created)).all()
        campaigns= Campaign.query.filter_by(sponsor=current_user.id).order_by(desc(Campaign.creation_date)).all()
        users= User.query.filter_by().all()
        influencer_platforms= Influencer.query.filter_by().all()
        if request.method=='POST':
            influencer_id= request.form.get('view_influencer')
            invite_accept= request.form.get('accept')
            invite_reject= request.form.get('reject')
            invite_delete = request.form.get('delete_id')
            campaign_id= request.form.get('campaign_id')
            campaign= Campaign.query.filter_by(id = campaign_id).first()
            invite= Sponsor_invites.query.filter_by(campaign_id = campaign_id, invitee_id = invite_accept or invite_reject or invite_delete).first()
            if invite_delete:
                db.session.delete(invite)
                db.session.commit()
                flash("This invite has been succesfully deleted.")
                return redirect(url_for('sponsor_invites'))
            if influencer_id:
                return redirect(url_for('access_influencer', influencer_id=influencer_id))
            elif invite_accept:
                if campaign.completed:
                    invite.rejected= True
                    db.session.commit()
                    flash("The campaign has already been completed.")
                elif campaign.influencers_required == campaign.influencers_acquired:
                    campaign.completed= True
                    invite.rejected = True
                    db.session.commit()
                    flash("The influencers required for this campaign has been completed. Please check your profile.")
                    return redirect(url_for('sponsor_invites'))
                invite.accepted = True
                campaign.influencers_acquired += 1
                db.session.commit()
                if campaign.influencers_acquired == campaign.influencers_required:
                    campaign.completed = True
                    db.session.commit()
                    flash("The number of influencers required for this campaign is now complete.")
                    return redirect(url_for('sponsor_profile'))
                flash("Sponsor invite successfully accepted.")
                return redirect(url_for('sponsor_invites'))
            elif invite_reject:
                invite.rejected = True
                db.session.commit()
                flash("The sponsor invite has been rejected.")
                return redirect(url_for('sponsor_invites'))
        return render_template('sponsor_invites.html', sponsor_invites=sponsor_invites, influencer_platforms=influencer_platforms, campaigns=campaigns, users=users)
        
    else:
        logout_user()
        flash("You're not authorized to access this page, please login again")
        return redirect(url_for('login'))
    

## Accessing campaign requests
@app.route('/sponsor_requests', methods=['GET', 'POST'])
@login_required
def sponsor_requests():
    if current_user.type == 'Sponsor':
        sponsor_requests= Influencer_invites.query.filter_by().order_by(desc(Influencer_invites.created)).all()
        campaigns= Campaign.query.filter_by(sponsor=current_user.id).order_by(desc(Campaign.creation_date)).all()
        influencer_platforms= Influencer.query.filter_by().all()
        users= User.query.filter_by().all()
        if request.method=='POST':
            influencer_id= request.form.get('view_influencer')
            campaign_id= request.form.get('campaign_id')
            invite_accept= request.form.get('accept')
            invite_reject= request.form.get('reject')
            invite= Influencer_invites.query.filter_by(campaign_id=campaign_id, invitor_id=invite_accept or invite_reject).first()
            campaign= Campaign.query.filter_by(id= campaign_id).first()
            if influencer_id:
                return redirect(url_for('access_influencer', influencer_id=influencer_id))
            elif invite_accept:
                if campaign.influencers_required == campaign.influencers_acquired:
                    campaign.completed = True
                    db.session.commit()
                    flash('This campaign has already been completed')
                    return redirect(url_for('sponsor_requests'))
                invite.accepted = True
                invite.responded = True
                invite.offer = campaign.budget
                campaign.influencers_acquired += 1
                db.session.commit()
                if campaign.influencers_required == campaign.influencers_acquired:
                    campaign.completed = True
                    db.session.commit()
                    flash('Influencer recruited for the campaign, this campaign has been completed.')
                    return redirect(url_for('sponsor_requests'))
                flash('Influencer has been recruited for this campaign.')
                return redirect(url_for('sponsor_requests'))
            elif invite_reject:
                invite.responded= True
                db.session.commit()
                flash('You rejected the request for this campaign')
                return redirect(url_for('sponsor_requests'))
            
        return render_template('sponsor_requests.html', sponsor_requests=sponsor_requests, campaigns=campaigns, users=users, influencer_platforms=influencer_platforms)
        
    else:
        logout_user()
        flash("You're not authorized to access this page, please login again")
        return redirect(url_for('login'))


## Accessing individual campaigns
@app.route('/campaigns/<int:campaign_id>', methods= ['GET', 'POST'])
@login_required
def access_campaign(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first()
    sponsor_invite = Sponsor_invites.query.filter_by(campaign_id = campaign.id, invitee_id = current_user.id, rejected = False).first()
    influencer_invite = Influencer_invites.query.filter_by(invitor_id = current_user.id, campaign_id = campaign_id).first()
    if current_user.type == 'admin' or campaign.private == False or (campaign.private == True and campaign.sponsor == current_user.id) or sponsor_invite or influencer_invite:
        sponsor= User.query.filter_by(id= campaign.sponsor).first()

        if request.method == 'POST':
            flag_campaign= request.form.get('flag')
            unflag_campaign= request.form.get('unflag')
            if flag_campaign:
                campaign= Campaign.query.filter_by(id=flag_campaign).first()
                campaign.flagged = True
                db.session.commit()
                flash('Campaign flagged succesfully')
                return redirect(url_for('admin_sponsors'))
            if unflag_campaign:
                campaign= Campaign.query.filter_by(id=unflag_campaign).first()
                campaign.flagged = False
                db.session.commit()
                flash('Campaign Unflagged succesfully')
                return redirect(url_for('admin_sponsors'))
            send_request= request.form.get('send_request')
            edit_campaign= request.form.get('edit_campaign')
            delete_campaign= request.form.get('delete_campaign')
            invite_verification = Sponsor_invites.query.filter_by(campaign_id=send_request, invitee_id= current_user.id).first()
            request_verification = Influencer_invites.query.filter_by(invitor_id=current_user.id, campaign_id=send_request).first()
            if send_request:
                if current_user.flagged == True:
                    flash('You can NOT send requests to campaigns as you have been flagged by the admins due to inappropriate behaviour.')
                    return redirect(url_for('influencer_home'))
                if campaign.flagged == True:
                    flash('You can NOT send requests to campaigns as this campaign has been flagged by the admins due to some inappropriate behaviour.')
                    return redirect(url_for('influencer_home'))
                if invite_verification:
                    flash("You have already been invited for this campaign by the sponsor, check your invites section for the invite.")
                    return redirect(url_for('influencer_invites'))
                if(request_verification): 
                    flash("You have already sent a request for this campaign, check your requests section for the request.")
                    return redirect(url_for('influencer_requests'))
                influencer_request= Influencer_invites(campaign_id=send_request, invitor_id= current_user.id, offer=campaign.budget)
                db.session.add(influencer_request)
                db.session.commit()
                flash("You have succesfully sent a request for this campaign, check your requests section for the request.")
                return redirect(url_for('influencer_requests'))
            elif delete_campaign:
                campaign= Campaign.query.filter_by(id=delete_campaign).first()
                if campaign.sponsor == current_user.id:
                    sponsor_invites= Sponsor_invites.query.filter_by(campaign_id=delete_campaign).all()
                    influencer_invites= Influencer_invites.query.filter_by(campaign_id=delete_campaign).all()
                    for invite in sponsor_invites:
                        db.session.delete(invite)
                    for invite in influencer_invites:
                        db.session.delete(invite)
                    db.session.delete(campaign)
                    db.session.commit()
                    flash('This campaign along with all the invites and requests has been deleted succesfully.')
                    return redirect(url_for('sponsor_profile'))
                else:
                    flash('You are not authorized to delete other\'s campaigns.')
                    return redirect(url_for('sponsor_profile'))
            elif edit_campaign:
                campaign= Campaign.query.filter_by(id= edit_campaign).first()
                if campaign.sponsor == current_user.id:
                    return redirect(url_for('edit_campaign', campaign_id=campaign.id))
                else:
                    flash('You are not authorized to edit other\'s campaigns.')
                    return redirect(url_for('sponsor_profile'))
        return render_template('campaign.html', campaign=campaign, sponsor=sponsor)
    else:
        flash('This is a private campaign, you\'re not allowed to access it.')
        if current_user.type == 'Influencer':
            return redirect(url_for('influencer_home'))
        elif current_user.type == 'Sponsor':
            return(redirect(url_for('sponsor_home')))



## Editing individual campaigns
@app.route('/edit_campaign/<int:campaign_id>', methods= ['GET', 'POST'])
@login_required
def edit_campaign(campaign_id):
    if current_user.type == 'Sponsor':
        campaign= Campaign.query.filter_by(id=campaign_id, sponsor= current_user.id).first()
        form = EditCampaignForm()
        if campaign:
            if form.validate_on_submit:
                new_private= form.private.data
                new_name= form.name.data
                new_description= form.description.data
                new_budget= form.budget.data
                new_influencers_required = form.influencers_required.data
                if new_name:
                    campaign.name= new_name
                if new_description:
                    campaign.description = new_description
                if new_budget:
                    campaign.budget = new_budget
                if new_influencers_required:
                    campaign.influencers_required += new_influencers_required
                    if campaign.influencers_required < campaign.influencers_acquired:
                        flash('Influencers required can not be less than influencers acquired.')
                        return redirect(url_for('sponsor_profile'))
                    elif campaign.influencers_required == campaign.influencers_acquired:
                        campaign.completed = True
                    else:
                        campaign.completed= False
                if new_private:
                    if new_private == 'Private':
                        campaign.private = True
                    elif new_private == 'Public':
                        campaign.private = False
                db.session.commit()
                if new_budget or new_description or new_influencers_required or new_name or new_private:
                    flash('You\'ve succesfully edited the campaign')
                    return redirect(url_for('sponsor_profile'))
            return render_template('edit_campaign.html', form=form, campaign=campaign)
        else:
            flash('You are not authorized to edit other\'s campaigns.')
            return redirect(url_for('sponsor_profile'))


## Accessing individual influencers
@app.route('/influencers/<int:influencer_id>', methods= ['GET', 'POST'])
@login_required
def access_influencer(influencer_id):
    form= CampaignSelect()
    influencer= Influencer.query.filter_by(user_id=influencer_id).all()
    influencer_details= User.query.filter_by(id= influencer[0].user_id).first()
    if request.method== 'POST':
        flag_influencer = request.form.get('flag_influencer')
        unflag_influencer = request.form.get('unflag_influencer')
        print(f'flagged{flag_influencer}')
        print(f'unflagged{unflag_influencer}')
        if current_user.flagged == True:
                    flash('You can NOT send invites to campaigns as you have been flagged by the admins due to inappropriate behaviour.')
                    return redirect(url_for('sponsor_home'))
        if flag_influencer:
                user= User.query.filter_by(id=flag_influencer).first()
                user.flagged = True
                db.session.commit()
                flash('This user has been flagged succesfully.')
                return redirect(url_for('admin_influencers'))
        elif unflag_influencer:
            user= User.query.filter_by(id=unflag_influencer).first()
            user.flagged = False
            db.session.commit()
            flash('This user has been Unflagged succesfully.')
            return redirect(url_for('admin_influencers'))
    
        elif form.validate_on_submit():
            if influencer_details.flagged == True:
                flash('You can NOT send invites to this influencer as they have been flagged by the admins due to inappropriate behaviour.')
                return redirect(url_for('sponsor_home'))
            campaign= form.choice.data
            requirements = form.requirements.data
            invite_verification= Sponsor_invites.query.filter_by(campaign_id= campaign.id, invitee_id= influencer_id).first()
            request_verification= Influencer_invites.query.filter_by(campaign_id= campaign.id, invitor_id= influencer_id).first()

            if campaign.completed:
                flash("This campaign is already complete, you cannot invite more influencers for the campaign.")
                return redirect(url_for('sponsor_home'))
            elif request_verification:
                if campaign.influencers_required == campaign.influencers_acquired:
                    campaign.completed = True
                    db.session.commit()
                    flash("This campaign has been completed you can not invite for this campaign anymore.")
                    return redirect(url_for('sponsor_profile'))
                campaign.influencers_acquired +=1
                if campaign.influencers_required == campaign.influencers_acquired:
                    campaign.completed = True
                    flash("This campaign has acquired the required number of influencers and is now complete.")
                request_verification.accepted= True
                request_verification.responded = True
                db.session.commit()
                flash("The person you just invited has already sent a request to join the campaign, so their campaign request has been accepted.")
                return redirect(url_for('sponsor_home'))
            elif invite_verification:
                flash('This influencer has already been invited for this campaign.')
                return redirect(url_for('sponsor_home'))
            invite = Sponsor_invites(campaign_id = campaign.id, invitor_id= current_user.id, invitee_id= influencer_id, requirements=requirements, negotiation_amount=campaign.budget)
            db.session.add(invite)
            db.session.commit()
            flash('This influencer has been invited')
            return redirect(url_for('sponsor_home'))

    return render_template('influencer.html', influencer=influencer, influencer_details=influencer_details, form=form)


## Logs out the user/admin
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
	logout_user()
	flash("You Have Been Logged Out!  Thanks For Stopping By...")
	return redirect(url_for('login'))


## Searchbar for searching products based on their name or category-name.
@app.route('/search', methods=['POST'])
@login_required
def search():
    form= SearchForm()
    if form.validate_on_submit:
        searched= form.searched.data
        campaign_searched = Campaign.query.filter(Campaign.name.like(f'%{searched}%'), Campaign.flagged == False).all()
        sponsors = User.query.filter_by(type = 'Sponsor', flagged = False).all()
        influencers = User.query.filter(User.name.like(f'%{searched}%'), User.type == 'Influencer', User.flagged == False).all()
        influencer_platforms= Influencer.query.filter_by().all()

        campaign_searched_admin = Campaign.query.filter(Campaign.name.like(f'%{searched}%')).all()
        sponsors_admin = User.query.filter_by(type = 'Sponsor').all()
        influencers_admin = User.query.filter(User.name.like(f'%{searched}%'), User.type == 'Influencer').all()
        influencer_platforms_admin= Influencer.query.filter_by().all()
        return render_template('searched_results.html', form=form, searched=searched,
                               campaign_searched=campaign_searched, sponsors=sponsors, influencers=influencers, 
                               influencer_platforms= influencer_platforms, campaign_searched_admin=campaign_searched_admin, 
                               sponsors_admin=sponsors_admin, influencers_admin=influencers_admin, 
                               influencer_platforms_admin=influencer_platforms_admin)
    
@app.route('/admin_home', methods=['GET', 'POST'])
@login_required
def admin_home():
    if current_user.type == 'admin':
        sponsors= User.query.filter_by(type='Sponsor', flagged=False).all()

        users_in_industry= []
        campaigns_in_industry= []
        for industry in industries:
            count = 0
            for sponsor in sponsors:
                sponsor_in_industry= Sponsor.query.filter_by(user_id= sponsor.id, industry=industry).first()
                if sponsor_in_industry:
                    count += 1
            users_in_industry.append(count)

        for industry in industries:
            campaign_count = 0
            for sponsor in sponsors:
                sponsor_in_industry= Sponsor.query.filter_by(user_id= sponsor.id, industry=industry).first()
                if sponsor_in_industry:
                    campaigns= Campaign.query.filter_by(sponsor=sponsor.id, completed=False, flagged=False).count()
                    campaign_count += campaigns
            campaigns_in_industry.append(campaign_count)
        
        return render_template('admin_home.html', industries=industries, users_in_industry=users_in_industry, campaigns_in_industry=campaigns_in_industry)
    else:
        flash("You\'re not authorized to enter this page.")
        logout_user()
        return redirect(url_for('login'))
    

@app.route('/admin_sponsors', methods=['GET', 'POST'])
@login_required
def admin_sponsors():
    if current_user.type == 'admin':
        sponsors = User.query.filter_by(type='Sponsor').all()
        campaigns = Campaign.query.filter_by().order_by(desc(Campaign.creation_date)).all()
        sponsor_details= Sponsor.query.filter_by().all()
        campaign_id= request.form.get('view_campaign')
        flag_sponsor= request.form.get('flag_sponsor')
        unflag_sponsor= request.form.get('unflag_sponsor')
        if request.method == 'POST':
            if flag_sponsor:
               sponsor= User.query.filter_by(id=flag_sponsor).first()
               sponsor.flagged= True
               db.session.commit()
               flash('This sponsor has succesfully been flagged')
               return redirect(url_for('admin_sponsors'))
            if unflag_sponsor:
               sponsor= User.query.filter_by(id=unflag_sponsor).first()
               sponsor.flagged= False
               db.session.commit() 
               flash('This sponsor has succesfully been Unflagged')
               return redirect(url_for('admin_sponsors'))
            if campaign_id:
                return redirect(url_for('access_campaign', campaign_id=campaign_id))
        return render_template('admin_sponsors.html', sponsors=sponsors, campaigns=campaigns, sponsor_details= sponsor_details)
    else:
        flash("You\'re not authorized to enter this page.")
        logout_user()
        return redirect(url_for('login'))
    
    
@app.route('/admin_influencers', methods=['GET', 'POST'])
@login_required
def admin_influencers():
    if current_user.type == 'admin':
        influencers= User.query.filter_by(type= 'Influencer').all()
        influencer_platforms= Influencer.query.filter_by().all()
        influencer_id= request.form.get('view_influencer')
        if request.method == 'POST':
            if influencer_id:
                return redirect(url_for('access_influencer', influencer_id=influencer_id))
        return render_template('admin_influencers.html', influencers=influencers, influencer_platforms=influencer_platforms)
    else:
        flash("You\'re not authorized to enter this page.")
        logout_user()
        return redirect(url_for('login'))
    
