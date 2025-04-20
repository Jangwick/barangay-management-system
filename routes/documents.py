from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.document import Document
from models.resident import Resident
from models import db
from datetime import datetime
from utils import role_required

documents_bp = Blueprint('documents', __name__, url_prefix='/documents')

@documents_bp.route('/')
@login_required
def documents():
    all_documents = Document.query.order_by(Document.issue_date.desc()).all()
    return render_template('documents/index.html', documents=all_documents)

@documents_bp.route('/issue', methods=['GET', 'POST'])
@login_required
def issue_document():
    # Pre-select resident if resident_id is provided in the URL
    resident_id = request.args.get('resident_id', None)
    selected_resident = None
    
    if resident_id:
        selected_resident = Resident.query.get(resident_id)
    
    if request.method == 'POST':
        resident_id = request.form['resident_id']
        document_type = request.form['document_type']
        purpose = request.form['purpose']
        
        new_document = Document(
            resident_id=resident_id,
            document_type=document_type,
            purpose=purpose,
            issue_date=datetime.now().date()
        )
        
        db.session.add(new_document)
        db.session.commit()
        flash('Document issued successfully!', 'success')
        return redirect(url_for('documents.view_document', document_id=new_document.id))
        
    residents = Resident.query.order_by(Resident.last_name, Resident.first_name).all()
    return render_template('documents/issue.html', residents=residents, selected_resident=selected_resident)

@documents_bp.route('/<int:document_id>')
@login_required
def view_document(document_id):
    document = Document.query.get_or_404(document_id)
    return render_template('documents/view.html', document=document)

@documents_bp.route('/<int:document_id>/print')
@login_required
def print_document(document_id):
    document = Document.query.get_or_404(document_id)
    return render_template('documents/print.html', document=document)

@documents_bp.route('/<int:document_id>/delete', methods=['POST'])
@login_required
@role_required('staff')  # Only staff and admin can delete
def delete_document(document_id):
    document = Document.query.get_or_404(document_id)
    
    try:
        db.session.delete(document)
        db.session.commit()
        flash('Document deleted successfully!', 'success')
    except:
        db.session.rollback()
        flash('Error deleting document.', 'error')
    
    return redirect(url_for('documents.documents'))
