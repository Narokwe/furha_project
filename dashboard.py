from flask import Flask, render_template, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from data_models import MotherRegistry
from ml_risk_model import RiskAssessmentModel
from config import Config

app = Flask(__name__)

@app.route('/')
def dashboard():
    # Load data
    registry = MotherRegistry()
    risk_model = RiskAssessmentModel()
    risk_model.load_model()
    
    # Prepare data for visualization
    df = pd.DataFrame([m.to_dict() for m in registry.mothers.values()])
    
    # Risk distribution
    risk_counts = df['risk_level'].value_counts()
    
    # Language distribution
    language_counts = df['language'].value_counts()
    
    # ANC visits
    anc_stats = df['anc_visits'].describe()
    
    # High-risk mothers
    high_risk_mothers = risk_model.identify_high_risk_mothers(registry)
    
    # Generate plots
    risk_plot = create_risk_plot(risk_counts)
    language_plot = create_language_plot(language_counts)
    anc_plot = create_anc_plot(df)
    
    return render_template('dashboard.html',
                         risk_plot=risk_plot,
                         language_plot=language_plot,
                         anc_plot=anc_plot,
                         total_mothers=len(df),
                         high_risk_count=len(high_risk_mothers),
                         languages=language_counts.to_dict())

def create_risk_plot(risk_counts):
    plt.figure(figsize=(8, 6))
    sns.barplot(x=risk_counts.index, y=risk_counts.values)
    plt.title('Risk Level Distribution')
    plt.xlabel('Risk Level')
    plt.ylabel('Count')
    
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return plot_url

def create_language_plot(language_counts):
    plt.figure(figsize=(8, 6))
    plt.pie(language_counts.values, labels=language_counts.index, autopct='%1.1f%%')
    plt.title('Language Distribution')
    
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return plot_url

def create_anc_plot(df):
    plt.figure(figsize=(8, 6))
    sns.histplot(df['anc_visits'], bins=10, kde=False)
    plt.title('ANC Visits Distribution')
    plt.xlabel('Number of ANC Visits')
    plt.ylabel('Count')
    
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return plot_url

@app.route('/api/mothers')
def get_mothers_data():
    registry = MotherRegistry()
    mothers_data = [m.to_dict() for m in registry.mothers.values()]
    return jsonify(mothers_data)

if __name__ == '__main__':
    app.run(debug=True, port=Config.DASHBOARD_PORT)