from app import app, db
from flask import redirect, render_template, url_for, request, session, flash, make_response
from app.models import *
from flask_bcrypt import Bcrypt
from random import *
from datetime import datetime 
import pdfkit


@app.route('/')
@app.route('/home')
def index():
    return render_template("home.html")

@app.route('/see_destination', methods=['GET', 'POST'])
def see_destination():
    destinations = TourDestination.query.all()
    destination_reviews = {}
    for destination in destinations:
        reviews = Reviews.query.filter_by(dest_id=destination.destination_id).limit(3).all()
        destination_reviews[destination] = reviews
    return render_template('see_destination.html', destinations=destinations, destination_reviews=destination_reviews)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            if bcrypt.check_password_hash(user.password, password):
                session["current_user"] = user.username
                if user.role_id == 0:
                    session["user_type"] = 'tourist'
                elif user.role_id == 1:
                    session["user_type"] = 'hotel-manager'
                elif user.role_id == 2:
                    session["user_type"] = 'transport-agent'


                return redirect(url_for('profile'))
            else:
                error_message = 'Invalid username or password!'
        else:
            error_message = 'Invalid username or password!'
        return render_template('login.html', error_message=error_message)

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




@app.route('/select_transport', methods=['GET', 'POST'])
def select_transport():
    destination_id = request.args.get('destination')
    selected_hotel = request.args.get('hotel')

    if request.method == 'POST':
        selected_transport = request.form['transport']
        selected_hotel = request.form['hotel']
        destination_id = request.form['destination']
        print(selected_transport, selected_hotel, destination_id)
        return redirect(url_for('select_room', hotel=selected_hotel, destination=destination_id, transport=selected_transport))


    transports = Transports.query.filter_by(dest_id=destination_id, availability=True).all()
    return render_template('select_transport.html', destination=destination_id, hotel=selected_hotel, transports=transports)


@app.route('/select_room', methods=['GET', 'POST'])
def select_room():
    destination_id = request.args.get('destination')
    selected_hotel = request.args.get('hotel')
    selected_transport = request.args.get('transport')

    if request.method == 'POST':
        selected_room = request.form['room']
        selected_transport = request.form['transport']
        selected_hotel = request.form['hotel']
        destination_id = request.form['destination']
        return redirect(url_for('select_date', room=selected_room, transport=selected_transport, hotel=selected_hotel, destination=destination_id))

    rooms = Rooms.query.filter_by(hotel_id=selected_hotel, availability=True).all()
    return render_template('select_room.html', destination=destination_id, hotel=selected_hotel, transport=selected_transport, rooms=rooms)

@app.route('/select_date', methods=['GET', 'POST'])
def select_date():
    destination_id = request.args.get('destination')
    selected_hotel = request.args.get('hotel')
    selected_transport = request.args.get('transport')
    selected_room = request.args.get('room')

    if request.method == 'POST':
        selected_arrival_date = request.form['arrival_date']
        selected_departure_date = request.form['departure_date']

        selected_room = request.form['room']
        selected_transport = request.form['transport']
        selected_hotel = request.form['hotel']
        destination_id = request.form['destination']

        if selected_arrival_date >= selected_departure_date:
            return render_template('select_date.html', destination=destination_id, hotel=selected_hotel, transport=selected_transport, room=selected_room, error='Arrival date must be before departure date!')
        else:
            return redirect(url_for('confirm_booking', room=selected_room, transport=selected_transport, hotel=selected_hotel, destination=destination_id, arrival_date=selected_arrival_date, departure_date=selected_departure_date))

    return render_template('select_date.html', destination=destination_id, hotel=selected_hotel, transport=selected_transport, room=selected_room)


def generateReservationID(user_id, destination_id, hotel_id, transport_id, room_id, reservation_date):
    reservation_id = str(user_id) + str(destination_id) + str(hotel_id) + str(transport_id) + str(room_id) 
    date = str(reservation_date.date()).split('-')
    for i in date:
        reservation_id += i

    time = str(reservation_date.time())[:8].split(':')
    for i in time:
        reservation_id += i
    return int(reservation_id)



