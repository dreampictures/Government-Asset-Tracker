import os
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from slugify import slugify
from models import db, User, Job, Category, Subscriber, Notification, INDIAN_STATES, QUALIFICATIONS, JOB_TYPES
from werkzeug.utils import secure_filename
from extensions import cache

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, is_admin=True).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        flash('Invalid username or password.', 'error')
    return render_template('admin/login.html')


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@admin_bp.route('/')
@admin_required
def dashboard():
    total_jobs = Job.query.count()
    total_subscribers = Subscriber.query.count()
    total_categories = Category.query.count()
    total_notifications = Notification.query.count()
    recent_jobs = Job.query.order_by(Job.created_at.desc()).limit(10).all()
    scraped_jobs = Job.query.filter_by(is_scraped=True).order_by(Job.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html',
                           total_jobs=total_jobs,
                           total_subscribers=total_subscribers,
                           total_categories=total_categories,
                           total_notifications=total_notifications,
                           recent_jobs=recent_jobs,
                           scraped_jobs=scraped_jobs)


@admin_bp.route('/jobs')
@admin_required
def jobs_list():
    page = request.args.get('page', 1, type=int)
    jobs = Job.query.order_by(Job.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/jobs.html', jobs=jobs)


@admin_bp.route('/jobs/add', methods=['GET', 'POST'])
@admin_required
def add_job():
    categories = Category.query.all()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('Job title is required.', 'error')
            return render_template('admin/add_job.html', categories=categories,
                                   states=INDIAN_STATES, qualifications=QUALIFICATIONS, job_types=JOB_TYPES)

        slug = slugify(title)
        existing = Job.query.filter_by(slug=slug).first()
        if existing:
            slug = slug + '-' + str(int(datetime_now_ts()))

        notification_link = request.form.get('notification_link', '')
        if 'notification_pdf' in request.files:
            file = request.files['notification_pdf']
            if file and file.filename:
                filename = secure_filename(file.filename)
                upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))
                notification_link = f'/static/uploads/{filename}'

        job = Job(
            title=title,
            slug=slug,
            organization=request.form.get('organization', ''),
            department=request.form.get('department', ''),
            category_id=request.form.get('category_id', type=int),
            qualification=request.form.get('qualification', ''),
            state=request.form.get('state', 'All India'),
            total_posts=request.form.get('total_posts', ''),
            salary=request.form.get('salary', ''),
            application_fee=request.form.get('application_fee', ''),
            age_limit=request.form.get('age_limit', ''),
            selection_process=request.form.get('selection_process', ''),
            start_date=request.form.get('start_date', ''),
            last_date=request.form.get('last_date', ''),
            apply_link=request.form.get('apply_link', ''),
            notification_link=notification_link,
            official_website=request.form.get('official_website', ''),
            description=request.form.get('description', ''),
            how_to_apply=request.form.get('how_to_apply', ''),
            vacancy_details=request.form.get('vacancy_details', ''),
            job_type=request.form.get('job_type', 'latest_jobs'),
            is_published=bool(request.form.get('is_published'))
        )
        db.session.add(job)
        db.session.commit()

        try:
            from telegram_bot.bot import send_job_alert
            send_job_alert(job)
        except Exception:
            pass

        try:
            from routes.api import send_email_alerts
            send_email_alerts(job)
        except Exception:
            pass

        cache.clear()
        flash('Job added successfully!', 'success')
        return redirect(url_for('admin.jobs_list'))

    return render_template('admin/add_job.html', categories=categories,
                           states=INDIAN_STATES, qualifications=QUALIFICATIONS, job_types=JOB_TYPES)


@admin_bp.route('/jobs/edit/<int:job_id>', methods=['GET', 'POST'])
@admin_required
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    categories = Category.query.all()

    if request.method == 'POST':
        job.title = request.form.get('title', job.title)
        job.organization = request.form.get('organization', '')
        job.department = request.form.get('department', '')
        job.category_id = request.form.get('category_id', type=int)
        job.qualification = request.form.get('qualification', '')
        job.state = request.form.get('state', 'All India')
        job.total_posts = request.form.get('total_posts', '')
        job.salary = request.form.get('salary', '')
        job.application_fee = request.form.get('application_fee', '')
        job.age_limit = request.form.get('age_limit', '')
        job.selection_process = request.form.get('selection_process', '')
        job.start_date = request.form.get('start_date', '')
        job.last_date = request.form.get('last_date', '')
        job.apply_link = request.form.get('apply_link', '')
        job.official_website = request.form.get('official_website', '')
        job.description = request.form.get('description', '')
        job.how_to_apply = request.form.get('how_to_apply', '')
        job.vacancy_details = request.form.get('vacancy_details', '')
        job.job_type = request.form.get('job_type', 'latest_jobs')
        job.is_published = bool(request.form.get('is_published'))

        notification_link = request.form.get('notification_link', job.notification_link)
        if 'notification_pdf' in request.files:
            file = request.files['notification_pdf']
            if file and file.filename:
                filename = secure_filename(file.filename)
                upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))
                notification_link = f'/static/uploads/{filename}'
        job.notification_link = notification_link

        db.session.commit()
        cache.clear()
        flash('Job updated successfully!', 'success')
        return redirect(url_for('admin.jobs_list'))

    return render_template('admin/edit_job.html', job=job, categories=categories,
                           states=INDIAN_STATES, qualifications=QUALIFICATIONS, job_types=JOB_TYPES)


