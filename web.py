from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from passlib.hash import pbkdf2_sha256
import os
import pymysql
from werkzeug.utils import secure_filename
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime

import numpy as np


app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions for images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# Database connection
def get_db_connection():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='travel_db'
    )
    return connection

@app.template_filter('date')
def format_date(value, date_format='%Y-%m-%d'):
    if value:
        return value.strftime(date_format)
    return value  # Return None if value is None
# Admin Check Decorator
def admin_required(f):
    def wrapped_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('You need to be an admin to access this page!')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    
    wrapped_function.__name__ = f.__name__
    return wrapped_function


# Index Page (Main Page)
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM destinations')
    destinations = cursor.fetchall()
    conn.close()
    return render_template('index.html', destinations=destinations)


@app.route('/list_destinations', methods=['GET'])
def list_destinations():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetching all required fields from the 'destinations' table
    cursor.execute('''SELECT id, name, description, image, address, category, best_season, ticket_price, activities
                      FROM destinations''')
    destinations = cursor.fetchall()
    conn.close()
    
    return render_template('list_destinations.html', destinations=destinations)


# Edit Destination (Admin only)
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_destination(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch the destination details from the database
    cursor.execute('SELECT * FROM destinations WHERE id = %s', (id,))
    destination = cursor.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        address = request.form['address']
        category = request.form['category']
        best_season = request.form['best_season']
        ticket_price = request.form['ticket_price']
        
        # Use .get() to avoid missing key error for 'activities' field
        activities = request.form.get('activities', '')  # Defaults to empty string if missing
        image = request.files.get('image')

        # If a new image is uploaded, save it
        if image:
            # Ensure the file has a valid extension
            if allowed_file(image.filename):
                # Delete the old image file from the folder if it exists
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], destination[3])  # Assuming the image is in the 4th column of the 'destinations' table
                if os.path.exists(old_image_path):
                    try:
                        os.remove(old_image_path)
                    except PermissionError:
                        flash('Could not delete the old image due to a permission issue.')

                # Save the new image with a sanitized filename
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                image_filename = filename
            else:
                flash('Invalid image file type. Allowed formats are: PNG, JPG, JPEG, GIF.')
                conn.close()
                return redirect(url_for('edit_destination', id=id))
        else:
            # If no new image is uploaded, use the old image
            image_filename = destination[3]  # Keep the old image name

        # Update the destination in the database
        try:
            cursor.execute('''UPDATE destinations 
                              SET name = %s, description = %s, address = %s, category = %s, 
                                  best_season = %s, ticket_price = %s, activities = %s, image = %s 
                              WHERE id = %s''', 
                           (name, description, address, category, best_season, ticket_price, activities, image_filename, id))
            conn.commit()
            flash('Destination updated successfully!')
        except Exception as e:
            flash(f'An error occurred while updating the destination: {e}')
            conn.close()
            return redirect(url_for('edit_destination', id=id))

        conn.close()
        return redirect(url_for('list_destinations'))

    conn.close()
    return render_template('edit_destination.html', destination=destination)

# # Add Destination (Admin only)

@app.route('/add', methods=['GET', 'POST'])
@admin_required
def add_destination():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        address = request.form['address']
        category = request.form['category']
        best_season = request.form['best_season']
        ticket_price = request.form['ticket_price']
        activities = request.form['activities']
        image = request.files['image']
        
        # If image is uploaded, save it
        if image and allowed_file(image.filename):
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_path)

        # Insert the destination into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO destinations (name, description, address, category, 
                        best_season, ticket_price, activities, image) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', 
                       (name, description, address, category, best_season, ticket_price, activities, image.filename if image else None))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    return render_template('add_destination.html')

# Booking a Destination (User only)

