from flask import Blueprint, render_template, request, url_for, Response
from slugify import slugify
from models import db, Job, Category, Subscriber, INDIAN_STATES, QUALIFICATIONS, JOB_TYPES
from datetime import datetime
import xml.etree.ElementTree as ET

main_bp = Blueprint('main', __name__)

STATE_SLUGS = {slugify(s + ' govt jobs'): s for s in INDIAN_STATES}
QUAL_SLUGS = {slugify(q + ' jobs'): q for q in QUALIFICATIONS}


@main_bp.route('/')
def index():
    latest_jobs = Job.query.filter_by(is_published=True, job_type='latest_jobs').order_by(Job.created_at.desc()).limit(12).all()
    trending_jobs = Job.query.filter_by(is_published=True).order_by(Job.updated_at.desc(), Job.views.desc()).limit(8).all()
    popular_jobs = Job.query.filter_by(is_published=True).order_by(Job.views.desc()).limit(8).all()
    admit_cards = Job.query.filter_by(is_published=True, job_type='admit_card').order_by(Job.created_at.desc()).limit(6).all()
    results = Job.query.filter_by(is_published=True, job_type='result').order_by(Job.created_at.desc()).limit(6).all()
    answer_keys = Job.query.filter_by(is_published=True, job_type='answer_key').order_by(Job.created_at.desc()).limit(6).all()
    syllabus = Job.query.filter_by(is_published=True, job_type='syllabus').order_by(Job.created_at.desc()).limit(6).all()
    admissions = Job.query.filter_by(is_published=True, job_type='admission').order_by(Job.created_at.desc()).limit(6).all()
    categories = Category.query.all()
    ticker_jobs = Job.query.filter_by(is_published=True).order_by(Job.created_at.desc()).limit(10).all()

    return render_template('index.html',
                           latest_jobs=latest_jobs,
                           trending_jobs=trending_jobs,
                           popular_jobs=popular_jobs,
                           admit_cards=admit_cards,
                           results=results,
                           answer_keys=answer_keys,
                           syllabus=syllabus,
                           admissions=admissions,
                           categories=categories,
                           ticker_jobs=ticker_jobs,
                           states=INDIAN_STATES,
                           qualifications=QUALIFICATIONS,
                           state_slugs=STATE_SLUGS,
                           qual_slugs=QUAL_SLUGS)


@main_bp.route('/job/<slug>')
def job_detail(slug):
    job = Job.query.filter_by(slug=slug, is_published=True).first_or_404()
    job.views = (job.views or 0) + 1
    db.session.commit()
    related_jobs = Job.query.filter(
        Job.category_id == job.category_id,
        Job.id != job.id,
        Job.is_published == True
    ).order_by(Job.created_at.desc()).limit(5).all()
    return render_template('job_detail.html', job=job, related_jobs=related_jobs)


