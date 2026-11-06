import unittest
from model import CAPABILITIES, validate_allocation, calculate_outcomes

class AllocationTests(unittest.TestCase):
    def test_valid_allocation(self):
        a = dict(zip(CAPABILITIES, [20,20,10,15,10,10,10,5]))
        self.assertTrue(validate_allocation(a)[0])
        self.assertEqual(calculate_outcomes(a)['Actionable service'], 10)
    def test_over_budget(self):
        a = {k: 20 for k in CAPABILITIES}
        self.assertFalse(validate_allocation(a)[0])
    def test_non_multiple_of_five(self):
        a = dict(zip(CAPABILITIES, [21,19,10,15,10,10,10,5]))
        self.assertFalse(validate_allocation(a)[0])
if __name__ == '__main__': unittest.main()
