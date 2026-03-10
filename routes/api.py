import os
import requests as http_requests
from flask import Blueprint, jsonify, request
from models import db, Job, Category, Subscriber, INDIAN_STATES, QUALIFICATIONS

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/search')
def search_jobs():
    query = request.args.get('q', '')
    state = request.args.get('state', '')
    qualification = request.args.get('qualification', '')
    category = request.args.get('category', '')
    page = request.args.get('page', 1, type=int)

    jobs_query = Job.query.filter_by(is_published=True)

    if query:
        jobs_query = jobs_query.filter(
            db.or_(
                Job.title.ilike(f'%{query}%'),
                Job.organization.ilike(f'%{query}%')
            )
        )
    if state:
        jobs_query = jobs_query.filter_by(state=state)
    if qualification:
        jobs_query = jobs_query.filter_by(qualification=qualification)
    if category:
        cat = Category.query.filter_by(slug=category).first()
        if cat:
            jobs_query = jobs_query.filter_by(category_id=cat.id)

    jobs = jobs_query.order_by(Job.created_at.desc()).paginate(page=page, per_page=20)

    return jsonify({
        'jobs': [{
            'id': j.id,
            'title': j.title,
            'slug': j.slug,
            'organization': j.organization,
            'total_posts': j.total_posts,
            'start_date': j.start_date,
            'last_date': j.last_date,
            'state': j.state,
            'qualification': j.qualification
        } for j in jobs.items],
        'total': jobs.total,
        'pages': jobs.pages,
        'page': jobs.page
    })


@api_bp.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    existing = Subscriber.query.filter_by(email=email).first()
    if existing:
        return jsonify({'message': 'Already subscribed'}), 200

    sub = Subscriber(email=email)
    db.session.add(sub)
    db.session.commit()
    return jsonify({'message': 'Subscribed successfully'}), 201


def send_email_alerts(job):
    resend_api_key = os.environ.get('RESEND_API_KEY', '')
    from_email = os.environ.get('RESEND_FROM_EMAIL', 'onboarding@resend.dev')

    if not resend_api_key:
        print("Resend API key not configured. Skipping email alerts.")
        return

    subscribers = Subscriber.query.filter_by(is_active=True).all()
    if not subscribers:
        return

    subject = f"New Job Alert: {job.title}"
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #1a237e; color: white; padding: 20px; text-align: center;">
            <h1 style="margin: 0;">New Job Alert</h1>
        </div>
        <div style="padding: 20px; background: #f5f5f5;">
            <h2 style="color: #1a237e;">{job.title}</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="padding: 8px; font-weight: bold;">Organization:</td><td style="padding: 8px;">{job.organization}</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Total Posts:</td><td style="padding: 8px;">{job.total_posts}</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Last Date:</td><td style="padding: 8px;">{job.last_date}</td></tr>
                <tr><td style="padding: 8px; font-weight: bold;">Qualification:</td><td style="padding: 8px;">{job.qualification}</td></tr>
            </table>
            <div style="text-align: center; margin-top: 20px;">
                <a href="{job.apply_link}" style="background: #ff6f00; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">Apply Now</a>
            </div>
        </div>
        <div style="padding: 10px; text-align: center; color: #666; font-size: 12px;">
            <p>IndiaJobPortal - Your Gateway to Government Jobs</p>
        </div>
    </body>
    </html>
    """

    for sub in subscribers:
        try:
            response = http_requests.post(
                'https://api.resend.com/emails',
                headers={
                    'Authorization': f'Bearer {resend_api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'from': from_email,
                    'to': [sub.email],
                    'subject': subject,
                    'html': html_body
                },
                timeout=10
            )
            if response.status_code in (200, 201):
                print(f"Email sent to {sub.email}")
            else:
                print(f"Email error for {sub.email}: {response.text}")
        except Exception as e:
            print(f"Email error for {sub.email}: {e}")