@app.route('/book/<int:destination_id>', methods=['POST'])
def book_destination(destination_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    user_id = session.get('user_id')
    if user_id:
        # Check if the user has already booked the same destination
        cursor.execute('SELECT * FROM bookings WHERE user_id = %s AND destination_id = %s', 
                       (user_id, destination_id))
        existing_booking = cursor.fetchone()

        if existing_booking:
            flash('You have already send request for this destination. You cannot book it again.', 'danger')
        else:
            # Proceed with booking if no existing booking is found
            cursor.execute('''INSERT INTO bookings (user_id, destination_id, is_pending) 
                               VALUES (%s, %s, %s)''', 
                           (user_id, destination_id, True))  # Assuming 'is_pending' is a boolean to mark pending status
            conn.commit()
            flash("Your request has been sent!")  # Flash message for confirmation
    else:
        flash("You must be logged in to book a destination.")

    conn.close()
    
    # Redirect back to the home page (or wherever the book button was clicked)
    return redirect(url_for('index'))  # This ensures it redirects to the main destinations page





from datetime import datetime

@app.route('/manage_bookings')
@admin_required
def manage_bookings():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all bookings with users, destinations, and booking date for display
    cursor.execute('''
        SELECT bookings.id, users.username, destinations.name, bookings.status, bookings.booking_date
        FROM bookings
        JOIN users ON bookings.user_id = users.id
        JOIN destinations ON bookings.destination_id = destinations.id
    ''')
    bookings = cursor.fetchall()

    # Format the booking_date before passing it to the template
    for i, booking in enumerate(bookings):
        # If booking[4] (the booking_date) is not None, format it
        if booking[4]:
            formatted_date = booking[4].strftime('%Y-%m-%d')  # Format date as 'YYYY-MM-DD'
            bookings[i] = list(booking)  # Convert tuple to list so it can be modified
            bookings[i][4] = formatted_date  # Update the booking_date field

    # Fetch only the bookings with 'Pending' status for count
    cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'Pending'")
    pending_bookings_count = cursor.fetchone()[0]

    conn.close()
    return render_template('manage_bookings.html', bookings=bookings, pending_bookings_count=pending_bookings_count)

@app.route('/update_booking/<int:booking_id>/<status>', methods=['POST'])
def update_booking(booking_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE bookings SET status = %s WHERE id = %s', (status, booking_id))
    conn.commit()
    conn.close()
    flash('Booking status updated successfully.')
    return redirect(url_for('manage_bookings'))

# Confirm Booking (Admin only)
@app.route('/confirm_booking/<int:booking_id>', methods=['POST'])
@admin_required
def confirm_booking(booking_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE bookings SET status = %s WHERE id = %s', ('Confirmed', booking_id))
    conn.commit()
    conn.close()
    flash('Your request has been send!')
    return redirect(url_for('manage_bookings'))

# User Registration Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        role = 'user'
        hashed_password = pbkdf2_sha256.hash(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash('Username already exists!')
            conn.close()
            return redirect(url_for('signup'))
        
        cursor.execute('INSERT INTO users (email, username, password, role) VALUES (%s, %s, %s, %s)',
                       (email, username, hashed_password, role))
        conn.commit()
        conn.close()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('signup.html')


#login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        conn.close()
        
        # Check if user exists and the hash method is valid
        if user:
            stored_password = user[2]  # Assuming password is in the 3rd column
            if stored_password and pbkdf2_sha256.verify(password, stored_password):
                session['user_id'] = user[0]
                session['username'] = user[1]
                session['role'] = user[3]
                
                # Check if the logged-in user is an admin and if there are any pending bookings
                if session['role'] == 'admin':
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM bookings WHERE is_pending = TRUE")
                    pending_count = cursor.fetchone()[0]
                    conn.close()

                    if pending_count > 0:
                        flash(f"You have {pending_count} pending booking requests.")
                flash('Login successful!')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password!')
        else:
            flash('User not found!')
    return render_template('login.html')

# # Search and AI-Based Recommendations
@app.route('/search')
def search_destinations():
    query = request.args.get('query', '')
    message = request.args.get('message', None)  # Get the message from the URL parameters if any

    conn = get_db_connection()
    cursor = conn.cursor()

    # Search destinations based on name or description
    cursor.execute("SELECT * FROM destinations WHERE name LIKE %s OR description LIKE %s", 
                   ('%' + query + '%', '%' + query + '%'))
    destinations = cursor.fetchall()

    main_result = None
    recommended_destinations = []

    if query and destinations:
        # Extract descriptions for similarity analysis
        descriptions = [destination[2] for destination in destinations]
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(descriptions)
        similarity_matrix = cosine_similarity(tfidf_matrix)

        # Find the main result if it matches the query exactly
        for idx, destination in enumerate(destinations):
            if destination[1].lower() == query.lower():
                main_result = destination  # Exact match found
                break

        # If no exact match, set the first destination as the main result
        if not main_result:
            main_result = destinations[0]

        # Get top recommendations based on similarity, excluding the main result
        main_index = destinations.index(main_result)  # Index of the main result
        sim_scores = list(enumerate(similarity_matrix[main_index]))
        sim_scores = sorted(sim_scores[1:], key=lambda x: x[1], reverse=True)  # Skip the first result (itself)
        recommended_destinations = [destinations[i[0]] for i in sim_scores[:3]]  # Top 3 recommendations

    conn.close()
    return render_template(
        'search_results.html', 
        query=query, 
        main_result=main_result, 
        recommended_destinations=recommended_destinations,
        message=message
    )


# # Profile page for user
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please log in to view your profile.')
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the user data, including email, username, and role
    cursor.execute('SELECT email, username, role FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()

    # Fetch booking information with destination name and status
    cursor.execute('''
        SELECT destinations.name, bookings.status 
        FROM bookings
        JOIN destinations ON bookings.destination_id = destinations.id
        WHERE bookings.user_id = %s
    ''', (user_id,))
    bookings = cursor.fetchall()
    
    conn.close()
    return render_template('profile.html', user=user, bookings=bookings)


# Delete Destination
@app.route('/delete/<int:id>', methods=['POST'])
@admin_required
def delete_destination(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get the destination to delete
    cursor.execute('SELECT * FROM destinations WHERE id = %s', (id,))
    destination = cursor.fetchone()

    if destination:
        # Delete the destination image
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], destination[3])
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except PermissionError:
                flash('Could not delete the old image due to a permission issue.')

        cursor.execute('DELETE FROM destinations WHERE id = %s', (id,))
        conn.commit()
        flash('Destination deleted successfully.')
    else:
        flash('Destination not found.')

    conn.close()
    return redirect(url_for('list_destinations'))


#wishlist
# Add to Wishlist
@app.route('/add_to_wishlist/<int:destination_id>', methods=['POST'])
def add_to_wishlist(destination_id):
    if 'user_id' not in session:
        flash("You must be logged in to add to your wishlist.", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the destination is already in the user's wishlist
    cursor.execute('SELECT * FROM wishlist WHERE user_id = %s AND destination_id = %s', (user_id, destination_id))
    existing_wishlist_item = cursor.fetchone()

    if existing_wishlist_item:
        flash('This destination is already in your wishlist.', 'info')
    else:
        # Add destination to the wishlist
        cursor.execute('INSERT INTO wishlist (user_id, destination_id) VALUES (%s, %s)', (user_id, destination_id))
        conn.commit()
        flash('Destination added to your wishlist!', 'success')

    conn.close()
    return redirect(url_for('index'))  # Redirect to index or appropriate page

# View Wishlist
@app.route('/wishlist')
def wishlist():
    if not session.get('user_id'):
        flash("You must be logged in to view your wishlist.", "danger")
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    
    # Fetch all wishlist items for the logged-in user
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT destinations.id, destinations.name, destinations.description, destinations.image 
                      FROM wishlist 
                      JOIN destinations ON wishlist.destination_id = destinations.id 
                      WHERE wishlist.user_id = %s''', (user_id,))
    destinations = cursor.fetchall()
    
    conn.close()
    return render_template('wishlist.html', destinations=destinations)

# Remove from Wishlist
@app.route('/remove_from_wishlist/<int:destination_id>', methods=['POST'])
def remove_from_wishlist(destination_id):
    if 'user_id' not in session:
        flash("You must be logged in to remove from your wishlist.", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    # Remove destination from the wishlist
    cursor.execute('DELETE FROM wishlist WHERE user_id = %s AND destination_id = %s', (user_id, destination_id))
    conn.commit()

    conn.close()
    flash('Destination removed from your wishlist!', 'success')
    return redirect(url_for('wishlist'))  # Redirect to the wishlist page

# Destination details
@app.route('/destination/<int:id>')
def destination_details(id):
    # Check if the user is logged in
    if not session.get('user_id'):
        flash('You need to be logged in to view destination details.', 'warning')
        return redirect(url_for('index'))  # Redirect to index page
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch destination details
    cursor.execute('SELECT * FROM destinations WHERE id = %s', (id,))
    destination = cursor.fetchone()

    conn.close()

    if not destination:
        flash('Destination not found!', 'danger')
        return redirect(url_for('index'))

    return render_template('destination_details.html', destination=destination)

# admin dashboard
@app.route('/admin/dashboard', methods=['GET', 'POST'])
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch total number of destinations
    cursor.execute('SELECT COUNT(*) FROM destinations')
    total_destinations = cursor.fetchone()[0]

    # Fetch total number of users
    cursor.execute('SELECT id, username, email FROM users')
    users = cursor.fetchall()
    total_users = len(users)

    if request.method == 'POST':
        # Handle user removal
        user_id = request.form.get('user_id')
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        conn.commit()
        flash('User account removed successfully!')
        return redirect(url_for('admin_dashboard'))

    conn.close()
    return render_template('admin_dashboard.html', total_destinations=total_destinations, total_users=total_users, users=users)


#logout
@app.route('/logout')
def logout():
    session.clear()  # Clears all session data
    flash('You have been logged out successfully!')
    return redirect(url_for('index'))  # Redirects to the login page
# Main Entry Point
if __name__ == '__main__':
    app.run(debug=True)
