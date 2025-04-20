from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from datetime import datetime, timedelta
from models.resident import Resident
from models.official import Official
from models.document import Document
from models.project import Project
from sqlalchemy import func

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/dashboard-stats')
def dashboard_stats():
    # Get counts for dashboard
    resident_count = Resident.query.count()
    
    # Count current officials (where end_term is in the future)
    official_count = Official.query.filter(Official.end_term >= datetime.now().date()).count()
    
    # Count documents issued this month
    first_day = datetime.now().replace(day=1).date()
    document_count = Document.query.filter(Document.issue_date >= first_day).count()
    
    # Count active projects
    project_count = Project.query.filter(Project.status.in_(['Planned', 'Ongoing'])).count()
    
    return jsonify({
        'residents': resident_count,
        'officials': official_count,
        'documents': document_count,
        'projects': project_count
    })

@main.route('/api/recent-documents')
def recent_documents():
    # Get 5 most recent documents with resident info
    recent_docs = Document.query.order_by(Document.issue_date.desc()).limit(5).all()
    
    documents = []
    for doc in recent_docs:
        # Assign color based on document type
        type_color = "bg-blue-100 text-blue-800"
        if "clearance" in doc.document_type.lower():
            type_color = "bg-green-100 text-green-800"
        elif "indigency" in doc.document_type.lower():
            type_color = "bg-yellow-100 text-yellow-800"
        elif "business" in doc.document_type.lower():
            type_color = "bg-purple-100 text-purple-800"
            
        documents.append({
            'id': doc.id,
            'document_type': doc.document_type,
            'type_color': type_color,
            'resident_name': f"{doc.resident.first_name} {doc.resident.last_name}",
            'resident_id': doc.resident_id,
            'issue_date': doc.issue_date.strftime('%b %d, %Y')
        })
    
    return jsonify({'documents': documents})

@main.route('/user-guide')
def user_guide():
    return render_template('user_guide.html')

@main.route('/contact-support', methods=['GET', 'POST'])
def contact_support():
    if request.method == 'POST':
        # In a real application, you would process the form data here
        # This could include sending an email or storing the request in the database
        flash('Your support request has been submitted. We will get back to you as soon as possible.', 'success')
        return redirect(url_for('main.contact_support'))
    
    return render_template('contact_support.html')
