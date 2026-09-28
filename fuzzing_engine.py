import unittest 
import tkinter as tk 
import itertools
import random  # NEW: Required for generating random fuzzing inputs
from test_parameters import BinaryTestConfiguration 
from fpgaCalculator import FpgaCalculator 
from binary_support import int_list_to_binary_string, binary_string_to_int_list, list_to_string
from binary_conversions import binary_to_real
from itertools import chain

class TestBench(unittest.TestCase): 
    
	@classmethod 
	def setUpClass(cls): 
		"""Initializes the class layout once in memory for the tests.""" 
		cls.root = tk.Tk() 
		cls.root.withdraw() # Keeps the window hidden from the desktop screen 
		# Instantiate your application class directly into the test context 
		cls.app = FpgaCalculator(cls.root) 
		cls.app.create_widgets() # Forces the widget bindings to complete 

		# =====================================================================
		# ?? RANDOM FUZZING REGRESSION SECTION (Runs First & Decoupled)
		# =====================================================================
		print("? Initializing Decoupled Random Fuzzing Regression Suite...")
		
		# Define configuration bounds for the random generator
		test_cases = ["REAL", "HEX", "BIN", "FP32", "FP64"]
		math_ops = ["+", "-", "*", "/"]
		
		# Set a target number of random combinations to run (e.g., 2000 patterns)
		NUM_FUZZ_PATTERNS = 2000 
		
		passed_fuzz = 0
		failed_fuzz = 0
		fuzz_mismatch_logs = []

		# Helper to execute calculations through your Tkinter app state silently
		def run_silent_fuzz(val, in_m, out_m, i_sz, f_sz):
			cls.app.input_mode.set(in_m) 
			cls.app.output_mode.set(out_m) 
			cls.app.int_bits.set(i_sz) 
			cls.app.frac_bits.set(f_sz) 
			cls.app.main_display_var.set(val) 
			cls.app.on_button_click("Enter") 
			return cls.app.aux_display_var.get()

		# Helper to generate a completely randomized, valid fixed-point binary string list
		def generate_random_bin_list(int_w, frac_w):
			# Randomize sign bit, integer bits, and fractional bits
			bits = [random.choice([0, 1]) for _ in range(int_w + frac_w)]
			bits.insert(int_w, '.') # Drop the radix point at the exact boundary
			return bits

		for pattern_idx in range(NUM_FUZZ_PATTERNS):
			# 1. Randomly select format pairs, widths, and operations
			in_type = random.choice(test_cases)
			out_type = random.choice(test_cases)
			op = random.choice(math_ops)
			
			# Constrain registers dynamically to mirror your hardware parameters
			int_size = 12 if in_type == "HEX" else 32
			frac_size = 12 if in_type == "HEX" else 32

			# 2. Generate two distinct, randomized binary array seeds
			seed_a = generate_random_bin_list(int_size, frac_size)
			seed_b = generate_random_bin_list(int_size, frac_size)
			
			str_seed_a = "".join(map(str, seed_a))
			str_seed_b = "".join(map(str, seed_b))

			try:
				# 3. Process inputs through the calculator's conversion layer
				conv_a = run_silent_fuzz(str_seed_a, "BIN", in_type, int_size, frac_size)
				conv_b = run_silent_fuzz(str_seed_b, "BIN", in_type, int_size, frac_size)
				
				# Handle division by zero constraints safely at the regression layer
				if op == '/' and binary_to_real(seed_b) == 0.0:
					continue 

				# Combine operands and operator into your standard execution string
				eval_string = f"{conv_a}{op}{conv_b}"
				raw_output = run_silent_fuzz(eval_string, in_type, "BIN", int_size, frac_size)
				
				# 4. Reference Verification Math
				val_a = binary_to_real(seed_a)
				val_b = binary_to_real(seed_b)
				
				if op == '+': expected_real = val_a + val_b
				elif op == '-': expected_real = val_a - val_b
				elif op == '*': expected_real = val_a * val_b
				elif op == '/': expected_real = val_a / val_b

				calculated_real = binary_to_real(binary_string_to_int_list(raw_output))

				# Validate tolerance to protect against basic floating-point representation limits
				if abs(calculated_real - expected_real) < 1e-7:
					passed_fuzz += 1
				else:
					failed_fuzz += 1
					fuzz_mismatch_logs.append(
						f"Pattern #{pattern_idx} Mismatch!\n"
						f"  Format Pair: {in_type} -> {out_type} | Op: [{op}] | Width: Q{int_size}.{frac_size}\n"
						f"  Operand A Binary: {str_seed_a} ({val_a})\n"
						f"  Operand B Binary: {str_seed_b} ({val_b})\n"
						f"  Expected Real:    {expected_real}\n"
						f"  Calculator Real:  {calculated_real} (Raw Return: '{raw_output}')\n"
					)
			except Exception as e:
				failed_fuzz += 1
				fuzz_mismatch_logs.append(f"Pattern #{pattern_idx} CRASHED: {str(e)} | Context: {str_seed_a} {op} {str_seed_b} [{in_type}]")

		print("\n" + "="*60)
		print(f"?? RANDOM FUZZING REGRESSION RESULTS: {'? PASSED' if failed_fuzz == 0 else '? FAILED'}")
		print(f"Total Random Permutations Evaluated: {passed_fuzz + failed_fuzz}")
		print(f"Passed Patterns: {passed_fuzz} | Detected Mismatches: {failed_fuzz}")
		print("="*60 + "\n")

		if failed_fuzz > 0:
			print("?? FUZZ ENGINE ERROR DIAGNOSTIC BREAKDOWN:")
			for log in fuzz_mismatch_logs[:5]: # Display first 5 failure vectors
				print(log + "-"*40)
			if failed_fuzz > 5:
				print(f"  ...and {failed_fuzz - 5} more hidden boundary failures discovered.")
			print("\n?? Regression check failed. Halting before executing directed tests.")
			raise RuntimeError("Randomized regression constraint mismatch detected.")
			
		print("?? Core ALU survived all random fuzzing patterns safely! Launching legacy directed tests...\n")
		# =====================================================================

	def press_key(self, char_str):
		"""Simulates a user physically typing characters or clicking grid buttons."""
		for char in char_str:
			self.app.on_button_click(char)

	def gui_entry_parameters(self, value, input_mode, output_mode, int_size, frac_size):
		self.app.input_mode.set(input_mode) 
		self.app.output_mode.set(output_mode) 
		self.app.int_bits.set(int_size) 
		self.app.frac_bits.set(frac_size) 
		self.app.main_display_var.set(value) 
		self.app.on_button_click("Enter") 
		return self.app.aux_display_var.get()
	
	def single_bit_shifter_right(self, operand_sign, seed_value):
		shift_register = seed_value
		
		if ('.' in shift_register):
			binary_point_index = shift_register.index('.')
		else:
			binary_point_index = len(shift_register)
		
		shift_register = [bit for bit in shift_register if bit != '.']
		
		shift_register.pop()
		shift_register.insert(0, operand_sign)
		shift_register.insert(binary_point_index, '.')
		return shift_register

	def single_bit_shifter_left(self, operand_sign, seed_value):
		shift_register = seed_value

		if ('.' in shift_register):
			binary_point_index = shift_register.index('.')
		else:
			binary_point_index = len(shift_register)
		
		shift_register = [bit for bit in shift_register if bit != '.']

		shift_register.pop(0)
		shift_register.append(0)
		shift_register.insert(binary_point_index, '.')
		return shift_register

	# DIRECTED TEST CODE REMAINING COMPLETELY UNTOUCHED AND IN PLACE BELOW
	def test_limited_single_bit_vectors(self):
		test_cases = ["REAL", "HEX", "BIN", "FP32", "FP64"]
		integer_sizes = [32, 12, 32, 32, 32]
		fraction_sizes = [32, 12, 32, 32, 32]
		
		real_single_pos_right = []
		hex_single_pos_right = []
		bin_single_pos_right = []
		fp32_single_pos_right = []
		fp64_single_pos_right = []
		
		output_arrays_pos_right = [real_single_pos_right, hex_single_pos_right, bin_single_pos_right, fp32_single_pos_right, fp64_single_pos_right]
		
		real_single_neg_right = []
		hex_single_neg_right = []
		bin_single_neg_right = []
		fp32_single_neg_right = []
		fp64_single_neg_right = []
		
		output_arrays_neg_right = [real_single_neg_right, hex_single_neg_right, bin_single_neg_right, fp32_single_neg_right, fp64_single_neg_right]

		real_single_pos_left = []
		hex_single_pos_left = []
		bin_single_pos_left = []
		fp32_single_pos_left = []
		fp64_single_pos_left = []
		
		output_arrays_pos_left = [real_single_pos_left, hex_single_pos_left, bin_single_pos_left, fp32_single_pos_left, fp64_single_pos_left]
		
		real_single_neg_left = []
		hex_single_neg_left = []
		bin_single_neg_left = []
		fp32_single_neg_left = []
		fp64_single_neg_left = []
		
		output_arrays_neg_left = [real_single_neg_left, hex_single_neg_left, bin_single_neg_left, fp32_single_neg_left, fp64_single_neg_left]

		binary_input_file = open("binary_input_file.txt", "w")

		pos_right_seed_value = [0] + [1] + [0]*10 + ['.'] + [0]*12
		single_positive_right_vectors = []
		
		for i in range(0, 23):
			single_positive_right_vectors.append(pos_right_seed_value)
			pos_right_seed_value = self.single_bit_shifter_right(0, pos_right_seed_value)

		binary_input_file.write("Single Positive Right Vectors" + "\n")
		
		for test, item, int_size, frac_size in zip(test_cases, output_arrays_pos_right, integer_sizes, fraction_sizes): 
			for i in range(0, len(single_positive_right_vectors)):
				item.append(self.gui_entry_parameters("".join(map(str, single_positive_right_vectors[i])), "BIN", test, int_size, frac_size))
				binary_input_file.write(str(item[i]) + "\n")				
		
		neg_right_seed_value = [1] + [0]*11 + ['.'] + [0]*12
		single_negative_right_vectors = []

		for i in range(0, 23):
			single_negative_right_vectors.append(neg_right_seed_value)
			neg_right_seed_value = self.single_bit_shifter_right(1, neg_right_seed_value)

		binary_input_file.write("Single Negative Right Vectors" + "\n")
		
		for test, item, int_size, frac_size in zip(test_cases, output_arrays_neg_right, integer_sizes, fraction_sizes): 			
			for i in range(0, len(single_negative_right_vectors)):
				item.append(self.gui_entry_parameters("".join(map(str, single_negative_right_vectors[i])), "BIN", test, int_size, frac_size))
				binary_input_file.write(str(item[i]) + "\n")				

		pos_left_seed_value = [0]*11 + ['.'] + [0]*11 + [1]
		single_positive_left_vectors = []

		for i in range(0, 23):
			single_positive_left_vectors.append(pos_left_seed_value)
