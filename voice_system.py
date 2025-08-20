from data_models import MotherRegistry
from config import Config
from datetime import datetime

class VoiceSystem:
    def __init__(self):
        self.registry = MotherRegistry()
    
    def call_mother(self, phone_number, message_type="weekly_tip"):
        """Simulate calling a mother with a message (text output only)"""
        mother = self.registry.get_mother(phone_number)
        if not mother:
            print(f"Mother with phone {phone_number} not found")
            return False
        
        # Calculate weeks pregnant
        weeks_pregnant = (datetime.now() - mother.lmp).days // 7
        
        if message_type == "weekly_tip":
            if weeks_pregnant < 14:
                message = "Health tip: Eat nutritious foods and take folic acid. Avoid alcohol and smoking."
            elif weeks_pregnant < 28:
                message = "Health tip: You should feel your baby move. Attend all antenatal appointments."
            else:
                message = "Health tip: Prepare for delivery. Know the signs of labor and where to go."
        
        elif message_type == "appointment_reminder":
            message = f"Appointment reminder: Your next antenatal visit is due soon. You are {weeks_pregnant} weeks pregnant."
        
        elif message_type == "symptom_report":
            message = "Thank you for reporting your symptoms. A health worker will contact you soon."
        
        print(f"VOICE CALL to {phone_number} ({mother.language}): {message}")
        return True