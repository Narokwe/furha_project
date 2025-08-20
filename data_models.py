from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
import pandas as pd

@dataclass
class Mother:
    phone_number: str
    national_id: str
    language: str
    edd: datetime  # Expected Due Date
    lmp: datetime  # Last Menstrual Period
    age: int
    prev_pregnancies: int
    prev_complications: bool
    risk_level: str = "low"
    anc_visits: int = 0
    missed_anc: int = 0
    last_contact: Optional[datetime] = None
    symptoms: List[str] = None
    
    def __post_init__(self):
        if self.symptoms is None:
            self.symptoms = []
    
    def to_dict(self):
        return {
            'phone_number': self.phone_number,
            'national_id': self.national_id,
            'language': self.language,
            'edd': self.edd.strftime('%Y-%m-%d'),
            'lmp': self.lmp.strftime('%Y-%m-%d'),
            'age': self.age,
            'prev_pregnancies': self.prev_pregnancies,
            'prev_complications': self.prev_complications,
            'risk_level': self.risk_level,
            'anc_visits': self.anc_visits,
            'missed_anc': self.missed_anc,
            'last_contact': self.last_contact.strftime('%Y-%m-%d') if self.last_contact else None,
            'symptoms': ','.join(self.symptoms) if self.symptoms else ''
        }

class MotherRegistry:
    def __init__(self, data_file='sample_data/sample_mothers.csv'):
        self.data_file = data_file
        self.mothers = {}
        self.load_data()
    
    def load_data(self):
        try:
            df = pd.read_csv(self.data_file)
            for _, row in df.iterrows():
                mother = Mother(
                    phone_number=row['phone_number'],
                    national_id=row['national_id'],
                    language=row['language'],
                    edd=datetime.strptime(row['edd'], '%Y-%m-%d'),
                    lmp=datetime.strptime(row['lmp'], '%Y-%m-%d'),
                    age=row['age'],
                    prev_pregnancies=row['prev_pregnancies'],
                    prev_complications=row['prev_complications'] == 'True',
                    risk_level=row.get('risk_level', 'low'),
                    anc_visits=row.get('anc_visits', 0),
                    missed_anc=row.get('missed_anc', 0),
                    symptoms=row.get('symptoms', '').split(',') if pd.notna(row.get('symptoms')) else []
                )
                if pd.notna(row.get('last_contact')):
                    mother.last_contact = datetime.strptime(row['last_contact'], '%Y-%m-%d')
                self.mothers[mother.phone_number] = mother
        except FileNotFoundError:
            # Create sample data if file doesn't exist
            self.create_sample_data()
    
    def create_sample_data(self):
        import os
        os.makedirs('sample_data', exist_ok=True)
        
        sample_mothers = [
            Mother(
                phone_number="+254711123456",
                national_id="12345678",
                language="Samburu",
                edd=datetime.now() + timedelta(days=120),
                lmp=datetime.now() - timedelta(days=90),
                age=28,
                prev_pregnancies=2,
                prev_complications=False
            ),
            Mother(
                phone_number="+254722987654",
                national_id="87654321",
                language="Rendille",
                edd=datetime.now() + timedelta(days=60),
                lmp=datetime.now() - timedelta(days=150),
                age=17,
                prev_pregnancies=0,
                prev_complications=True,
                symptoms=['bleeding']
            )
        ]
        
        df = pd.DataFrame([m.to_dict() for m in sample_mothers])
        df.to_csv(self.data_file, index=False)
        self.load_data()
    
    def add_mother(self, mother):
        self.mothers[mother.phone_number] = mother
        self.save_data()
    
    def save_data(self):
        df = pd.DataFrame([m.to_dict() for m in self.mothers.values()])
        df.to_csv(self.data_file, index=False)
    
    def get_mother(self, phone_number):
        return self.mothers.get(phone_number)
    
    def update_mother(self, phone_number, **kwargs):
        mother = self.get_mother(phone_number)
        if mother:
            for key, value in kwargs.items():
                setattr(mother, key, value)
            self.save_data()
            return True
        return False