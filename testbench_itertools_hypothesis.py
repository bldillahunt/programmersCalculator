import unittest 
import tkinter as tk 
import itertools
from hypothesis import given, settings, strategies as st
from test_parameters import TestCase 
from fpgaCalculator import FpgaCalculator 

class TestBench(unittest.TestCase): 
    
    @classmethod 
    def setUpClass(cls): 
        """Initializes the class layout once in memory for the tests.""" 
        cls.root = tk.Tk() 
        cls.root.withdraw() # Keeps the window hidden from the desktop screen 
        # Instantiate your application class directly into the test context 
        cls.app = FpgaCalculator(cls.root) 
        cls.app.create_widgets() # Forces the widget bindings to complete 

    def press_key(self, char_str): 
        """Simulates a user physically typing characters or clicking grid buttons.""" 
        for char in char_str: 
            self.app.on_button_click(char) 

    # ========================================================================= 
    # NEW: HYPOTHESIS BITSTRING GENERATORS (Math Strategy Blocks)
    # ========================================================================= 
    @staticmethod
    def gen_bin_val(draw):
        """Generates valid 1s/0s with an optional single binary point."""
        bits = draw(st.lists(st.sampled_from(["0", "1"]), min_size=1, max_size=16))
        if draw(st.booleans()) and len(bits) > 1:
            split = draw(st.integers(min_value=1, max_value=len(bits)-1))
            return "".join(bits[:split]) + "." + "".join(bits[split:])
        return "".join(bits)

    @staticmethod
    def gen_hex_val(draw):
        """Generates valid hardware hex characters."""
        return "".join(draw(st.lists(st.sampled_from("0123456789ABCDEF"), min_size=1, max_size=8)))

    @staticmethod
    def gen_real_val(draw):
        """Generates real float values."""
        return f"{draw(st.floats(allow_nan=False, allow_infinity=False, min_value=-10000, max_value=10000)):.4f}"

    @staticmethod
    def gen_ieee_val(draw, length):
        """Generates raw IEEE strings."""
        return "".join(draw(st.lists(st.sampled_from("0123456789ABCDEF"), min_size=length, max_size=length)))

    @st.composite
    def hardware_string_strategy(cls, draw):
        """Generates randomized math strings based on the chosen input mode and operation."""
        in_mode = draw(st.sampled_from(["BIN", "HEX", "REAL", "FP32", "FP64"]))
        op = draw(st.sampled_from(["+", "-", "*", "/", "CONVERT"]))
        
        # Helper to grab a clean value representation
        def get_val(mode):
            if mode == "BIN": return cls.gen_bin_val(draw)
            if mode == "HEX": return cls.gen_hex_val(draw)
            if mode == "REAL": return cls.gen_real_val(draw)
            if mode == "FP32": return cls.gen_ieee_val(draw, 8)
            if mode == "FP64": return cls.gen_ieee_val(draw, 16)
        
        val_a = get_val(in_mode)
        
        # If it's a conversion, return just the solo value string
        if op == "CONVERT":
            return val_a, in_mode, op
            
        # Otherwise generate val_b and pack them together with the operator separator
        val_b = get_val(in_mode)
        if op == "/" and val_b in ["0", "0.0", "0000"]: 
            val_b = "1" # Avoid explicit zero divisions up front to find structural bugs first
            
        return f"{val_a}{op}{val_b}", in_mode, op

    # ========================================================================= 
    # NEW: AUTOMATED 125-PATH MATRIX + FUZZER 
    # ========================================================================= 
    @given(
        hw_data=hardware_string_strategy(),
        int_bits_val=st.sampled_from(['8', '16', '32']),
        frac_bits_val=st.sampled_from(['8', '16', '32'])
    )
    @settings(max_examples=50, deadline=None) # Tests 50 structural variations per execution cycle
    def test_comprehensive_matrix_fuzzer(self, hw_data, int_bits_val, frac_bits_val):
        input_string, computed_in_mode, computed_op = hw_data
        
        # Match your exact UI mode definitions
        modes = ["BIN", "HEX", "REAL", "FP32", "FP64"]
        
        # 125 path coverage matrix sweep inside the fuzz loop
        for out_mode in modes:
            with self.subTest(in_mode=computed_in_mode, out_mode=out_mode, op=computed_op):
                
                # Feed your application variables exactly like your manual test cases do
                self.app.input_mode.set(computed_in_mode)
                self.app.output_mode.set(out_mode)
                self.app.int_bits.set(int_bits_val)
                self.app.frac_bits.set(frac_bits_val)
                self.app.main_display_var.set(input_string)
                
                # Execute evaluation path
                try:
                    self.app.on_button_click("Enter")
                    result = self.app.aux_display_var.get()
                    
                    # Basic UI structural assertions
                    self.assertIsNotNone(result)
                    
                    # Prevent prefix or formatting leaks
                    if result != "ERROR":
                        if out_mode == "BIN":
                            self.assertNotIn("0b", result, "Binary display leakage detected.")
                        elif out_mode == "HEX":
                            self.assertNotIn("0x", result, "Hexadecimal display leakage detected.")
                            self.assertNotIn(".", result, "Pure fixed hex display shouldn't have decimal points.")
                            
                except Exception as e:
                    self.fail(f"CRASH OCCURRED!\nInput: {input_string}\n"
                              f"Path: {computed_in_mode} -> {out_mode} using {computed_op}\n"
                              f"Config: Int Bits {int_bits_val}, Frac Bits {frac_bits_val}\n"
                              f"Reason: {str(e)}")

    # ========================================================================= 
    # THE DATA PATH TEST MATRIX EXAMPLES (Your original manual test paths)
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
            TestCase('16', '16', 'BIN', 'REAL', '0.000000000000001/1', '-3.0517578125e-05'), 
            TestCase('16', '16', 'BIN', 'REAL', '11111001.001/0.0101001', '-21.463414634146343') 
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
        test_cases_hex_real = [ 
            TestCase('16', '16', 'HEX', 'REAL', '', 'ERROR'), 
            TestCase('16', '16', 'HEX', 'REAL', '0', '0.0'), 
            TestCase('16', '16', 'HEX', 'REAL', '0+', '0.0'), 
            TestCase('16', '16', 'HEX', 'REAL', '0x', 'ERROR'), 
            TestCase('16', '16', 'HEX', 'REAL', '0x0', 'ERROR'), 
            TestCase('16', '16', 'HEX', 'REAL', '7FFFFFFF+7FFFFFFF', 'ERROR'), 
            TestCase('16', '16', 'HEX', 'REAL', '3FFFFFFF+3FFFFFFF', '32767.999969482422'), 
            TestCase('16', '16', 'HEX', 'REAL', '80000000-10000', 'ERROR'), 
            TestCase('16', '16', 'HEX', 'REAL', '80000000-80000000', '0.0'), # FAILS HERE 
            TestCase('16', '16', 'HEX', 'REAL', '7F0000*7F0000', '1057030144.0'), 
            TestCase('16', '16', 'HEX', 'REAL', '0BE0000*0BE0000', 'ERROR') 
        ] 
        for test in test_cases_hex_real: 
            self.app.input_mode.set(test.input_mode) 
            self.app.output_mode.set(test.output_mode) 
            self.app.int_bits.set(test.integer_bits) 
            self.app.frac_bits.set(test.fraction_bits) 
            self.app.main_display_var.set(test.input_string) 
            self.app.on_button_click("Enter") 
            self.assertEqual(self.app.aux_display_var.get(), test.expected) 

    def test_path_bin_to_hex(self): 
        test_cases_bin_hex = [ 
            TestCase('16', '16', 'BIN', 'HEX', '0.000000000000001/1', 'FFFF0000'), 
            TestCase('16', '16', 'BIN', 'HEX', '11111001/00000101', 'FFFE999A') 
        ] 
        for test in test_cases_bin_hex: 
            self.app.input_mode.set(test.input_mode) 
            self.app.output_mode.set(test.output_mode) 
            self.app.int_bits.set(test.integer_bits) 
            self.app.frac_bits.set(test.fraction_bits) 
            self.app.main_display_var.set(test.input_string) 
            self.app.on_button_click("Enter") 
            self.assertEqual(self.app.aux_display_var.get(), test.expected) 

    @classmethod 
    def tearDownClass(cls): 
        """Cleanly destroys the hidden Tkinter context after all test paths execute.""" 
        cls.root.destroy() 

if __name__ == "__main__": 
    unittest.main()
