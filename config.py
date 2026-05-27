import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 300}
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASEDIR, 'app/static/uploads')
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB for property images
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.zoho.com')
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@edcarproperties.co.zw')
    ADMIN_PHONE = os.environ.get('ADMIN_PHONE', '+263772555263')
    LISTING_FEE = 20
    PAYMENT_DETAILS = os.environ.get('PAYMENT_DETAILS', """
EcoCash:     0772 555 263
CBZ Account: 0772 555 263 840
Contact:     +263 772 555 263 / +263 712 731 810
Reference:   Your Full Name
Amount:      $20 (Private Listing)
Note:        Edcar-managed properties list FREE
    """)


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'edcar.db')
    )


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
