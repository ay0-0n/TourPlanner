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
            current_user = User.query.filter_by(username = username, password= password).one()
            session["current_user"] = current_user.username
            session['user_type'] = current_user.user_type
            return redirect(url_for('profile'))
        
        except:
            return render_template('login.html', error='Invalid username or password!')
        
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


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'current_user' in session:
        username = session['current_user']
        current_user = User.query.filter_by(username = username).first()
        return render_template('profile.html', user = current_user)
    else:
        return redirect(url_for('login'))

@app.route('/reservation', methods = ['GET', 'POST'])
def reservation():
    if 'current_user' in session and session['user_type'] == 'tourist':
        username = session['current_user']
        current_user = User.query.filter_by(username = username).first()
    else:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        selected_destination = request.form['destination']
        return redirect(url_for('select_hotel', destination = selected_destination))

    destinations = TourDestination.query.all()
    return render_template('reservation.html', destinations = destinations)





@app.route('/select_hotel', methods=['GET', 'POST'])
def select_hotel():
    destination_id = request.args.get('destination')

    if request.method == 'POST':
        destination_id = request.form['destination']
        selected_hotel = request.form['hotel']
        return redirect(url_for('select_transport', hotel=selected_hotel, destination=destination_id))
    
    hotels = Hotels.query.filter_by(dest_id=destination_id).all()
    return render_template('select_hotel.html', destination = destination_id, hotels=hotels)






@app.route('/select_transport', methods = ['GET', 'POST'])
def select_transport():
    destination_id = request.args.get('destination')
    hotel_id = request.args.get('hotel')


    transports = TransportAgent.query.filter_by(dest_id = destination_id)
    return render_template('select_transport.html', destination_id=destination_id, hotel_id=hotel_id, transports = transports)


    




@app.route('/manage_hotel', methods = ['GET', 'POST'])
def manage_hotel():
    if 'current_user' in session and session['user_type'] == 'hotel-manager':
        username = session['current_user']
        current_user = User.query.filter_by(username = username).first()
    else:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        hotel_name = request.form['hotel_name']
        hotel_location = request.form['hotel_location']
        destination_id = request.form['destination'] 

        new_hotel = Hotels(hotel_name = hotel_name, hotel_location = hotel_location, manager_id = current_user.user_id, dest_id = destination_id)
        db.session.add(new_hotel)
        db.session.commit()

    destinations = TourDestination.query.all()
    return render_template('manage_hotels.html', destinations = destinations)
    

@app.route('/manage_transport', methods = ['GET', 'POST'])
def manage_transport():
    if 'current_user' in session and session['user_type'] == 'transport-agent':
        username = session['current_user']
        current_user = User.query.filter_by(username = username).first()
    else:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        transport_type = request.form['transport_type']
        availability = request.form['availability'] == 'True'
        cost = int(request.form['cost'])
        destination_id = request.form['destination']

        new_transport = TransportAgent(transport_type = transport_type, availability = availability, agent_id = current_user.user_id, cost = cost, dest_id = destination_id)
        db.session.add(new_transport)
        db.session.commit()

    destinations = TourDestination.query.all()
    return render_template('manage_transports.html', destinations = destinations)
    
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_type', None)
    return redirect(url_for('login'))
