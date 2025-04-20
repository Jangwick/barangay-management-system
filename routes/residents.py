from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from models.resident import Resident
from models import db
from utils import parse_date, role_required
from sqlalchemy import or_

residents_bp = Blueprint('residents', __name__, url_prefix='/residents')

@residents_bp.route('/')
@login_required
def residents():
    # Add search and pagination
    search_term = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Resident.query
    
    if search_term:
        query = query.filter(
            or_(
                Resident.first_name.ilike(f'%{search_term}%'),
                Resident.last_name.ilike(f'%{search_term}%'),
                Resident.address.ilike(f'%{search_term}%')
            )
        )
    
    # Sort options
    sort_by = request.args.get('sort', 'last_name')
    sort_dir = request.args.get('dir', 'asc')
    
    if sort_by == 'name':
        if sort_dir == 'asc':
            query = query.order_by(Resident.last_name.asc(), Resident.first_name.asc())
        else:
            query = query.order_by(Resident.last_name.desc(), Resident.first_name.desc())
    elif sort_by == 'date_added':
        if sort_dir == 'asc':
            query = query.order_by(Resident.created_at.asc())
        else:
            query = query.order_by(Resident.created_at.desc())
    
    # Paginate results
    residents_pagination = query.paginate(page=page, per_page=per_page)
    
    return render_template('residents/index.html', 
                          residents=residents_pagination.items,
                          pagination=residents_pagination,
                          search_term=search_term,
                          sort_by=sort_by,
                          sort_dir=sort_dir)

@residents_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_resident():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        contact_number = request.form['contact_number']
        email = request.form['email']
        birth_date = parse_date(request.form['birth_date'])
        
        new_resident = Resident(
            first_name=first_name,
            last_name=last_name,
            address=address,
            contact_number=contact_number,
            email=email,
            birth_date=birth_date
        )
        
        db.session.add(new_resident)
        db.session.commit()
        flash('Resident added successfully!', 'success')
        return redirect(url_for('residents.residents'))
        
    return render_template('residents/add.html')

@residents_bp.route('/<int:resident_id>', methods=['GET'])
@login_required
def view_resident(resident_id):
    resident = Resident.query.get_or_404(resident_id)
    return render_template('residents/view.html', resident=resident)

@residents_bp.route('/<int:resident_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_resident(resident_id):
    resident = Resident.query.get_or_404(resident_id)
    
    if request.method == 'POST':
        resident.first_name = request.form['first_name']
        resident.last_name = request.form['last_name']
        resident.address = request.form['address']
        resident.contact_number = request.form['contact_number']
        resident.email = request.form['email']
        resident.birth_date = parse_date(request.form['birth_date'])
        
        db.session.commit()
        flash('Resident updated successfully!', 'success')
        return redirect(url_for('residents.view_resident', resident_id=resident.id))
        
    return render_template('residents/edit.html', resident=resident)

@residents_bp.route('/<int:resident_id>/delete', methods=['POST'])
@login_required
@role_required('staff')  # Only staff and above can delete
def delete_resident(resident_id):
    resident = Resident.query.get_or_404(resident_id)
    
    try:
        db.session.delete(resident)
        db.session.commit()
        flash('Resident deleted successfully!', 'success')
    except:
        db.session.rollback()
        flash('Error deleting resident. The resident may have associated records.', 'error')
    
    return redirect(url_for('residents.residents'))
