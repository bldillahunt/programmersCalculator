import unittest 
import tkinter as tk 
import itertools
from hypothesis import given, settings, strategies as st
from test_parameters import TestCase 
from fpgaCalculator import FpgaCalculator 

# ========================================================================= 
# FREE-STANDING HYPOTHESIS STRATEGIES (Fixed 'draw' Positional Argument)
# ========================================================================= 
def gen_bin_val(draw):
    bits = draw(st.lists(st.sampled_from(["0", "1"]), min_size=1, max_size=16))
    if draw(st.booleans()) and len(bits) > 1:
        split = draw(st.integers(min_value=1, max_value=len(bits)-1))
        return "".join(bits[:split]) + "." + "".join(bits[split:])
    return "".join(bits)

def gen_hex_val(draw):
    return "".join(draw(st.lists(st.sampled_from("0123456789ABCDEF"), min_size=1, max_size=8)))

def gen_real_val(draw):
    # Generates a standard floating point number as a clean string representation
    return f"{draw(st.floats(allow_nan=False, allow_infinity=False, min_value=-10000, max_value=10000)):.4f}"

def gen_ieee_val(draw, length):
    return "".join(draw(st.lists(st.sampled_from("0123456789ABCDEF"), min_size=length, max_size=length)))

@st.composite
def hardware_string_strategy(draw):
    # Updated to match your custom float naming variables seamlessly
    in_mode = draw(st.sampled_from(["BIN", "HEX", "REAL", "FP32", "FP64"]))
    op = draw(st.sampled_from(["+", "-", "*", "/", ""]))
    
    # Pass 'draw' explicitly down into the lower helper scopes
    if in_mode == "BIN": val_a = gen_bin_val(draw)
    elif in_mode == "HEX": val_a = gen_hex_val(draw)
    elif in_mode == "REAL": val_a = gen_real_val(draw)
    elif in_mode == "FP32": val_a = gen_ieee_val(draw, 8)
    elif in_mode == "FP64": val_a = gen_ieee_val(draw, 16)
    
    if op == "":
        return val_a, in_mode, op
        
    if in_mode == "BIN": val_b = gen_bin_val(draw)
    elif in_mode == "HEX": val_b = gen_hex_val(draw)
    elif in_mode == "REAL": val_b = gen_real_val(draw)
    elif in_mode == "FP32": val_b = gen_ieee_val(draw, 8)
    elif in_mode == "FP64": val_b = gen_ieee_val(draw, 16)
    
    # Avoid mathematical division explosions inside your UI engine layers 
    if op == "/" and val_b in ["0", "0.0", "0000"]: 
        val_b = "1"
        
    return f"{val_a}{op}{val_b}", in_mode, op


class TestBench(unittest.TestCase): 
    
    @classmethod 
    def setUpClass(cls): 
        cls.root = tk.Tk() 
        cls.root.withdraw() 
        cls.app = FpgaCalculator(cls.root) 
        cls.app.create_widgets() 

    def press_key(self, char_str): 
        for char in char_str: 
            self.app.on_button_click(char) 

    # ========================================================================= 
    # AUTOMATED 125-PATH MATRIX + FUZZER 
    # ========================================================================= 
    @given(
        hw_data=hardware_string_strategy(),
        int_bits_val=st.sampled_from(['8', '16', '32']),
        frac_bits_val=st.sampled_from(['8', '16', '32'])
    )
    @settings(max_examples=50, deadline=None) 
    def test_comprehensive_matrix_fuzzer(self, hw_data, int_bits_val, frac_bits_val):
        input_string, computed_in_mode, computed_op = hw_data
        
        modes = ["BIN", "HEX", "REAL", "FP32", "FP64"]
        
        for out_mode in modes:
            with self.subTest(in_mode=computed_in_mode, out_mode=out_mode, op=computed_op):
                
                self.app.input_mode.set(computed_in_mode)
                self.app.output_mode.set(out_mode)
                self.app.int_bits.set(int_bits_val)
                self.app.frac_bits.set(frac_bits_val)
                self.app.main_display_var.set(input_string)
                
                try:
                    self.app.on_button_click("Enter")
                    result = self.app.aux_display_var.get()
                    self.assertIsNotNone(result)
                    
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
            TestCase('16', '16', 'HEX', 'REAL', '80000000-80000000', '0.0'), 
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
        cls.root.destroy() 

if __name__ == "__main__": 
    unittest.main()
