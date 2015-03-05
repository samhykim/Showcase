# Allows us to set up different config environments for our app. 
# Often there are things that are going to be different between your local, 
# staging, and production setups. You’ll want to connect to different 
# databases, have different AWS keys, etc. Let’s set up a config file to 
# deal with the different environments.
import os

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
