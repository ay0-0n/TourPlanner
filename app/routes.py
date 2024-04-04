from app import app, db
from flask import redirect, render_template, url_for, request, session, flash
from app.models import *
from flask_bcrypt import Bcrypt

@app.route('/')
@app.route('/home')
def index():
    return render_template("home.html")

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            user = User.query.filter_by(username=username).first()

            if user and bcrypt.check_password_hash(user.password, password):
                session["username"] = user.username
                if user.role_id == 0:
                    return redirect(url_for('tourist'))
                elif user.role_id == 1:
                    return redirect(url_for('hotelmanager'))
                elif user.role_id == 2:
                    return redirect(url_for('travelagent'))
            else:
                return render_template('login.html', error_message='Invalid username or password!')
        
        except:
            return render_template('login.html', error_message='Invalid username or password!')
        

    return render_template('login.html')





bcrypt = Bcrypt()

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone_number = request.form['phone_number']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        role_id = request.form['role_id']

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return render_template('signup.html', error_message='Username already exists!')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(first_name=first_name, last_name=last_name, phone_number=phone_number,
                        email=email, username=username, password=hashed_password, role_id=role_id)

        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please login to continue.')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/forgetpass', methods=['GET', 'POST'])
def forgetpass():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()

        if user:
            return redirect(url_for('login'))
        else:
            return render_template('forgetpass.html', error_message='Email not found, please try again!')
    return render_template('forgetpass.html')

@app.route('/tourist')
def tourist():
    return render_template('tourist.html')

@app.route('/hotelmanager')
def hotelmanager():
    return render_template('hotelmanager.html')

@app.route('/travelagent')
def travelagent():
    return render_template('travelagent.html')
    
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))