import unittest
import tkinter as tk

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

    def test_path_bin_to_hex(self):
        """Path 12: BIN -> HEX Complete Integration Validation."""
        # --- SUB-TEST GROUP A: THE 3 EDGE CASES ---
        self.app.input_mode.set("BIN")
        self.app.output_mode.set("HEX")
        self.app.int_bits.set(4)
        self.app.frac_bits.set(4)

        # Edge Case 1: Pure single operand conversion (Zero representation)
        self.app.main_display_var.set("0.0")
        self.app.on_button_click("Enter")
        self.assertEqual(self.app.aux_display_var.get(), "0")

        # Edge Case 2: Negative two's complement fractional math handling
        self.app.main_display_var.set("1.1+0.1") # (-0.5 + 0.5) = 0.0
        self.app.on_button_click("Enter")
        self.assertEqual(self.app.aux_display_var.get(), "0")

        # Edge Case 3: Math overflow causing truncation down to bits footprint
        self.app.main_display_var.set("1111+0001") # Forces bit carry out
        self.app.on_button_click("Enter")
        self.assertEqual(self.app.aux_display_var.get(), "0") # Expect wrap-around

        # --- SUB-TEST GROUP B: THE 3 INPUT ERRORS (Testing your verification methods) ---
        
        # Error Input 1: Character Violation (Radio button is BIN, but input contains HEX)
        self.app.main_display_var.set("101A+0101") 
        self.app.on_button_click("Enter")
        # Assert that your verification method interceptor updates the display with a safe error message
        self.assertIn("ERROR", self.app.aux_display_var.get())

        # Error Input 2: Multiple Radix Points (Malforming the fraction layout)
        self.app.main_display_var.set("1.0.1+0.1")
        self.app.on_button_click("Enter")
        self.assertIn("ERROR", self.app.aux_display_var.get())

        # Error Input 3: Operator Syntax Fault (Typing hanging or dangling characters)
        self.app.main_display_var.set("1101+")
        self.app.on_button_click("Enter")
        self.assertIn("ERROR", self.app.aux_display_var.get())

    @classmethod
    def tearDownClass(cls):
        """Cleanly destroys the hidden Tkinter context after all test paths execute."""
        cls.root.destroy()

if __name__ == "__main__":
    unittest.main()
