import re
from datetime import datetime
from data_models import Mother, MotherRegistry
from config import Config

class USSDSimulator:
    def __init__(self):
        self.sessions = {}  # Stores session per phone number

    def process_ussd_request(self, phone_number, ussd_input, registry: MotherRegistry):
        """
        Process USSD input.
        `registry` is passed from main.py to update dashboard in real-time.
        """
        ussd_input = ussd_input.strip()

        # Initial dial
        if ussd_input == Config.USSD_CODE:
            self.sessions[phone_number] = {'step': 'welcome', 'data': {}}
            return self.show_welcome_menu()

        # Remove USSD code if mistakenly typed again
        if ussd_input.startswith(Config.USSD_CODE):
            ussd_input = ussd_input[len(Config.USSD_CODE):].strip()

        # If session does not exist, create one
        if phone_number not in self.sessions:
            self.sessions[phone_number] = {'step': 'welcome', 'data': {}}
            return self.show_welcome_menu()

        # Continue existing session
        return self.process_menu_navigation(phone_number, ussd_input, registry)

    def show_welcome_menu(self):
        return (
            "CON Welcome to FURHA Antenatal Care\n"
            "1. Register for antenatal care\n"
            "2. Report symptoms\n"
            "3. Check next appointment\n"
            "4. Listen to health tips\n"
            "5. View dashboard data"
        )

    def process_menu_navigation(self, phone_number, input_text, registry: MotherRegistry):
        session = self.sessions[phone_number]
        step = session.get('step', 'welcome')

        # Step: Welcome menu
        if step == 'welcome':
            if input_text == '1':
                session['step'] = 'registration_language'
                return self.start_registration()
            elif input_text == '2':
                return self.report_symptoms()
            elif input_text == '3':
                return self.check_appointment(phone_number, registry)
            elif input_text == '4':
                return self.play_health_tips(phone_number)
            elif input_text == '5':
                return "CON View the dashboard in your browser at http://localhost:5000"
            else:
                return f"CON Invalid option. Please choose 1-5."

        # Step: Registration language selection
        elif step == 'registration_language':
            return self.handle_language_selection(phone_number, input_text)

        # Step: National ID input
        elif step == 'registration_national_id':
            return self.handle_national_id(phone_number, input_text)

        # Step: Expected due date input
        elif step == 'registration_edd':
            return self.handle_edd(phone_number, input_text, registry)

        # Unknown step or expired session
        return f"END Session expired. Please dial {Config.USSD_CODE} again."

    # Registration: Start
    def start_registration(self):
        response = "CON Select your language:\n"
        for key, lang in Config.LANGUAGES.items():
            response += f"{key}. {lang['name']}\n"
        return response.strip()

    # Handle language selection
    def handle_language_selection(self, phone_number, input_text):
        session = self.sessions[phone_number]
        if input_text not in Config.LANGUAGES:
            return "CON Invalid selection. Please choose:\n1. Rendille\n2. Samburu\n3. Swahili"
        session['data']['language'] = Config.LANGUAGES[input_text]['name']
        session['step'] = 'registration_national_id'
        return "CON Please enter your National ID:"

    # Handle National ID input
    def handle_national_id(self, phone_number, input_text):
        session = self.sessions[phone_number]
        if not re.match(r'^[0-9]{6,12}$', input_text):
            return "CON Invalid National ID. Please enter a valid ID:"
        session['data']['national_id'] = input_text
        session['step'] = 'registration_edd'
        return "CON Please enter your expected due date (DD-MM-YYYY):"

    # Handle Expected Due Date input
    def handle_edd(self, phone_number, input_text, registry: MotherRegistry):
        session = self.sessions[phone_number]
        try:
            edd = datetime.strptime(input_text, '%d-%m-%Y')
            session['data']['edd'] = edd
        except ValueError:
            return "CON Invalid date format. Please use DD-MM-YYYY:"

        # Save mother to passed registry
        data = session['data']
        mother = Mother(
            phone_number=phone_number,
            language=data['language'],
            national_id=data['national_id'],
            lmp=data['edd']  # Using EDD as placeholder for LMP
        )
        registry.add_mother(mother)

        # Clear session
        del self.sessions[phone_number]

        return f"END Registration complete. Thank you, {mother.language} speaker! " \
               f"You can view the dashboard at http://localhost:5000"

    # Check next appointment
    def check_appointment(self, phone_number, registry: MotherRegistry):
        mother = registry.get_mother(phone_number)
        if not mother:
            return "END You are not registered. Please register first."

        weeks_pregnant = (datetime.now() - mother.lmp).days // 7

        if weeks_pregnant < 12:
            next_appointment = "within 4 weeks for your first ANC visit"
        elif weeks_pregnant < 28:
            next_appointment = "within 4 weeks for your next ANC visit"
        elif weeks_pregnant < 36:
            next_appointment = "within 2 weeks for your next ANC visit"
        else:
            next_appointment = "within 1 week for your next ANC visit"

        return f"END You are {weeks_pregnant} weeks pregnant. Your next appointment is due {next_appointment}."

    # Report symptoms (voice call placeholder)
    def report_symptoms(self):
        return "CON Please wait for a voice call to report symptoms."

    # Play health tips (voice call placeholder)
    def play_health_tips(self, phone_number):
        return "CON Please wait for a voice call with health tips."