@admin_bp.route('/jobs/delete/<int:job_id>', methods=['POST'])
@admin_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    Notification.query.filter_by(job_id=job_id).update({'job_id': None})
    db.session.delete(job)
    db.session.commit()
    cache.clear()
    flash('Job deleted successfully!', 'success')
    return redirect(url_for('admin.jobs_list'))


@admin_bp.route('/categories')
@admin_required
def categories_list():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/categories/add', methods=['POST'])
@admin_required
def add_category():
    name = request.form.get('name', '').strip()
    if not name:
        flash('Category name is required.', 'error')
        return redirect(url_for('admin.categories_list'))
    slug = slugify(name)
    existing = Category.query.filter_by(slug=slug).first()
    if existing:
        flash('Category already exists.', 'error')
        return redirect(url_for('admin.categories_list'))
    cat = Category(name=name, slug=slug, description=request.form.get('description', ''))
    db.session.add(cat)
    db.session.commit()
    cache.clear()
    flash('Category added!', 'success')
    return redirect(url_for('admin.categories_list'))


@admin_bp.route('/categories/delete/<int:cat_id>', methods=['POST'])
@admin_required
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()
    cache.clear()
    flash('Category deleted!', 'success')
    return redirect(url_for('admin.categories_list'))


@admin_bp.route('/subscribers')
@admin_required
def subscribers_list():
    page = request.args.get('page', 1, type=int)
    subscribers = Subscriber.query.order_by(Subscriber.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/subscribers.html', subscribers=subscribers)


@admin_bp.route('/subscribers/delete/<int:sub_id>', methods=['POST'])
@admin_required
def delete_subscriber(sub_id):
    sub = Subscriber.query.get_or_404(sub_id)
    db.session.delete(sub)
    db.session.commit()
    flash('Subscriber removed!', 'success')
    return redirect(url_for('admin.subscribers_list'))


@admin_bp.route('/generate-content/<int:job_id>', methods=['POST'])
@admin_required
def generate_content(job_id):
    job = Job.query.get_or_404(job_id)
    try:
        from ai_module.generator import generate_job_article
        content = generate_job_article(job)
        if content:
            job.description = content
            db.session.commit()
            flash('AI content generated successfully!', 'success')
        else:
            flash('Failed to generate content.', 'error')
    except Exception as e:
        flash(f'Error generating content: {str(e)}', 'error')
    return redirect(url_for('admin.edit_job', job_id=job_id))


@admin_bp.route('/run-scraper', methods=['POST'])
@admin_required
def run_scraper():
    try:
        from scraper.scraper import run_scraper as do_scrape
        count = do_scrape()
        cache.clear()
        flash(f'Scraper completed! {count} new jobs added.', 'success')
    except Exception as e:
        flash(f'Scraper error: {str(e)}', 'error')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/notifications')
@admin_required
def notifications_list():
    page = request.args.get('page', 1, type=int)
    notifications = Notification.query.order_by(Notification.created_at.desc()).paginate(page=page, per_page=20)
    jobs = Job.query.order_by(Job.title).all()
    return render_template('admin/notifications.html', notifications=notifications, jobs=jobs)


@admin_bp.route('/notifications/add', methods=['POST'])
@admin_required
def add_notification():
    title = request.form.get('title', '').strip()
    if not title:
        flash('Notification title is required.', 'error')
        return redirect(url_for('admin.notifications_list'))

    file_path = ''
    if 'notification_file' in request.files:
        file = request.files['notification_file']
        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, filename))
            file_path = f'/static/uploads/{filename}'

    notification = Notification(
        title=title,
        message=request.form.get('message', ''),
        type=request.form.get('type', 'system'),
        file_path=file_path,
        job_id=request.form.get('job_id', type=int) or None,
        status='active'
    )
    db.session.add(notification)
    db.session.commit()
    flash('Notification added successfully!', 'success')
    return redirect(url_for('admin.notifications_list'))


@admin_bp.route('/notifications/delete/<int:notif_id>', methods=['POST'])
@admin_required
def delete_notification(notif_id):
    notification = Notification.query.get_or_404(notif_id)
    db.session.delete(notification)
    db.session.commit()
    flash('Notification deleted!', 'success')
    return redirect(url_for('admin.notifications_list'))


def datetime_now_ts():
    from datetime import datetime
    return datetime.utcnow().timestamp()
