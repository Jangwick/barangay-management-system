from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.official import Official
from models import db
from utils import parse_date, role_required
from datetime import datetime

officials_bp = Blueprint('officials', __name__, url_prefix='/officials')

@officials_bp.route('/')
@login_required
def officials():
    all_officials = Official.query.order_by(Official.start_term.desc()).all()
    today = datetime.now().date()
    return render_template('officials.html', officials=all_officials, today=today)

@officials_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('staff')  # Only staff and admin can add officials
def add_official():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        position = request.form['position']
        start_term = parse_date(request.form['start_term'])
        end_term = parse_date(request.form['end_term'])
        contact_number = request.form['contact_number']
        
        new_official = Official(
            first_name=first_name,
            last_name=last_name,
            position=position,
            start_term=start_term,
            end_term=end_term,
            contact_number=contact_number
        )
        
        db.session.add(new_official)
        db.session.commit()
        flash('Official added successfully!', 'success')
        return redirect(url_for('officials.officials'))
        
    return render_template('add_official.html')

@officials_bp.route('/<int:official_id>', methods=['GET'])
@login_required
def view_official(official_id):
    official = Official.query.get_or_404(official_id)
    today = datetime.now().date()
    is_current = official.end_term >= today
    return render_template('view_official.html', official=official, is_current=is_current)

@officials_bp.route('/<int:official_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('staff')
def edit_official(official_id):
    official = Official.query.get_or_404(official_id)
    
    if request.method == 'POST':
        official.first_name = request.form['first_name']
        official.last_name = request.form['last_name']
        official.position = request.form['position']
        official.start_term = parse_date(request.form['start_term'])
        official.end_term = parse_date(request.form['end_term'])
        official.contact_number = request.form['contact_number']
        
        db.session.commit()
        flash('Official updated successfully!', 'success')
        return redirect(url_for('officials.view_official', official_id=official.id))
        
    return render_template('edit_official.html', official=official)

@officials_bp.route('/<int:official_id>/delete', methods=['POST'])
@login_required
@role_required('admin')  # Only admin can delete officials
def delete_official(official_id):
    official = Official.query.get_or_404(official_id)
    
    try:
        db.session.delete(official)
        db.session.commit()
        flash('Official deleted successfully!', 'success')
    except:
        db.session.rollback()
        flash('Error deleting official.', 'error')
    
    return redirect(url_for('officials.officials'))
