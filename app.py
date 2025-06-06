from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db  # Import db from models package
from models.models import User, ParkingLot, ParkingSpot, Reservation  # Import models from models.models


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def create_admin_user():
    """Create default admin user if it doesn't exist"""
    with app.app_context():
        admin_user = User.query.filter_by(role='admin').first()
        if not admin_user:
            admin = User(
                username='admin',
                email='admin@gmail.com',
                password_hash=generate_password_hash('admin'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()

# ================== AUTHENTICATION DECORATORS ==================
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# ================== AUTHENTICATION ROUTES ==================
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        user = User.query.filter_by(username=username, role=role).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Welcome {user.username}!', 'success')
            return redirect(url_for('admin_dashboard' if user.role == 'admin' else 'user_dashboard'))
        
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username/Email already exists!', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('login'))

# ================== ADMIN ROUTES ==================
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    lots = ParkingLot.query.all()
    users = User.query.filter_by(role='user').all()
    total_spots = ParkingSpot.query.count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    
    return render_template('admin_dashboard.html',
                         lots=lots,
                         users=users,
                         total_spots=total_spots,
                         occupied_spots=occupied_spots)

@app.route('/create_lot', methods=['POST'])
@admin_required
def create_lot():
    try:
        lot = ParkingLot(
            prime_location_name=request.form['name'],
            price=float(request.form['price']),
            address=request.form['address'],
            pin_code=request.form['pin_code'],
            number_of_spots=int(request.form['number_of_spots'])
        )
        db.session.add(lot)
        db.session.commit()
        
        # Create parking spots
        for _ in range(lot.number_of_spots):
            spot = ParkingSpot(lot_id=lot.id)
            db.session.add(spot)
        db.session.commit()
        
        flash(f'Parking lot "{lot.prime_location_name}" created successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating parking lot: {str(e)}', 'danger')
    return redirect(url_for('admin_dashboard'))
@app.route('/registrations')
@admin_required
def registrations():
    users = User.query.all()
    return render_template('registrations.html', users=users)
@app.route('/admin/lot/<int:lot_id>/spots')
def admin_view_spots(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
    return render_template('admin_spots.html', lot=lot, spots=spots)
@app.route('/admin/spot/<int:spot_id>/delete', methods=['POST'])
def admin_delete_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)

    if spot.status == 'O':
        flash("Cannot delete: spot is currently occupied.", "danger")
        return redirect(url_for('admin_view_spots', lot_id=spot.lot_id))

    db.session.delete(spot)
    db.session.commit()
    flash("Spot deleted successfully.", "success")
    return redirect(url_for('admin_view_spots', lot_id=spot.lot_id))
@app.route('/admin/spot/<int:spot_id>/edit', methods=['GET', 'POST'])
def edit_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    lots = ParkingLot.query.all()

    active_res = Reservation.query.filter_by(spot_id=spot.id, status='active').first()

    if request.method == 'POST':
        new_status = request.form['status']
        new_lot_id = int(request.form['lot_id'])

        if spot.status == 'O' and active_res:
            flash('Cannot edit occupied spot with an active reservation.', 'danger')
            return redirect(url_for('admin_view_spots', lot_id=spot.lot_id))

        spot.status = new_status
        spot.lot_id = new_lot_id
        db.session.commit()
        flash('Spot updated successfully.', 'success')
        return redirect(url_for('admin_view_spots', lot_id=spot.lot_id))

    return render_template('edit_spot.html', spot=spot, lots=lots)
@app.route('/lot/<int:lot_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    if request.method == 'POST':
        lot.prime_location_name = request.form['name']
        lot.price = float(request.form['price'])
        lot.address = request.form['address']
        lot.pin_code = request.form['pin_code']
        db.session.commit()
        flash('Parking lot updated successfully.', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_lot.html', lot=lot)


@app.route('/lot/<int:lot_id>/delete', methods=['POST'])
@admin_required
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    
    # Check if any spot in this lot is occupied or has reservations
    for spot in lot.spots:
        active_reservations = Reservation.query.filter_by(spot_id=spot.id, status='active').first()
        if active_reservations:
            flash('Cannot delete lot. Some spots have active reservations.', 'danger')
            return redirect(url_for('admin_dashboard'))
    
    # Optional: double-check if all spots are available
    if any(spot.status == 'O' for spot in lot.spots):
        flash('Cannot delete lot. Some spots are still occupied.', 'danger')
        return redirect(url_for('admin_dashboard'))

    # Delete all spots first
    for spot in lot.spots:
        db.session.delete(spot)
    
    db.session.delete(lot)
    db.session.commit()
    flash('Parking lot deleted successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    users, lots, spots = [], [], []
    search_type = ''
    if request.method == 'POST':
        search_type = request.form['search_type']
        keyword = request.form['keyword']

        if search_type == 'user':
            users = User.query.filter(
                (User.username.ilike(f'%{keyword}%')) |
                (User.email.ilike(f'%{keyword}%'))
            ).all()
        elif search_type == 'lot':
            lots = ParkingLot.query.filter(
                (ParkingLot.pin_code.ilike(f'%{keyword}%')) |
                (ParkingLot.prime_location_name.ilike(f'%{keyword}%'))
            ).all()
        elif search_type == 'spot':
            spots = ParkingSpot.query.filter(
                (ParkingSpot.status.ilike(f'%{keyword}%'))
            ).all()

    return render_template('search.html', users=users, lots=lots, spots=spots, search_type=search_type)
@app.route('/admin/summary')
def admin_summary():
    users_count = User.query.count()
    available_spots = ParkingSpot.query.filter_by(status='A').count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    return render_template('admin_summary.html', users_count=users_count,
                           available_spots=available_spots, occupied_spots=occupied_spots)
# ================== USER ROUTES ==================
@app.route('/user/dashboard')
@login_required
def user_dashboard():
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    lots = ParkingLot.query.all()
    reservations = Reservation.query.filter_by(user_id=session['user_id'])\
                    .order_by(Reservation.parking_timestamp.desc()).all()
    
    search = request.args.get('search', '').strip()
    if search:
        # Filter parking lots by place name (prime_location_name) or pin_code
        lots = ParkingLot.query.filter(
            (ParkingLot.prime_location_name.ilike(f'%{search}%')) | 
            (ParkingLot.pin_code.ilike(f'%{search}%'))
        ).all()
    else:
        lots = ParkingLot.query.all()

   

    return render_template('user_dashboard.html',
                         lots=lots,
                         reservations=reservations)
@app.route('/book_spot/<int:lot_id>', methods=['GET', 'POST'])
@login_required
def book_spot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    if session.get('role') != 'user':
        flash('Only users can book spots.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
        if not available_spot:
            flash('No available spots in this parking lot!', 'danger')
            return redirect(url_for('user_dashboard'))
        reservation = Reservation(
            spot_id=available_spot.id,
            user_id=session['user_id'],
            parking_timestamp=datetime.utcnow(),
            status='active'
        )
        available_spot.status = 'O'
        db.session.add(reservation)
        db.session.commit()
        flash('Parking spot booked successfully!', 'success')
        return redirect(url_for('user_dashboard'))

    # GET: Show confirmation page
    available_spots = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').count()
    return render_template('book_confirm.html', lot=lot, available_spots=available_spots)

@app.route('/release_spot/<int:reservation_id>')
@login_required
def release_spot(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    
    if reservation.user_id != session['user_id']:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('user_dashboard'))
    
    if reservation.status != 'active':
        flash('This reservation is not active', 'warning')
        return redirect(url_for('user_dashboard'))
    
    try:
        # Calculate cost
        reservation.leaving_timestamp = datetime.utcnow()
        duration = reservation.leaving_timestamp - reservation.parking_timestamp
        hours = max(1, duration.total_seconds() / 3600)
        reservation.parking_cost = round(hours * reservation.spot.lot.price, 2)
        reservation.status = 'completed'
        
        # Free up the spot
        reservation.spot.status = 'A'
        
        db.session.commit()
        flash(f'Spot released! Total cost: ₹{reservation.parking_cost}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error releasing spot: {str(e)}', 'danger')
    
    return redirect(url_for('user_dashboard'))
@app.route('/user/reservations')
@login_required
def user_reservations():
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    reservations = Reservation.query.filter_by(user_id=session['user_id']).order_by(Reservation.parking_timestamp.desc()).all()
    return render_template('user_reservations.html', reservations=reservations)


# ================== PROFILE ROUTES ==================
@app.route('/profile')
@login_required
def user_profile():
    user = User.query.get(session['user_id'])
    reservations = Reservation.query.filter_by(user_id=user.id)\
                    .order_by(Reservation.parking_timestamp.desc()).all()
    return render_template('user_profile.html',
                         user=user,
                         reservations=reservations)
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')

        # Simple validation
        if not username or not email:
            flash('Username and Email are required.', 'danger')
            return redirect(url_for('edit_profile'))

        # Check for uniqueness of username and email (optional but recommended)
        if User.query.filter(User.username == username, User.id != user.id).first():
            flash('Username already taken.', 'danger')
            return redirect(url_for('edit_profile'))

        if User.query.filter(User.email == email, User.id != user.id).first():
            flash('Email already taken.', 'danger')
            return redirect(url_for('edit_profile'))

        user.username = username
        user.email = email
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('user_profile'))

    return render_template('edit_profile.html', user=user)
@app.route('/user/summary')
@login_required
def user_summary():
    user_id = session['user_id']
    booked_count = Reservation.query.filter_by(user_id=user_id, status='active').count()
    released_count = Reservation.query.filter_by(user_id=user_id, status='completed').count()

    return render_template('user_summary.html',
                           booked=booked_count,
                           released=released_count)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_user()
    app.run(debug=True)
