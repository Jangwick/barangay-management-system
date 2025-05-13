from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from models.user import User, ROLE_ADMIN, ROLE_STAFF, ROLE_USER
from models import db
from functools import wraps
from models.blotter import Blotter # Import Blotter model
from models.resident import Resident # Import Resident model for linking
from datetime import datetime
from forms.blotter_form import BlotterForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You do not have permission to access this page', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def index():
    return render_template('admin/index.html')

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.all()
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        role = request.form.get('role', ROLE_USER)
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('admin.new_user'))
            
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('admin.new_user'))
            
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('User created successfully', 'success')
        return redirect(url_for('admin.users'))
        
    return render_template('admin/new_user.html')

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.role = request.form.get('role')
        user.is_active = 'is_active' in request.form
        
        # Only update password if provided
        new_password = request.form.get('password')
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('admin.users'))
        
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting your own account
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'error')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin.users'))

# Blotter Management Routes
@admin_bp.route('/blotters')
@login_required
@admin_required
def list_blotters():
    blotters = Blotter.query.order_by(Blotter.date_reported.desc()).all()
    return render_template('admin/blotters.html', blotters=blotters)

@admin_bp.route('/blotters/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_blotter():
    residents = Resident.query.order_by(Resident.last_name, Resident.first_name).all()
    if request.method == 'POST':
        try:
            incident_date_str = request.form.get('incident_date')
            incident_time_str = request.form.get('incident_time')
            
            incident_date = datetime.strptime(incident_date_str, '%Y-%m-%d').date()
            incident_time = None
            if incident_time_str:
                incident_time = datetime.strptime(incident_time_str, '%H:%M').time()

            new_blotter_record = Blotter(
                complainant_name=request.form.get('complainant_name'),
                respondent_name=request.form.get('respondent_name'),
                incident_type=request.form.get('incident_type'),
                incident_date=incident_date,
                incident_time=incident_time,
                incident_location=request.form.get('incident_location'),
                details=request.form.get('details'),
                status=request.form.get('status', 'Pending'),
                complainant_resident_id=request.form.get('complainant_resident_id') if request.form.get('complainant_resident_id') else None,
                respondent_resident_id=request.form.get('respondent_resident_id') if request.form.get('respondent_resident_id') else None
            )
            db.session.add(new_blotter_record)
            db.session.commit()
            flash('Blotter record created successfully.', 'success')
            return redirect(url_for('admin.list_blotters'))
        except ValueError as e:
            flash(f'Error in form data: {e}. Please check date and time formats.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
            
    return render_template('admin/new_blotter.html', residents=residents)

@admin_bp.route('/blotters/edit/<int:blotter_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_blotter(blotter_id):
    """Edit an existing blotter or create a new one if blotter_id is 0"""
    
    # Initialize blotter and form
    if blotter_id > 0:
        # Edit existing blotter
        blotter = Blotter.query.get_or_404(blotter_id)
        form = BlotterForm(obj=blotter)
    else:
        # Create new blotter
        form = BlotterForm()
    
    # Get all residents for the dropdown selectors
    residents = Resident.query.order_by(Resident.last_name).all()
    
    if form.validate_on_submit():
        try:
            if blotter_id > 0:
                # Update existing blotter - use the form to update properties
                form.populate_obj(blotter)
                
                # Ensure complainant_name is set if there's a resident ID
                if blotter.complainant_resident_id and not blotter.complainant_name:
                    resident = Resident.query.get(blotter.complainant_resident_id)
                    if resident:
                        blotter.complainant_name = f"{resident.first_name} {resident.last_name}"
                
                flash('Blotter record has been updated successfully!', 'success')
            else:
                # Create new blotter - DON'T set the ID field
                new_blotter = Blotter()
                
                # Copy data from form to new_blotter manually
                new_blotter.incident_type = form.incident_type.data
                new_blotter.incident_date = form.incident_date.data
                new_blotter.incident_time = form.incident_time.data
                new_blotter.incident_location = form.incident_location.data
                new_blotter.details = form.details.data
                new_blotter.status = form.status.data
                new_blotter.date_reported = datetime.utcnow()
                
                # Handle resident IDs and ensure names are set
                if form.complainant_resident_id.data:
                    new_blotter.complainant_resident_id = form.complainant_resident_id.data
                    # Get the resident name from the database
                    resident = Resident.query.get(form.complainant_resident_id.data)
                    if resident:
                        new_blotter.complainant_name = f"{resident.first_name} {resident.last_name}"
                    else:
                        # Fallback if resident not found
                        new_blotter.complainant_name = "Unknown Complainant"
                else:
                    # Use form data if available, otherwise set a default
                    new_blotter.complainant_name = form.complainant_name.data or "Anonymous"
                
                if form.respondent_resident_id.data:
                    new_blotter.respondent_resident_id = form.respondent_resident_id.data
                    # Get the resident name from the database
                    resident = Resident.query.get(form.respondent_resident_id.data)
                    if resident:
                        new_blotter.respondent_name = f"{resident.first_name} {resident.last_name}"
                else:
                    # Respondent name is optional, use form data if available
                    new_blotter.respondent_name = form.respondent_name.data
                
                # Add the new blotter to the session
                db.session.add(new_blotter)
                flash('New blotter record has been created successfully!', 'success')
            
            # Commit the changes
            db.session.commit()
            return redirect(url_for('admin.list_blotters'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            # Use logger if current_app is available
            import logging
            logging.error(f"Error saving blotter: {str(e)}")
    
    return render_template('admin/blotter_form.html', 
                          form=form, 
                          residents=residents,
                          blotter_id=blotter_id)

@admin_bp.route('/blotters/view/<int:blotter_id>')
@login_required
@admin_required
def view_blotter(blotter_id):
    """View a specific blotter record"""
    blotter = Blotter.query.get_or_404(blotter_id)
    return render_template('admin/blotter_view.html', blotter=blotter)

@admin_bp.route('/blotters/<int:blotter_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_blotter(blotter_id):
    blotter_record = Blotter.query.get_or_404(blotter_id)
    try:
        db.session.delete(blotter_record)
        db.session.commit()
        flash('Blotter record deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting blotter record: {str(e)}', 'error')
    return redirect(url_for('admin.list_blotters'))
