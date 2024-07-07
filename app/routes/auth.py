# Import necessary modules and classes from Flask and the app's database models
from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from app.database.models import db, Employee

# Create a Blueprint named 'auth_bp' for authentication-related routes
auth_bp = Blueprint('auth_bp', __name__)

# Define a route for the login page, which handles both GET and POST requests
@auth_bp.route('/', methods=['GET', 'POST'])
def login(): 
    # Check if the request method is POST, which means the form has been submitted
    if request.method == 'POST':
        # Retrieve form data for role, email, and password from the request object
        role = request.form['role']
        email = request.form['email']
        password = request.form['password']
        
        # Store the retrieved form data in the session object, so that i can use this data from every other pagef
        session['role'] = role
        session['email'] = email
        session['password'] = password
        
        # Check if the role selected is 'admin'
        if role == 'admin':
            # Query the database to find an admin user with the given email and password
            user = Employee.query.filter_by(email=email, password=password, is_admin=True).first()
            if user:  # If a matching user is found
                # Create a dictionary with the user's information
                user_dict = {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'position': user.position,
                    'department': user.department,
                    'joining_date': user.joining_date
                }
                # Store the user's information in the session
                session['user_dict'] = user_dict
                # Flash a success message to the user
                flash('Admin login successful', 'success')
                # Redirect to the admin dashboard
                #!Note: main_bp (blueprint name) .admin (function name of that file)
                return redirect(url_for('main_bp.admin')) # redirect use for performing logical operation and data propagation
            else:
                # Flash an error message if no matching admin user is found
                flash('Invalid email or password for admin', 'danger')
        elif role == 'user':
            # Query the database to find a non-admin user with the given email and password
            user = Employee.query.filter_by(email=email, password=password, is_admin=False).first()
            if user:  # If a matching user is found
                # Create a dictionary with the user's information
                user_dict = {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'position': user.position,
                    'department': user.department,
                    'joining_date': user.joining_date
                }
                # Store the user's information in the session
                session['user_dict'] = user_dict
                # Flash a success message to the user
                flash('User login successful', 'success')
                # Redirect to the user profile 
                #!Note: main_bp (blueprint name) .user (function name of that file)
                return redirect(url_for('main_bp.user')) # redirect use for performing logical operation and data propagation
            else:
                # Flash an error message if no matching user is found
                flash('Invalid email or password for user', 'danger')
    # Render the login template if the request method is GET or if login fails
    return render_template('login.html') # render_template can only show the html file but can't perform any logical operation or data propagation
# Define a route for logging out
@auth_bp.route('/logout')
def logout():
    # Clear the session to log the user out
    session.clear()
    # Redirect to the login page
    return redirect(url_for('auth_bp.login'))
