from app import app, db
from flask import redirect, render_template, url_for, request, session
from app.models import User

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            current_user = User.query.filter_by(username = username, password= password).one()
            session["username"] = current_user.username
            user_type = current_user.user_type
            return f'Hello {session["username"]}! <a href="/logout">logout</a>'
            # if user_type == 'tourist':
            #     return redirect(url_for('tourist'))
            # elif user_type == 'hotel-manager':
            #     return redirect(url_for('hotelmanager'))
            # else:
            #     return redirect(url_for('travelagent'))
        
        except:
            return render_template('login.html', error='Invalid username or password!')
        

    return render_template('login.html')

@app.route('/signup' , methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone_number = request.form['phone_number']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return render_template('signup.html', error_message='Username already exists!')

        new_user = User(first_name=first_name, last_name=last_name, phone_number=phone_number,
                        email=email, username=username, password=password, user_type=user_type)
        
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))


    return render_template('signup.html')

# @app.route('/tourist', methods=['GET', 'POST'])
# def tourist():
#     if 'username' in session:
#         return f'Hello {session["username"]}! You are a Tourist! <a href="/logout">logout</a>'
#     else:
#         return 'Please login first <a href="/login">login</a>'

# @app.route('/hotelmanager', methods=['GET', 'POST'])
# def hotelmanager():
#     if 'username' in session:
#         return f'Hello {session["username"]}! You are a Hotel Manager! <a href="/logout">logout</a>'
#     else:
#         return 'Please login first <a href="/login">login</a>'

# @app.route('/travelagent', methods=['GET', 'POST'])
# def travelagent():
#     if 'username' in session:
#         return f'Hello {session["username"]}! You are a Travel Agent! <a href="/logout">logout</a>'
#     else:
#         return 'Please login first <a href="/login">login</a>'
    
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))