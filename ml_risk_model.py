import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from data_models import MotherRegistry
import joblib

class RiskAssessmentModel:
    def __init__(self):
        self.model = None
        self.label_encoders = {}
        self.features = ['age', 'prev_pregnancies', 'prev_complications', 'missed_anc', 'symptoms_count']
        self.target = 'risk_level'
    
    def prepare_data(self, df):
        """Prepare data for model training"""
        # Create a copy to avoid modifying original data
        data = df.copy()
        
        # Encode boolean fields
        data['prev_complications'] = data['prev_complications'].astype(int)
        
        # Count symptoms
        data['symptoms_count'] = data['symptoms'].apply(lambda x: len(x.split(',')) if pd.notna(x) else 0)
        
        # Create risk levels based on rules (for training data)
        # In a real scenario, this would come from historical data with actual outcomes
        data['risk_level'] = 'low'
        data.loc[
            (data['age'] < 18) | 
            (data['age'] > 35) |
            (data['prev_complications'] == 1) |
            (data['symptoms_count'] > 0) |
            (data['missed_anc'] > 1),
            'risk_level'
        ] = 'medium'
        
        data.loc[
            (data['age'] < 16) | 
            (data['age'] > 40) |
            (data['symptoms_count'] > 2) |
            (data['missed_anc'] > 2),
            'risk_level'
        ] = 'high'
        
        return data[self.features], data[self.target]
    
    def train(self, data_file):
        """Train the risk assessment model"""
        df = pd.read_csv(data_file)
        X, y = self.prepare_data(df)
        
        # Encode target variable
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        self.label_encoders['risk_level'] = le
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
        
        # Train model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        print(f"Model trained. Train accuracy: {train_score:.2f}, Test accuracy: {test_score:.2f}")
        
        # Save model
        joblib.dump(self.model, 'models/risk_model.pkl')
        joblib.dump(self.label_encoders, 'models/label_encoders.pkl')
    
    def load_model(self):
        """Load trained model"""
        try:
            self.model = joblib.load('models/risk_model.pkl')
            self.label_encoders = joblib.load('models/label_encoders.pkl')
            return True
        except FileNotFoundError:
            print("Model not found. Please train the model first.")
            return False
    
    def predict_risk(self, mother):
        """Predict risk level for a mother"""
        if not self.model:
            if not self.load_model():
                return "unknown"
        
        # Prepare features for prediction
        features = pd.DataFrame([{
            'age': mother.age,
            'prev_pregnancies': mother.prev_pregnancies,
            'prev_complications': 1 if mother.prev_complications else 0,
            'missed_anc': mother.missed_anc,
            'symptoms_count': len(mother.symptoms) if mother.symptoms else 0
        }])
        
        # Make prediction
        prediction_encoded = self.model.predict(features)
        risk_level = self.label_encoders['risk_level'].inverse_transform(prediction_encoded)[0]
        
        return risk_level
    
    def identify_high_risk_mothers(self, registry):
        """Identify all high-risk mothers in the registry"""
        high_risk = []
        for mother in registry.mothers.values():
            risk_level = self.predict_risk(mother)
            if risk_level == 'high':
                high_risk.append(mother)
        
        return high_risk