@main_bp.route('/category/<slug>')
def category_page(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    jobs = Job.query.filter_by(
        category_id=category.id, is_published=True
    ).order_by(Job.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('category.html', category=category, jobs=jobs)


@main_bp.route('/state/<slug>')
def state_page(slug):
    state_name = STATE_SLUGS.get(slug)
    if not state_name:
        from flask import abort
        abort(404)
    page = request.args.get('page', 1, type=int)
    jobs = Job.query.filter_by(
        state=state_name, is_published=True
    ).order_by(Job.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('state.html', state_name=state_name, slug=slug, jobs=jobs)


@main_bp.route('/qualification/<slug>')
def qualification_page(slug):
    qual_name = QUAL_SLUGS.get(slug)
    if not qual_name:
        from flask import abort
        abort(404)
    page = request.args.get('page', 1, type=int)
    jobs = Job.query.filter_by(
        qualification=qual_name, is_published=True
    ).order_by(Job.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('qualification.html', qual_name=qual_name, slug=slug, jobs=jobs)


@main_bp.route('/search')
def search():
    query = request.args.get('q', '')
    state = request.args.get('state', '')
    qualification = request.args.get('qualification', '')
    category = request.args.get('category', '')
    organization = request.args.get('organization', '')
    page = request.args.get('page', 1, type=int)

    jobs_query = Job.query.filter_by(is_published=True)

    if query:
        jobs_query = jobs_query.filter(
            db.or_(
                Job.title.ilike(f'%{query}%'),
                Job.organization.ilike(f'%{query}%'),
                Job.department.ilike(f'%{query}%'),
                Job.description.ilike(f'%{query}%')
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
    if organization:
        jobs_query = jobs_query.filter(Job.organization.ilike(f'%{organization}%'))

    jobs = jobs_query.order_by(Job.created_at.desc()).paginate(page=page, per_page=20)
    categories = Category.query.all()

    return render_template('search.html',
                           jobs=jobs, query=query, state=state,
                           qualification=qualification, category=category,
                           organization=organization,
                           categories=categories,
                           states=INDIAN_STATES,
                           qualifications=QUALIFICATIONS)


@main_bp.route('/subscribe', methods=['POST'])
def subscribe():
    from flask import flash, redirect
    email = request.form.get('email', '').strip()
    if not email:
        flash('Please enter a valid email address.', 'error')
        return redirect(request.referrer or url_for('main.index'))

    existing = Subscriber.query.filter_by(email=email).first()
    if existing:
        flash('You are already subscribed!', 'info')
    else:
        sub = Subscriber(email=email)
        db.session.add(sub)
        db.session.commit()
        flash('Successfully subscribed to job alerts!', 'success')

    return redirect(request.referrer or url_for('main.index'))


@main_bp.route('/sitemap.xml')
def sitemap():
    pages = []
    now = datetime.utcnow().strftime('%Y-%m-%d')

    pages.append({'loc': url_for('main.index', _external=True), 'lastmod': now, 'priority': '1.0'})

    jobs = Job.query.filter_by(is_published=True).all()
    for job in jobs:
        pages.append({
            'loc': url_for('main.job_detail', slug=job.slug, _external=True),
            'lastmod': (job.updated_at or job.created_at).strftime('%Y-%m-%d'),
            'priority': '0.8'
        })

    categories = Category.query.all()
    for cat in categories:
        pages.append({
            'loc': url_for('main.category_page', slug=cat.slug, _external=True),
            'lastmod': now,
            'priority': '0.7'
        })

    for slug in STATE_SLUGS:
        pages.append({
            'loc': url_for('main.state_page', slug=slug, _external=True),
            'lastmod': now,
            'priority': '0.6'
        })

    for slug in QUAL_SLUGS:
        pages.append({
            'loc': url_for('main.qualification_page', slug=slug, _external=True),
            'lastmod': now,
            'priority': '0.6'
        })

    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for page in pages:
        xml_content += '  <url>\n'
        xml_content += f'    <loc>{page["loc"]}</loc>\n'
        xml_content += f'    <lastmod>{page["lastmod"]}</lastmod>\n'
        xml_content += f'    <priority>{page["priority"]}</priority>\n'
        xml_content += '  </url>\n'
    xml_content += '</urlset>'

    return Response(xml_content, mimetype='application/xml')


@main_bp.route('/robots.txt')
def robots():
    content = f"""User-agent: *
Allow: /

Sitemap: {url_for('main.sitemap', _external=True)}

Disallow: /admin/
"""
    return Response(content, mimetype='text/plain')


@main_bp.route('/jobs/<job_type>')
def jobs_by_type(job_type):
    if job_type not in JOB_TYPES:
        from flask import abort
        abort(404)
    type_names = {
        'latest_jobs': 'Latest Jobs',
        'admit_card': 'Admit Cards',
        'result': 'Results',
        'answer_key': 'Answer Keys',
        'syllabus': 'Syllabus',
        'admission': 'Admissions'
    }
    page = request.args.get('page', 1, type=int)
    jobs = Job.query.filter_by(
        is_published=True, job_type=job_type
    ).order_by(Job.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('jobs_by_type.html',
                           jobs=jobs, job_type=job_type,
                           type_name=type_names.get(job_type, job_type))