@app.route('/confirm_booking', methods=['POST', 'GET'])
def confirm_booking():
    if request.method == 'POST':
        destination_id = request.form['destination']
        selected_hotel = request.form['hotel']
        selected_transport = request.form['transport']
        selected_room = request.form['room']
        arrival_date = request.form['arrival_date']
        departure_date = request.form['departure_date']
        dinner_reservation = bool(int(request.form['dinner_reservation']))

        arrival_date_obj = datetime.strptime(arrival_date, '%Y-%m-%d')
        departure_date_obj = datetime.strptime(departure_date, '%Y-%m-%d')

        reservation_date = datetime.now()

        user = User.query.filter_by(username=session['current_user']).first().user_id

        new_reservation = Reservation(
            user_id=user,
            reservation_id=generateReservationID(user, destination_id, selected_hotel, selected_transport, selected_room, reservation_date),
            transport_id=selected_transport,
            room_id=selected_room,
            arrival_date=arrival_date_obj,
            departure_date=departure_date_obj,
            dinner_reservation=dinner_reservation,
            reservation_date=reservation_date
        )
        
        db.session.add(new_reservation)
        db.session.commit()

        # Corrected filtering syntax
        destination = TourDestination.query.filter_by(destination_id=destination_id).first()
        hotel = Hotels.query.filter_by(hotel_id=selected_hotel).first()
        transport = Transports.query.filter_by(transport_id=selected_transport).first()
        room = Rooms.query.filter_by(room_id=selected_room).first()

        # Construct the data dictionary
        data = {
            'destination': {
                'destination_id': destination.destination_id,
                'destination_name': destination.destination_name
            },
            'hotel': {
                'hotel_id': hotel.hotel_id,
                'hotel_name': hotel.hotel_name
            },
            'transport': {
                'transport_id': transport.transport_id,
                'transport_type': transport.transport_type,
                'cost': transport.cost
            },
            'room': {
                'room_id': room.room_id,
                'room_no': room.room_no,
                'room_type': room.room_type,
                'cost': room.cost
            },
            'arrival_date': arrival_date,
            'departure_date': departure_date,
            'dinner_reservation': bool(int(dinner_reservation)),
            'reservation_date': reservation_date
        }
        print(data)
        session['booking_data'] = data
        return redirect(url_for('booking_success'))
    
    # If the request method is GET, render the confirm_booking template with the provided data
    destination_id = request.args.get('destination')
    selected_hotel = request.args.get('hotel')
    selected_transport = request.args.get('transport')
    selected_room = request.args.get('room')
    arrival_date = request.args.get('arrival_date')
    departure_date = request.args.get('departure_date')
    return render_template('confirm_booking.html', destination=destination_id, hotel=selected_hotel, transport=selected_transport, room=selected_room, arrival_date=arrival_date, departure_date=departure_date)


@app.route('/booking_success', methods=['GET', 'POST'])
def booking_success():
    data = session.get('booking_data')
    if not data:
        return redirect(url_for('confirm_booking'))

    return render_template('booking_success.html', data=data)


@app.route('/download_invoice')
def download_invoice():
    data = session.get('booking_data')
    if not data:
        return "No booking data found."
    
    # Render the HTML template with the provided data
    html_content = f"""
    <h1>Invoice</h1>
    <hr/>
    <p><strong>Destination:</strong> {data['destination']['destination_name']}</p>
    <p><strong>Hotel:</strong> {data['hotel']['hotel_name']}</p>
    <p><strong>Transport:</strong> {data['transport']['transport_type']}</p>
    <p><strong>Room no:</strong> {data['room']['room_no']}</p>
    <p><strong>Room Type:</strong> {data['room']['room_type']}</p>
    <p><strong>Arrival Date:</strong> {data['arrival_date']}</p>
    <p><strong>Departure Date:</strong> {data['departure_date']}</p>
    <p><strong>Dinner Reservation:</strong> {"Yes" if data['dinner_reservation'] else "No"}</p>
    <p><strong>Reservation Date:</strong> {data['reservation_date']}</p>
    <p><strong>Total Cost:</strong> {data['room']['cost'] + data['transport']['cost']}</p>
    
    """

    # Convert the HTML to PDF
    pdf = pdfkit.from_string(html_content, False)

    # Create a response
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=invoice.pdf'
    return response

@app.route('/add_review', methods=['GET', 'POST'])
def add_review():
    if request.method == 'POST':
        destination_id = request.form['destination']
        review = request.form['review']
        rating = request.form['rating']

        new_review = Reviews(
            user_id = User.query.filter_by(username=session['current_user']).first().user_id,
            dest_id = destination_id,
            feedback = review,
            rating = rating
        )

        db.session.add(new_review)
        db.session.commit()
        return redirect(url_for('profile'))
    return render_template('add_review.html', destinations=TourDestination.query.all())



@app.route('/manage_hotel', methods = ['GET', 'POST'])
def manage_hotel():
    if 'current_user' in session and session['user_type'] == 'hotel-manager':
        username = session['current_user']
        current_user = User.query.filter_by(username = username).first()
    else:
        return redirect(url_for('login'))

    if request.method == 'POST':
        hotel_name = request.form['hotel_name']
        hotel_location = request.form['hotel_location']
        destination_id = request.form['destination'] 

        new_hotel = Hotels(hotel_name = hotel_name, hotel_location = hotel_location, manager_id = current_user.user_id, dest_id = destination_id)
        db.session.add(new_hotel)
        db.session.commit()
        return redirect(url_for('add_rooms'))
    
    if request.method == 'GET':
        current_user = User.query.filter_by(username = session['current_user']).first()
        try:
            hotel = Hotels.query.filter_by(manager_id = current_user.user_id).first()
            if hotel:
                return redirect(url_for('add_rooms'))
            else:
                destinations = TourDestination.query.all()
                return render_template('manage_hotels.html', destinations = destinations)
        except:
            destinations = TourDestination.query.all()
            return render_template('manage_hotels.html', destinations = destinations)


