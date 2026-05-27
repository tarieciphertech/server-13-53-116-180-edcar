from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os

mail = Mail()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    try:
        from dotenv import load_dotenv
        load_dotenv('/etc/edcar.env')
        load_dotenv()
    except ImportError:
        pass

    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        from config import ProductionConfig
        app.config.from_object(ProductionConfig)
    else:
        from config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)

    from app.models import db, User
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.public import public
    from app.routes.auth import auth
    from app.routes.agent import agent
    from app.routes.admin import admin_bp

    app.register_blueprint(public)
    app.register_blueprint(auth)
    app.register_blueprint(agent)
    app.register_blueprint(admin_bp)

    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'properties'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'proofs'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'projects'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'cars'), exist_ok=True)

    with app.app_context():
        db.create_all()
        create_default_admin(app)

    return app


def create_default_admin(app):
    with app.app_context():
        from app.models import User, db
        from werkzeug.security import generate_password_hash
        if not User.query.filter_by(role='admin').first():
            admin = User(
                name='Administrator',
                email='admin@edcarproperties.co.zw',
                phone='+263772555263',
                password=generate_password_hash('admin1234'),
                role='admin',
                is_approved=True
            )
            db.session.add(admin)
            db.session.commit()
            print('✅ Admin created: admin@edcarproperties.co.zw / admin1234')
