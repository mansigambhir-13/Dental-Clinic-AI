# Appointment booking
import json
from typing import List, Dict, Optional
from datetime import datetime
from utils.helpers import load_json_file, save_json_file, format_date
from config import Config

class BookingSystem:
    def __init__(self):
        self.appointments_file = Config.APPOINTMENTS_FILE
        self.appointments_data = self.load_appointments()

    def load_appointments(self) -> Dict:
        """Load appointment data from JSON file."""
        return load_json_file(self.appointments_file)

    def save_appointments(self) -> bool:
        """Save appointment data to JSON file."""
        return save_json_file(self.appointments_file, self.appointments_data)

    def get_available_slots(self, limit: int = 10) -> List[Dict]:
        """Get list of available appointment slots."""
        available_slots = []
        for slot in self.appointments_data.get('available_slots', []):
            if slot.get('available', False):
                available_slots.append(slot)
                if len(available_slots) >= limit:
                    break
        return available_slots

    def get_slots_by_date(self, date: str) -> List[Dict]:
        """Get available slots for a specific date."""
        slots = []
        for slot in self.appointments_data.get('available_slots', []):
            if slot.get('date') == date and slot.get('available', False):
                slots.append(slot)
        return slots

    def get_slots_by_type(self, appointment_type: str) -> List[Dict]:
        """Get available slots for a specific appointment type."""
        slots = []
        for slot in self.appointments_data.get('available_slots', []):
            if (slot.get('type', '').lower() == appointment_type.lower() and 
                slot.get('available', False)):
                slots.append(slot)
        return slots

    def book_appointment(self, slot_id: int, patient_info: Dict) -> Dict:
        """
        Book an appointment slot.
        Returns booking confirmation or error message.
        """
        # Find the slot
        slot_index = None
        for i, slot in enumerate(self.appointments_data.get('available_slots', [])):
            if slot.get('id') == slot_id:
                slot_index = i
                break

        if slot_index is None:
            return {
                'success': False,
                'message': 'Appointment slot not found.',
                'booking_id': None
            }

        slot = self.appointments_data['available_slots'][slot_index]
        
        if not slot.get('available', False):
            return {
                'success': False,
                'message': 'This appointment slot is no longer available.',
                'booking_id': None
            }

        # Create booking
        booking_id = f"BOOK_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        booked_appointment = {
            'booking_id': booking_id,
            'slot_id': slot_id,
            'date': slot['date'],
            'time': slot['time'],
            'duration': slot['duration'],
            'type': slot['type'],
            'patient_info': patient_info,
            'status': 'confirmed',
            'booked_at': datetime.now().isoformat()
        }

        # Add to booked appointments
        if 'booked_appointments' not in self.appointments_data:
            self.appointments_data['booked_appointments'] = []
        
        self.appointments_data['booked_appointments'].append(booked_appointment)

        # Mark slot as unavailable
        self.appointments_data['available_slots'][slot_index]['available'] = False

        # Save changes
        if self.save_appointments():
            return {
                'success': True,
                'message': f'Appointment booked successfully!',
                'booking_id': booking_id,
                'appointment_details': booked_appointment
            }
        else:
            return {
                'success': False,
                'message': 'Failed to save booking. Please try again.',
                'booking_id': None
            }

    def cancel_booking(self, booking_id: str) -> Dict:
        """Cancel a booking and make the slot available again."""
        booked_appointments = self.appointments_data.get('booked_appointments', [])
        
        booking_index = None
        for i, booking in enumerate(booked_appointments):
            if booking.get('booking_id') == booking_id:
                booking_index = i
                break

        if booking_index is None:
            return {
                'success': False,
                'message': 'Booking not found.'
            }

        booking = booked_appointments[booking_index]
        slot_id = booking.get('slot_id')

        # Find and reactivate the slot
        for slot in self.appointments_data.get('available_slots', []):
            if slot.get('id') == slot_id:
                slot['available'] = True
                break

        # Remove from booked appointments
        del self.appointments_data['booked_appointments'][booking_index]

        if self.save_appointments():
            return {
                'success': True,
                'message': 'Appointment cancelled successfully.'
            }
        else:
            return {
                'success': False,
                'message': 'Failed to cancel booking. Please try again.'
            }

    def format_slot_display(self, slot: Dict) -> str:
        """Format a slot for display to user."""
        date_formatted = format_date(slot.get('date', ''))
        return (f"📅 {date_formatted}\n"
                f"🕐 {slot.get('time', 'N/A')}\n"
                f"⏱️ Duration: {slot.get('duration', 'N/A')}\n"
                f"🦷 Type: {slot.get('type', 'General')}\n"
                f"🆔 Slot ID: {slot.get('id', 'N/A')}")

    def get_booking_summary(self, booking_id: str) -> Optional[Dict]:
        """Get booking details by booking ID."""
        for booking in self.appointments_data.get('booked_appointments', []):
            if booking.get('booking_id') == booking_id:
                return booking
        return None

    def get_available_dates(self) -> List[str]:
        """Get list of dates with available appointments."""
        dates = set()
        for slot in self.appointments_data.get('available_slots', []):
            if slot.get('available', False):
                dates.add(slot.get('date'))
        return sorted(list(dates))

    def get_available_types(self) -> List[str]:
        """Get list of available appointment types."""
        types = set()
        for slot in self.appointments_data.get('available_slots', []):
            if slot.get('available', False):
                types.add(slot.get('type'))
        return sorted(list(types))