import unittest
from api.services.slot_service import SlotService

class TestSlotService(unittest.TestCase):
    def test_get_slots_by_city_and_date(self):
        # Test with valid data
        slots = SlotService.get_slots_by_city_and_date("New York", "2023-10-25")
        self.assertIsInstance(slots, list)

        # Check that all returned slots are in the correct city and date
        for slot in slots:
            self.assertEqual(slot['date'], "2023-10-25")

    def test_get_slots_with_no_results(self):
        # Test with a city that doesn't exist
        slots = SlotService.get_slots_by_city_and_date("Unknown City", "2023-10-25")
        self.assertEqual(len(slots), 0)

        # Test with a date that has no slots
        slots = SlotService.get_slots_by_city_and_date("New York", "2099-12-31")
        self.assertEqual(len(slots), 0)

if __name__ == '__main__':
    unittest.main()
