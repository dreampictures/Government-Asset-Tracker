import os
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from models import db, User, Category
from config import Config
from slugify import slugify


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

    db.init_app(app)
    csrf = CSRFProtect(app)

    login_manager = LoginManager()
    login_manager.login_view = 'admin.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.main import main_bp, STATE_SLUGS, QUAL_SLUGS
    from routes.admin import admin_bp
    from routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    csrf.exempt(api_bp)

    @app.context_processor
    def inject_globals():
        def get_categories():
            return Category.query.all()

        top_states = ['Punjab', 'Uttar Pradesh', 'Bihar', 'Haryana', 'Rajasthan',
                      'Maharashtra', 'Madhya Pradesh', 'Delhi', 'Gujarat', 'Tamil Nadu',
                      'Karnataka', 'West Bengal']

        def get_top_states():
            return [(slugify(s + ' govt jobs'), s) for s in top_states]

        def get_qualifications():
            from models import QUALIFICATIONS
            return [(slugify(q + ' jobs'), q) for q in QUALIFICATIONS]

        return dict(
            get_categories=get_categories,
            get_top_states=get_top_states,
            get_qualifications=get_qualifications
        )

    with app.app_context():
        db.create_all()
        seed_data()
        setup_scheduler(app)

    return app


def seed_data():
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@indiajobportal.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

    default_categories = [
        ('Central Govt Jobs', 'central-govt-jobs'),
        ('State Govt Jobs', 'state-govt-jobs'),
        ('Bank Jobs', 'bank-jobs'),
        ('Railway Jobs', 'railway-jobs'),
        ('Police Jobs', 'police-jobs'),
        ('Defence Jobs', 'defence-jobs'),
        ('Teaching Jobs', 'teaching-jobs'),
        ('Engineering Jobs', 'engineering-jobs'),
        ('Medical Jobs', 'medical-jobs'),
    ]
    for name, slug in default_categories:
        if not Category.query.filter_by(slug=slug).first():
            db.session.add(Category(name=name, slug=slug))
    db.session.commit()

    from models import Job
    if Job.query.count() == 0:
        sample_jobs = [
            {
                'title': 'SSC GD Constable Recruitment 2026',
                'slug': 'ssc-gd-constable-recruitment-2026',
                'organization': 'Staff Selection Commission',
                'department': 'Ministry of Home Affairs',
                'qualification': '10th Pass',
                'state': 'All India',
                'total_posts': '25000',
                'salary': 'Rs. 21,700 - 69,100',
                'application_fee': 'General: Rs. 100, SC/ST/Women: Nil',
                'age_limit': '18-23 Years',
                'start_date': '01-03-2026',
                'last_date': '31-03-2026',
                'apply_link': 'https://ssc.nic.in',
                'notification_link': 'https://ssc.nic.in',
                'official_website': 'https://ssc.nic.in',
                'selection_process': 'Written Exam, Physical Test, Medical Test',
                'job_type': 'latest_jobs',
                'category_slug': 'central-govt-jobs',
                'views': 1250,
            },
            {
                'title': 'IBPS PO Recruitment 2026',
                'slug': 'ibps-po-recruitment-2026',
                'organization': 'Institute of Banking Personnel Selection',
                'department': 'Banking Sector',
                'qualification': 'Graduation',
                'state': 'All India',
                'total_posts': '4500',
                'salary': 'Rs. 36,000 - 63,840',
                'application_fee': 'General: Rs. 850, SC/ST: Rs. 175',
                'age_limit': '20-30 Years',
                'start_date': '15-02-2026',
                'last_date': '15-03-2026',
                'apply_link': 'https://ibps.in',
                'notification_link': 'https://ibps.in',
                'official_website': 'https://ibps.in',
                'selection_process': 'Prelims, Mains, Interview',
                'job_type': 'latest_jobs',
                'category_slug': 'bank-jobs',
                'views': 2100,
            },
            {
                'title': 'RRB NTPC Recruitment 2026',
                'slug': 'rrb-ntpc-recruitment-2026',
                'organization': 'Railway Recruitment Board',
                'department': 'Indian Railways',
                'qualification': '12th Pass',
                'state': 'All India',
                'total_posts': '35000',
                'salary': 'Rs. 19,900 - 63,200',
                'application_fee': 'General: Rs. 500, SC/ST: Rs. 250',
                'age_limit': '18-33 Years',
                'start_date': '01-03-2026',
                'last_date': '30-03-2026',
                'apply_link': 'https://www.rrbcdg.gov.in',
                'notification_link': 'https://www.rrbcdg.gov.in',
                'official_website': 'https://www.rrbcdg.gov.in',
                'selection_process': 'CBT-1, CBT-2, Typing/Skill Test',
                'job_type': 'latest_jobs',
                'category_slug': 'railway-jobs',
                'views': 3500,
            },
            {
                'title': 'UP Police Constable Recruitment 2026',
                'slug': 'up-police-constable-recruitment-2026',
                'organization': 'UP Police Recruitment Board',
                'department': 'Uttar Pradesh Police',
                'qualification': '12th Pass',
                'state': 'Uttar Pradesh',
                'total_posts': '60000',
                'salary': 'Rs. 21,700 - 69,100',
                'application_fee': 'General: Rs. 400, SC/ST: Rs. 200',
                'age_limit': '18-25 Years',
                'start_date': '10-03-2026',
                'last_date': '10-04-2026',
                'apply_link': 'https://uppbpb.gov.in',
                'notification_link': 'https://uppbpb.gov.in',
                'official_website': 'https://uppbpb.gov.in',
                'selection_process': 'Written Exam, Physical Test, Document Verification',
                'job_type': 'latest_jobs',
                'category_slug': 'police-jobs',
                'views': 5200,
            },
            {
                'title': 'Indian Army Agniveer Recruitment 2026',
                'slug': 'indian-army-agniveer-recruitment-2026',
                'organization': 'Indian Army',
                'department': 'Ministry of Defence',
                'qualification': '10th Pass',
                'state': 'All India',
                'total_posts': '46000',
                'salary': 'Rs. 30,000 per month',
                'application_fee': 'Nil',
                'age_limit': '17.5 - 23 Years',
                'start_date': '01-02-2026',
                'last_date': '28-02-2026',
                'apply_link': 'https://joinindianarmy.nic.in',
                'notification_link': 'https://joinindianarmy.nic.in',
                'official_website': 'https://joinindianarmy.nic.in',
                'selection_process': 'Online Exam, Physical Test, Medical',
                'job_type': 'latest_jobs',
                'category_slug': 'defence-jobs',
                'views': 4100,
            },
            {
                'title': 'Punjab PSSSB Clerk Recruitment 2026',
                'slug': 'punjab-psssb-clerk-recruitment-2026',
                'organization': 'PSSSB Punjab',
                'department': 'Punjab Government',
                'qualification': 'Graduation',
                'state': 'Punjab',
                'total_posts': '3000',
                'salary': 'Rs. 19,900 - 63,200',
                'application_fee': 'General: Rs. 600, SC/ST: Rs. 300',
                'age_limit': '18-37 Years',
                'start_date': '05-03-2026',
                'last_date': '05-04-2026',
                'apply_link': 'https://sssb.punjab.gov.in',
                'notification_link': 'https://sssb.punjab.gov.in',
                'official_website': 'https://sssb.punjab.gov.in',
                'selection_process': 'Written Exam, Typing Test',
                'job_type': 'latest_jobs',
                'category_slug': 'state-govt-jobs',
                'views': 800,
            },
            {
                'title': 'SSC CGL 2026 Admit Card Released',
                'slug': 'ssc-cgl-2026-admit-card',
                'organization': 'Staff Selection Commission',
                'department': 'Central Government',
                'qualification': 'Graduation',
                'state': 'All India',
                'total_posts': '8000',
                'salary': 'Rs. 25,500 - 81,100',
                'start_date': '01-03-2026',
                'last_date': '20-03-2026',
                'apply_link': 'https://ssc.nic.in',
                'notification_link': 'https://ssc.nic.in',
                'official_website': 'https://ssc.nic.in',
                'job_type': 'admit_card',
                'category_slug': 'central-govt-jobs',
                'views': 950,
            },
            {
                'title': 'IBPS Clerk 2025 Result Declared',
                'slug': 'ibps-clerk-2025-result',
                'organization': 'IBPS',
                'department': 'Banking',
                'qualification': 'Graduation',
                'state': 'All India',
                'total_posts': '6000',
                'apply_link': 'https://ibps.in',
                'notification_link': 'https://ibps.in',
                'official_website': 'https://ibps.in',
                'job_type': 'result',
                'category_slug': 'bank-jobs',
                'views': 1800,
            },
            {
                'title': 'CTET 2026 Answer Key Published',
                'slug': 'ctet-2026-answer-key',
                'organization': 'CBSE',
                'department': 'Education',
                'qualification': 'B.Ed',
                'state': 'All India',
                'total_posts': '',
                'apply_link': 'https://ctet.nic.in',
                'notification_link': 'https://ctet.nic.in',
                'official_website': 'https://ctet.nic.in',
                'job_type': 'answer_key',
                'category_slug': 'teaching-jobs',
                'views': 600,
            },
            {
                'title': 'AIIMS MBBS Admission 2026',
                'slug': 'aiims-mbbs-admission-2026',
                'organization': 'AIIMS',
                'department': 'Health & Family Welfare',
                'qualification': '12th Pass',
                'state': 'All India',
                'total_posts': '1200',
                'salary': '',
                'application_fee': 'General: Rs. 1500, SC/ST: Rs. 1200',
                'age_limit': '17-25 Years',
                'start_date': '01-01-2026',
                'last_date': '31-01-2026',
                'apply_link': 'https://aiimsexams.ac.in',
                'notification_link': 'https://aiimsexams.ac.in',
                'official_website': 'https://aiimsexams.ac.in',
                'job_type': 'admission',
                'category_slug': 'medical-jobs',
                'views': 2200,
            },
        ]

        for jd in sample_jobs:
            cat = Category.query.filter_by(slug=jd.pop('category_slug', '')).first()
            job = Job(
                **jd,
                category_id=cat.id if cat else None,
                is_published=True
            )
            db.session.add(job)
        db.session.commit()


def setup_scheduler(app):
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        scheduler = BackgroundScheduler()

        def scheduled_scrape():
            with app.app_context():
                try:
                    from scraper.scraper import run_scraper
                    run_scraper()
                except Exception as e:
                    print(f"Scheduled scraper error: {e}")

        scheduler.add_job(func=scheduled_scrape, trigger='interval', hours=24, id='daily_scraper')
        scheduler.start()
    except Exception as e:
        print(f"Scheduler setup error: {e}")


app = create_app()

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