def get_hotel_id_for_manager(manager_id):
    hotel = Hotels.query.filter_by(manager_id=manager_id).first()
    if hotel:
        return hotel.hotel_id
    else:
        return None

@app.route('/add_rooms', methods=['GET', 'POST'])
def add_rooms():
    if 'current_user' in session and session['user_type'] == 'hotel-manager':
        username = session['current_user']
        current_user = User.query.filter_by(username=username).first()
    else:
        return redirect(url_for('login'))

    hotel_id = get_hotel_id_for_manager(current_user.user_id)

    if request.method == 'POST':
        room_no = request.form['room_no']
        room_type = request.form['room_type']
        cost = request.form['cost']
        availability = request.form['availability'] == 'True'

        new_room = Rooms(room_no=room_no, room_type=room_type, cost=cost, availability=availability, hotel_id=hotel_id)
        db.session.add(new_room)
        db.session.commit()

    rooms = Rooms.query.filter_by(hotel_id=hotel_id).all()
    return render_template('add_rooms.html', rooms=rooms)

@app.route('/toggle_room/<int:room_id>', methods=['GET', 'POST'])
def toggle_room(room_id):
    room = Rooms.query.get(room_id)
    room.availability = not room.availability
    db.session.commit()
    return redirect(url_for('add_rooms'))

@app.route('/delete_room/<int:room_id>', methods=['GET', 'POST'])
def delete_room(room_id):
    room = Rooms.query.get(room_id)
    db.session.delete(room)
    db.session.commit()
    return redirect(url_for('add_rooms'))

@app.route('/change_hotel_details', methods=['GET', 'POST'])
def change_hotel_details():
    if request.method == 'POST':
        new_hotel_name = request.form.get('new_hotel_name', None)
        new_hotel_location = request.form.get('new_hotel_location', None)
        new_destination_id = request.form['new_destination_id']

        current_user = User.query.filter_by(username=session['current_user']).first()
        manager_id = current_user.user_id

        hotel = Hotels.query.filter_by(manager_id=manager_id).first()
        if hotel:
            if new_hotel_name:
                hotel.hotel_name = new_hotel_name
            if new_hotel_location:
                hotel.hotel_location = new_hotel_location
            hotel.dest_id = new_destination_id
            db.session.commit()
            return redirect(url_for('profile'))
        else:
            error = "You have not added any hotel yet."
            destinations = TourDestination.query.all()
            return render_template('change_hotel_details.html', error=error, destinations=destinations)

    destinations = TourDestination.query.all()
    return render_template('change_hotel_details.html', destinations=destinations)



def get_destination_name(dest_id):
    destination = TourDestination.query.get(dest_id)
    return destination.destination_name if destination else "Unknown"    

@app.route('/manage_transport', methods = ['GET', 'POST'])
def manage_transport():
    if 'current_user' in session and session['user_type'] == 'transport-agent':
        username = session['current_user']
        current_user = User.query.filter_by(username = username).first()
    else:
        return redirect(url_for('login'))

    if request.method == 'POST':
        transport_type = request.form['transport_type']
        availability = request.form['availability'] == 'True'
        cost = int(request.form['cost'])
        destination_id = request.form['destination']

        new_transport = Transports(transport_type = transport_type, availability = availability, agent_id = current_user.user_id, cost = cost, dest_id = destination_id)
        db.session.add(new_transport)
        db.session.commit()

    destinations = TourDestination.query.all()
    transports = Transports.query.filter_by(agent_id = current_user.user_id).all()
    return render_template('manage_transports.html', destinations = destinations, transports = transports, get_destination_name = get_destination_name)


@app.route('/toggle_transport/<int:transport_id>')
def toggle_transport(transport_id):
    transport = Transports.query.get(transport_id)
    if transport:
        transport.availability = not transport.availability
        db.session.commit()
    return redirect(url_for('manage_transport'))


@app.route('/delete_transport/<int:transport_id>')
def delete_transport(transport_id):
    transport = Transports.query.get(transport_id)
    if transport:
        db.session.delete(transport)
        db.session.commit()
    return redirect(url_for('manage_transport'))
    
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_type', None)
    session.pop('booking_data', None)
    return redirect(url_for('login'))