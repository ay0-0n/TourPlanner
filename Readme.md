# Tour Planner

Welcome to Tour Planner! This is project that me and [turjo](https://github.com/turjosajid) did for the CSE370-Datase Managemnt. This is a tour management website where people can complete the tour booking from Destination and hotels to transport and finally generate e recipt. The website lets you sign up as one of three roles. Tourist, Hotel owner and Travel Agent. 

**Tourist**: Tourists can book destinations, reserve hotel and room and can also book transports. After the booking is complete,the site will generate a PDF recipt with the total bill. They can also review any destination and rate them.

**Hotel Managers**: Hotel managers can add thir hotel, and the rooms. They can manage room by checking and managing their availability. They can also delete rooms. They can change their hotel description if necessarry.

**Travel Agent** Travel Agents can add transports, manage or delete the added transport. Their role is pretty similar to Hotel manager 




## Features
**Authentication**: Password are hashed with *flask_bcrypt* for security. Users can select their role during sign up
**Home Page**: Navbar, Banner and "See Destinations" route in the homepage. Users can see all the destinations and their reviews the site has to offer in See Destinations Page
**PDF Generation**: Pdf generation of the recipt with *pdfkit*
**All Blogs**: Shows all the blogs in the sebsite, Search(Based on title) and Sorting (Based on categories) functionality.
**Toggling avaiability**: Toggling availability of transports and rooms in a tabluar form.

## Whats Behind
*html*, *css*, *tailwindCSS*, *flask*, *sqlite*


## Installation and Setup

1. **Clone the Repository**:

2. **Install flask**
    ```bash
    pip install Flask

3. **Install flask_sqlalchemy for manageing the database**
    ```bash
    pip install -U Flask-SQLAlchemy

3. **Install flask_bcrypt for password hashing**
    ```bash
    pip install flask-bcrypt

4. **Install pdfkit for generating pdf**
    ```bash
    pip install pdfkit

4. **Download wkhtml in your local computer to convert html to pdf**:
   [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)

5. **Run**:
    ```bash
    flask run
