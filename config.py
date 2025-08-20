import os

class Config:
    # Languages supported
    LANGUAGES = {
        '1': {'name': 'Rendille', 'code': 'en'},  # Using English for demo
        '2': {'name': 'Samburu', 'code': 'en'},   # Using English for demo
        '3': {'name': 'Swahili', 'code': 'en'}    # Using English for demo
    }
    
    # USSD code
    USSD_CODE = '*555#'
    
    # Risk factors and thresholds
    RISK_FACTORS = {
        'age': {'low': 18, 'high': 35},
        'prev_complications': True,
        'missed_anc': 2,
        'symptoms': ['bleeding', 'severe_pain', 'fever']
    }
    
    # File paths
    DATA_FILE = 'sample_data/sample_mothers.csv'
    VOICE_FILES_DIR = 'voice_messages/'
    
    # Dashboard settings
    DASHBOARD_PORT = 5000