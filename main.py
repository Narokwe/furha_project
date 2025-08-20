from ussd_simulator import USSDSimulator
from voice_system import VoiceSystem
from ml_risk_model import RiskAssessmentModel
from data_models import MotherRegistry, Mother
from config import Config
import threading
import webbrowser
import warnings
import time

# Suppress Matplotlib GUI warnings
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")


def show_dashboard_data(registry, risk_model):
    """Simple text-based dashboard in terminal"""
    print("\n" + "="*50)
    print("FURHA DASHBOARD DATA")
    print("="*50)

    mothers = list(registry.mothers.values())
    print(f"Total mothers registered: {len(mothers)}")

    # Language distribution
    languages = {}
    for mother in mothers:
        languages[mother.language] = languages.get(mother.language, 0) + 1

    print("\nLanguage distribution:")
    for lang, count in languages.items():
        print(f"  {lang}: {count} mothers")

    # Risk levels
    risk_counts = {'low': 0, 'medium': 0, 'high': 0}
    for mother in mothers:
        risk_level = risk_model.predict_risk(mother)
        risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1

    print("\nRisk level distribution:")
    for level, count in risk_counts.items():
        print(f"  {level}: {count} mothers")

    # High-risk mothers
    high_risk = risk_model.identify_high_risk_mothers(registry)
    print(f"\nHigh-risk mothers needing attention: {len(high_risk)}")
    for mother in high_risk:
        print(f"  {mother.phone_number} ({mother.language})")


def run_dashboard():
    """Run Flask dashboard in background thread"""
    from dashboard import app
    # threaded=True ensures multiple requests and non-blocking
    app.run(debug=False, port=Config.DASHBOARD_PORT, use_reloader=False, threaded=True)


def main():
    # Initialize modules
    ussd_simulator = USSDSimulator()
    voice_system = VoiceSystem()
    risk_model = RiskAssessmentModel()
    registry = MotherRegistry()

    print("FURHA Prototype System Initialized")
    print("==================================")

    # Load or train risk model
    try:
        risk_model.load_model()
        print("✓ Risk assessment model loaded")
    except:
        print("Model not found. Training risk assessment model...")
        risk_model.train(Config.DATA_FILE)
        print("✓ Risk assessment model trained")

    # Start dashboard in background thread
    dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
    dashboard_thread.start()

    # Open dashboard in default browser
    time.sleep(1)  # small delay to ensure dashboard starts
    webbrowser.open(f"http://localhost:{Config.DASHBOARD_PORT}")
    print(f"\nDashboard available at http://localhost:{Config.DASHBOARD_PORT}\n")

    # USSD commands menu
    print("USSD Simulator Commands:")
    print(f"Dial {Config.USSD_CODE} to start")
    print("1. Register for antenatal care")
    print("2. Report symptoms")
    print("3. Check next appointment")
    print("4. Listen to health tips")
    print("5. View dashboard data")

    # Terminal USSD input loop
    while True:
        print("\n" + "="*50)
        phone = input("Enter phone number (or 'quit' to exit): ")
        if phone.lower() == 'quit':
            break

        ussd_input = input("Enter USSD input: ")
        response = ussd_simulator.process_ussd_request(phone, ussd_input, registry=registry)
        print("System response:", response)

        # Continue session until it ends
        while not response.startswith("END"):
            ussd_input = input("Enter USSD input: ")
            response = ussd_simulator.process_ussd_request(phone, ussd_input, registry=registry)
            print("System response:", response)

            # Auto-handle voice calls
            if "voice call" in response:
                if "health tips" in response:
                    voice_system.call_mother(phone, "weekly_tip")
                elif "symptoms" in response:
                    voice_system.call_mother(phone, "symptom_report")

        # View terminal dashboard
        if ussd_input == "5":
            show_dashboard_data(registry, risk_model)


if __name__ == '__main__':
    main()