import unittest
import tkinter as tk
from test_parameters import TestCase

from fpgaCalculator import FpgaCalculator

class TestBench(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		"""Initializes the class layout once in memory for the tests."""
		cls.root = tk.Tk()
		cls.root.withdraw()  # Keeps the window hidden from the desktop screen

		# Instantiate your application class directly into the test context
		cls.app = FpgaCalculator(cls.root)
		cls.app.create_widgets() # Forces the widget bindings to complete
    
	def press_key(self, char_str):
		"""Simulates a user physically typing characters or clicking grid buttons."""
		for char in char_str:
			self.app.on_button_click(char)

    # =========================================================================
    # THE DATA PATH TEST MATRIX EXAMPLES
    # =========================================================================

	def test_path_bin_to_real(self):
		test_cases_bin_real = [
		TestCase('16', '16', 'BIN', 'REAL', '', 'ERROR'),
		TestCase('16', '16', 'BIN', 'REAL', '0', '0.0'),
		TestCase('16', '16', 'BIN', 'REAL', '0+', 'ERROR'),
		TestCase('16', '16', 'BIN', 'REAL', '0.', 'ERROR'),
		TestCase('16', '16', 'BIN', 'REAL', '.0', 'ERROR'),
		TestCase('16', '16', 'BIN', 'REAL', '11111001/00000101', '-1.4'),
		TestCase('16', '32', 'BIN', 'REAL', '0.000000000000001/0.00000101', '0.0015625'),
		TestCase('16', '16', 'BIN', 'REAL', '11111001+00000101', '-2.0'),
		TestCase('16', '16', 'BIN', 'REAL', '11111001+00000101', '-2.0'),
		TestCase('16', '16', 'BIN', 'REAL', '11111001+00000101', '-2.0')
		]

		for test in test_cases_bin_real:
			self.app.input_mode.set(test.input_mode)
			self.app.output_mode.set(test.output_mode)
			self.app.int_bits.set(test.integer_bits)
			self.app.frac_bits.set(test.fraction_bits)
			self.app.main_display_var.set(test.input_string)
			self.app.on_button_click("Enter")
			self.assertEqual(self.app.aux_display_var.get(), test.expected)

	def test_path_hex_to_real(self):
		test_cases_bin_real = [
		TestCase('16', '16', 'HEX', 'REAL', '', 'ERROR'),
		TestCase('16', '16', 'HEX', 'REAL', '0', '0.0'),
		TestCase('16', '16', 'HEX', 'REAL', '0+', 'ERROR'),
		TestCase('16', '16', 'HEX', 'REAL', '0x', 'ERROR'),
		TestCase('16', '16', 'HEX', 'REAL', '0x0', 'ERROR'),
		TestCase('16', '16', 'HEX', 'REAL', '7FFFFFFF+7FFFFFFF', 'ERROR'),
		TestCase('16', '16', 'HEX', 'REAL', '3FFFFFFF+3FFFFFFF', '32767.999969482422'),
		TestCase('16', '16', 'HEX', 'REAL', '80000000-10000', 'ERROR'),
		TestCase('16', '16', 'HEX', 'REAL', '80000000-80000000', 'ERROR'),
		TestCase('16', '16', 'HEX', 'REAL', '7F0000*7F0000', '1057030144.0'),
		TestCase('16', '16', 'HEX', 'REAL', '0BE0000*0BE0000', 'ERROR')
		]

	@classmethod
	def tearDownClass(cls):
		"""Cleanly destroys the hidden Tkinter context after all test paths execute."""
		cls.root.destroy()

if __name__ == "__main__":
    unittest.main()
