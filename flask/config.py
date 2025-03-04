import os,random, string

class Config(object):
    # Set up the App SECRET_KEY
    SECRET_KEY  = os.getenv('SECRET_KEY')
    USE_CORS = True
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_HEADERS = 'Content-Type'
        


class ProductionConfig(Config):
    DEBUG = False
    
class DevelopmentConfig(Config):
    DEBUG = True
 

# Load all possible configurations
configurations = {
    'production': ProductionConfig,
    'development': DevelopmentConfig
}