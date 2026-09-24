import unittest 
import tkinter as tk 
import itertools
from test_parameters import BinaryTestConfiguration 
from fpgaCalculator import FpgaCalculator 
from binary_support import int_list_to_binary_string
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

	def press_key(self, char_str):
		"""Simulates a user physically typing characters or clicking grid buttons."""
		for char in char_str:
			self.app.on_button_click(char)

	def gui_entry_parameters(self, value, input_mode, output_mode, int_size, frac_size):
		self.app.input_mode.set("BIN") 
		self.app.output_mode.set(test.test_cases) 
		self.app.int_bits.set(32) 
		self.app.frac_bits.set(32) 
		self.app.main_display_var.set(value) 
		self.app.on_button_click("Enter") 
		return self.app.aux_display_var.get()
	
	def single_bit_shifter_right(self, maximum_size, operand_sign):
		if maximum_size %2 == 0:
			integer_size = maximum_size/2
			fraction_size = maximum_size/2
		else:
			integer_size = maximum_size//2 + 1
			fraction_size = maximum_size//2
			
		msb = [operand_sign]
		seed_value = msb + [1] + [0]*(integer_size-1) + ['.'] + [0]*fraction_size
		shift_register = seed_value
		output_data = []
		
		for i in maximum_size:
			output_data.append(shift_register)
			shift_register.pop()
			shift_register.insert(0, msb)
		
		output_data_string = int_list_to_binary_string(output_data, len(output_data))
		
		return output_data_string

	def single_bit_shifter_left(self, maximum_size, operand_sign):
		if maximum_size %2 == 0:
			integer_size = maximum_size/2
			fraction_size = maximum_size/2
		else:
			integer_size = maximum_size//2 + 1
			fraction_size = maximum_size//2
			
		lsb = [operand_sign]
		seed_value = [operand_sign]*integer_size + [0]*(fraction_size-1) + [1]
		shift_register = seed_value
		output_data = []
		
		for i in maximum_size:
			output_data.append(shift_register)
			shift_register.pop()
			shift_register.insert(0, msb)
		
		output_data_string = int_list_to_binary_string(output_data, len(output_data))
		
		return output_data_string

	# Create test vectors that will fit into IEEE754 single values
	def test_limited_single_bit_vectors(self):
		# STEP 1: Create the binary test vectors
		
		test_cases = ["REAL", "HEX", "BIN", "FP32", "FP64"]
		
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

 		for test in test_cases: 
			# Test pattern: single bit, positive value shifted to the right
 			single_positive_right_vectors = single_bit_shifter_right(23, 0)

			for item in chain.from_iterable(output_arrays_pos_right): 			
				for i in len(single_positive_right_vectors):
					item.append(gui_entry_parameters(self, single_positive_right_vectors[i], "BIN", test, 32, 32))

			# Test pattern: single bit, negative value shifted to the right
 			single_negative_right_vectors = single_bit_shifter_right(23, 1)

			for item in chain.from_iterable(output_arrays_neg_right): 			
				for i in len(single_negative_right_vectors):
					item.append(gui_entry_parameters(self, single_negative_right_vectors[i], "BIN", test, 32, 32))
		
			# Test pattern: single bit, positive value shifted to the left
 			single_positive_left_vectors = single_bit_shifter_left(23, 0)

			for item in chain.from_iterable(output_arrays_pos_left): 			
				for i in len(single_positive_left_vectors):
					item.append(gui_entry_parameters(self, single_positive_left_vectors[i], "BIN", test, 32, 32))

			# Test pattern: single bit, negative value shifted to the left
 			single_negative_left_vectors = single_bit_shifter_left(23, 1)

			for item in chain.from_iterable(output_arrays_neg_left): 			
				for i in len(single_negative_left_vectors):
					item.append(gui_entry_parameters(self, single_negative_left_vectors[i], "BIN", test, 32, 32))
		
		print("Created test vectors")
		
		# STEP 2: Run the test vectors back through the calculator

		# Test pattern: single bit, positive value shifted to the right
		single_pos_right_real = []
		single_pos_right_hex = []
		single_pos_right_bin = []
		single_pos_right_fp32 = []
		single_pos_right_fp64 = []

		bin_out_arrays_pos_right = [single_pos_right_real, single_pos_right_hex, single_pos_right_bin, single_pos_right_fp32, single_pos_right_fp64]

		for tests, input_lists, output_lists in zip(test_cases, output_arrays_pos_right, bin_out_arrays_pos_right):
			for i in len(input_lists):
				output_lists.append(gui_entry_parameters(self, input_lists[i], tests, "BIN", 32, 32))

		# Test pattern: single bit, negative value shifted to the right
		single_neg_right_real = []
		single_neg_right_hex = []
		single_neg_right_bin = []
		single_neg_right_fp32 = []
		single_neg_right_fp64 = []

		bin_out_arrays_neg_right = [single_neg_right_real, single_neg_right_hex, single_neg_right_bin, single_neg_right_fp32, single_neg_right_fp64]

		for tests, input_lists, output_lists in zip(test_cases, output_arrays_neg_right, bin_out_arrays_neg_right):
			for i in len(input_lists):
				output_lists.append(gui_entry_parameters(self, input_lists[i], tests, "BIN", 32, 32))

		# Test pattern: single bit, positive value shifted to the left
		single_pos_left_real = []
		single_pos_left_hex = []
		single_pos_left_bin = []
		single_pos_left_fp32 = []
		single_pos_left_fp64 = []

		bin_out_arrays_pos_right = [single_pos_left_real, single_pos_left_hex, single_pos_left_bin, single_pos_left_fp32, single_pos_left_fp64]

		for tests, input_lists, output_lists in zip(test_cases, output_arrays_pos_left, bin_out_arrays_pos_left):
			for i in len(input_lists):
				output_lists.append(gui_entry_parameters(self, input_lists[i], tests, "BIN", 32, 32))

		# Test pattern: single bit, negative value shifted to the left
		single_neg_left_real = []
		single_neg_left_hex = []
		single_neg_left_bin = []
		single_neg_left_fp32 = []
		single_neg_left_fp64 = []

		bin_out_arrays_neg_left = [single_neg_left_real, single_neg_left_hex, single_neg_left_bin, single_neg_left_fp32, single_neg_left_fp64]

		for tests, input_lists, output_lists in zip(test_cases, output_arrays_neg_left, bin_out_arrays_neg_left):
			for i in len(input_lists):
				output_lists.append(gui_entry_parameters(self, input_lists[i], tests, "BIN", 32, 32))
		
		print("Generated binary outputs")
		
		# Step 3: Compare input lists to output lists
		if (output_arrays_pos_right == bin_out_arrays_pos_right):
			print("Positive right test passed")
		else:
			print("Positive right test failed"

		if (output_arrays_neg_right == bin_out_arrays_neg_right):
			print("Negative right test passed")
		else:
			print("Negative right test failed"

		if (output_arrays_pos_left == bin_out_arrays_pos_left):
			print("Positive left test passed")
		else:
			print("Positive left test failed"

		if (output_arrays_neg_left == bin_out_arrays_neg_left):
			print("Negative left test passed")
		else:
			print("Negative left test failed"
			
				