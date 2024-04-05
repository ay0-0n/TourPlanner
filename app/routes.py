from app import app, db
from flask import redirect, render_template, url_for, request, session, flash
from app.models import *
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from random import *

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'tourplanner.dev@gmail.com'
app.config['MAIL_PASSWORD'] = 'kmox qqhn pkzk xbws'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

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

        existing_email = User.query.filter_by(email=email).first()
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return render_template('signup.html', error_message='Username already exists!')
        if existing_email:
            return render_template('signup.html', error_message='Email already exists!')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(first_name=first_name, last_name=last_name, phone_number=phone_number,
                        email=email, username=username, password=hashed_password, role_id=role_id)

        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please login to continue.')
        return redirect(url_for('login'))

    return render_template('signup.html')

mail = Mail(app)
otp = randint(1000, 9999)

def send_mail(email):
    msg = Message('OTP: Tour planner', sender='tourplanner.dev@gmail.com', recipients=[email])
    msg.body = str(otp)
    mail.send(msg)
    return redirect(url_for('otpcheck', email=email))

@app.route('/otpcheck', methods=['GET','POST'])
def otpcheck():
    if request.method == 'POST':
        user_otp = request.form['otp']
        if otp == int(user_otp):
            return redirect(url_for('resetpass'))
        else:
            return render_template('otpcheck.html', error_message='Invalid OTP, please try again!')
    return render_template('otpcheck.html')

@app.route('/resetpass', methods=['GET', 'POST'])
def resetpass():
    email = session.get('email')
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        if password == confirm_password:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user = User.query.filter_by(email=email).first() 
            user.password = hashed_password
            db.session.commit()
            session.pop('email')
            return redirect(url_for('login'))
        else:
            return render_template('resetpass.html', error_message='Password does not match, please try again!')
    
    return render_template('resetpass.html')

@app.route('/forgetpass', methods=['GET', 'POST'])
def forgetpass():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()

        if user:
            session['email'] = email
            send_mail(email)
            return redirect(url_for('otpcheck'))
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