import unittest 
import tkinter as tk 
import itertools
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

	# Create test vectors that will fit into IEEE754 single values
	def test_limited_single_bit_vectors(self):
		# STEP 1: Create the binary test vectors
		
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

		# Test pattern: single bit, positive value shifted to the right
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
		
		# Test pattern: single bit, negative value shifted to the right
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

		# Test pattern: single bit, positive value shifted to the left
		pos_left_seed_value = [0]*11 + ['.'] + [0]*11 + [1]
		single_positive_left_vectors = []

		for i in range(0, 23):
			single_positive_left_vectors.append(pos_left_seed_value)
			pos_left_seed_value = self.single_bit_shifter_left(0, pos_left_seed_value)

		binary_input_file.write("Single Positive Left Vectors" + "\n")
		
		for test, item, int_size, frac_size in zip(test_cases, output_arrays_pos_left, integer_sizes, fraction_sizes): 			
			for i in range(0, len(single_positive_left_vectors)):
				item.append(self.gui_entry_parameters("".join(map(str, single_positive_left_vectors[i])), "BIN", test, int_size, frac_size))
				binary_input_file.write(str(item[i]) + "\n")				

		# Test pattern: single bit, negative value shifted to the left
		neg_left_seed_value = [1]*11 + ['.'] + [1]*11 + [1]
		single_negative_left_vectors = []

		for i in range(0, 23):
			single_negative_left_vectors.append(neg_left_seed_value)
			neg_left_seed_value = self.single_bit_shifter_left(0, neg_left_seed_value)

		binary_input_file.write("Single Negative Left Vectors" + "\n")
		
		for test, item, int_size, frac_size in zip(test_cases, output_arrays_neg_left, integer_sizes, fraction_sizes): 			
			for i in range(0, len(single_negative_left_vectors)):
				item.append(self.gui_entry_parameters("".join(map(str, single_negative_left_vectors[i])), "BIN", test, int_size, frac_size))
				binary_input_file.write(str(item[i]) + "\n")				

		print("Created test vectors")
		
		# STEP 2: Run the test vectors back through the calculator
		binary_output_file = open("binary_output_file.txt", "w")

		# Test pattern: single bit, positive value shifted to the right
		single_pos_right_real = []
		single_pos_right_hex = []
		single_pos_right_bin = []
		single_pos_right_fp32 = []
		single_pos_right_fp64 = []

		bin_out_arrays_pos_right = [single_pos_right_real, single_pos_right_hex, single_pos_right_bin, single_pos_right_fp32, single_pos_right_fp64]
		real_out_arrays_pos_right = [single_pos_right_real, single_pos_right_hex, single_pos_right_bin, single_pos_right_fp32, single_pos_right_fp64]

		binary_output_file.write("Single Positive Right Output Vectors" + "\n")
		
		for tests, input_lists, output_lists, int_size, frac_size in zip(test_cases, output_arrays_pos_right, bin_out_arrays_pos_right, integer_sizes, fraction_sizes):
			binary_output_file.write("Output type = " + str(tests) + "\n")
			
			for i in range(0, len(input_lists)):
				output_lists.append(self.gui_entry_parameters(input_lists[i], tests, "BIN", int_size, frac_size))
				binary_output_file.write(str(output_lists[i]) + "\n")

		# Test pattern: single bit, negative value shifted to the right
		single_neg_right_real = []
		single_neg_right_hex = []
		single_neg_right_bin = []
		single_neg_right_fp32 = []
		single_neg_right_fp64 = []

		bin_out_arrays_neg_right = [single_neg_right_real, single_neg_right_hex, single_neg_right_bin, single_neg_right_fp32, single_neg_right_fp64]

		binary_output_file.write("Single Negative Right Output Vectors" + "\n")
		
		for tests, input_lists, output_lists, int_size, frac_size in zip(test_cases, output_arrays_neg_right, bin_out_arrays_neg_right, integer_sizes, fraction_sizes):
			binary_output_file.write("Output type = " + str(tests) + "\n")
			
			for i in range(0, len(input_lists)):
				output_lists.append(self.gui_entry_parameters(input_lists[i], tests, "BIN", int_size, frac_size))
				binary_output_file.write(str(output_lists[i]) + "\n")

		# Test pattern: single bit, positive value shifted to the left
		single_pos_left_real = []
		single_pos_left_hex = []
		single_pos_left_bin = []
		single_pos_left_fp32 = []
		single_pos_left_fp64 = []

		bin_out_arrays_pos_left = [single_pos_left_real, single_pos_left_hex, single_pos_left_bin, single_pos_left_fp32, single_pos_left_fp64]

		binary_output_file.write("Single Positive Left Output Vectors" + "\n")
		
		for tests, input_lists, output_lists, int_size, frac_size in zip(test_cases, output_arrays_pos_left, bin_out_arrays_pos_left, integer_sizes, fraction_sizes):
			binary_output_file.write("Output type = " + str(tests) + "\n")
			
			for i in range(0, len(input_lists)):
				output_lists.append(self.gui_entry_parameters(input_lists[i], tests, "BIN", int_size, frac_size))
				binary_output_file.write(str(output_lists[i]) + "\n")

		# Test pattern: single bit, negative value shifted to the left
		single_neg_left_real = []
		single_neg_left_hex = []
		single_neg_left_bin = []
		single_neg_left_fp32 = []
		single_neg_left_fp64 = []

		bin_out_arrays_neg_left = [single_neg_left_real, single_neg_left_hex, single_neg_left_bin, single_neg_left_fp32, single_neg_left_fp64]
		
		binary_output_file.write("Single Negative Left Output Vectors" + "\n")
		
		for tests, input_lists, output_lists, int_size, frac_size in zip(test_cases, output_arrays_neg_left, bin_out_arrays_neg_left, integer_sizes, fraction_sizes):
			binary_output_file.write("Output type = " + str(tests) + "\n")
			
			for i in range(0, len(input_lists)):
				output_lists.append(self.gui_entry_parameters(input_lists[i], tests, "BIN", int_size, frac_size))
				binary_output_file.write(str(output_lists[i]) + "\n")
		
		binary_input_file.close()
		binary_output_file.close()
		
		print("Generated binary outputs")
		
		# Step 3: Compare input lists to output lists
		# Put binary inputs and binary outputs together in the same file
		comparison_file = open("binary_comparison.txt", "w")
		
		for tests, output_list in zip(test_cases, bin_out_arrays_pos_right):
			for i in range(0, len(single_positive_right_vectors)):
				comparison_file.write(str(binary_to_real(single_positive_right_vectors[i])) + " " + str(binary_to_real(binary_string_to_int_list(output_list[i]))) + " " + list_to_string(single_positive_right_vectors[i]) + " " + output_list[i] + "\n")
		
		for tests, output_list in zip(test_cases, bin_out_arrays_neg_right):
			for i in range(0, len(single_negative_right_vectors)):
				comparison_file.write(str(binary_to_real(single_negative_right_vectors[i])) + " " + str(binary_to_real(binary_string_to_int_list(output_list[i]))) + " " + list_to_string(single_negative_right_vectors[i]) + " " + output_list[i] + "\n")
		
		for tests, output_list in zip(test_cases, bin_out_arrays_pos_left):
			for i in range(0, len(single_positive_left_vectors)):
				comparison_file.write(str(binary_to_real(single_positive_left_vectors[i])) + " " + str(binary_to_real(binary_string_to_int_list(output_list[i]))) + " " + list_to_string(single_positive_left_vectors[i]) + " " + output_list[i] + "\n")
		
		for tests, output_list in zip(test_cases, bin_out_arrays_neg_left):
			for i in range(0, len(single_negative_left_vectors)):
				comparison_file.write(str(binary_to_real(single_negative_left_vectors[i])) + " " + str(binary_to_real(binary_string_to_int_list(output_list[i]))) + " " + list_to_string(single_negative_left_vectors[i]) + " " + output_list[i] + "\n")
		
		comparison_file.close()
		
		with open("binary_comparison.txt", "r") as file:
		    for line_num, line in enumerate(file, 1):
		        # Skip empty lines
		        if not line.strip(): 
		            continue
		            
		        # Split the row into two string columns, then convert to floats
		        col1, col2, col3, col4 = map(float, line.split())
		        
		        # Compare them
		        if col1 != col2:
		            print(f"Mismatch at line {line_num}: Column 1 ({col1}) != Column 2 ({col2})")

		#---------- MATH OPERATION TESTS ----------
		# STEP 4
		# Use the data from the output of step 1 above, pair them off, and then pass them through four times,
		# once for each math operation
		
		math_operations = ["+", "-", "*", "/"]
		
		test_a_real_add = []
		test_a_real_sub = []
		test_a_real_mult = []
		test_a_real_div = []
		
		test_a_real_lists = [test_a_real_add, test_a_real_sub, test_a_real_mult, test_a_real_div]

		test_a_hex_add = []
		test_a_hex_sub = []
		test_a_hex_mult = []
		test_a_hex_div = []
		
		test_a_hex_lists = [test_a_hex_add, test_a_hex_sub, test_a_hex_mult, test_a_hex_div]
		
		test_a_bin_add = []
		test_a_bin_sub = []
		test_a_bin_mult = []
		test_a_bin_div = []
		
		test_a_bin_lists = [test_a_bin_add, test_a_bin_sub, test_a_bin_mult, test_a_bin_div]
		
		test_a_fp32_add = []
		test_a_fp32_sub = []
		test_a_fp32_mult = []
		test_a_fp32_div = []
		
		test_a_fp32_lists = [test_a_fp32_add, test_a_fp32_sub, test_a_fp32_mult, test_a_fp32_div]
		
		test_a_fp64_add = []
		test_a_fp64_sub = []
		test_a_fp64_mult = []
		test_a_fp64_div = []
		
		test_a_fp64_lists = [test_a_fp64_add, test_a_fp64_sub, test_a_fp64_mult, test_a_fp64_div]
		
		test_b_real_add = []
		test_b_real_sub = []
		test_b_real_mult = []
		test_b_real_div = []
		
		test_b_real_lists = [test_b_real_add, test_b_real_sub, test_b_real_mult, test_b_real_div]

		test_b_hex_add = []
		test_b_hex_sub = []
		test_b_hex_mult = []
		test_b_hex_div = []
		
		test_b_hex_lists = [test_b_hex_add, test_b_hex_sub, test_b_hex_mult, test_b_hex_div]
		
		test_b_bin_add = []
		test_b_bin_sub = []
		test_b_bin_mult = []
		test_b_bin_div = []
		
		test_b_bin_lists = [test_b_bin_add, test_b_bin_sub, test_b_bin_mult, test_b_bin_div]
		
		test_b_fp32_add = []
		test_b_fp32_sub = []
		test_b_fp32_mult = []
		test_b_fp32_div = []
		
		test_b_fp32_lists = [test_b_fp32_add, test_b_fp32_sub, test_b_fp32_mult, test_b_fp32_div]
		
		test_b_fp64_add = []
		test_b_fp64_sub = []
		test_b_fp64_mult = []
		test_b_fp64_div = []
		
		test_b_fp64_lists = [test_b_fp64_add, test_b_fp64_sub, test_b_fp64_mult, test_b_fp64_div]
		
		test_a_lists = [test_a_real_lists, test_a_hex_lists, test_a_bin_lists, test_a_fp32_lists, test_a_fp64_lists]
		test_b_lists = [test_b_real_lists, test_b_hex_lists, test_b_bin_lists, test_b_fp32_lists, test_b_fp64_lists]
		
		for tests, test_a, test_b, pos_right, neg_right, pos_left, neg_left, int_size, frac_size in zip(test_cases, test_a_lists, test_b_lists, output_arrays_pos_right, output_arrays_neg_right, output_arrays_pos_left, output_arrays_neg_left, integer_sizes, fraction_sizes):	# 5 iterations
			for math_a, math_b, op in zip(test_a, test_b, math_operations):	# 4 iterations
				for i in range(0, len(pos_right)):
					input_data_a = pos_right[i] + op + neg_left[i]
					math_a.append(self.gui_entry_parameters(input_data_a, tests, "BIN", int_size, frac_size))
					
					print(len(pos_right), len(neg_right), len(pos_left), len(neg_left))
					print(pos_right[i])
					
					if (op == '+'):
						math_a_real_result = binary_to_real(single_positive_right_vectors[i]) + binary_to_real(single_negative_left_vectors[i])
					elif (op == '-'):
						math_a_real_result = binary_to_real(single_positive_right_vectors[i]) - binary_to_real(single_negative_left_vectors[i])
					elif (op == '*'):
						math_a_real_result = binary_to_real(single_positive_right_vectors[i]) * binary_to_real(single_negative_left_vectors[i])
					elif (op == '/'):
						math_a_real_result = binary_to_real(single_positive_right_vectors[i]) / binary_to_real(single_negative_left_vectors[i])
					
					math_a_real = binary_to_real(binary_string_to_int_list(math_a[i]))
					
					if (math_a_real_result != math_a_real):
						print("Mismatch: output A = ", math_a_real, "actual = ", math_a_real_result)
					
					input_data_b = neg_right[i] + op + pos_left[i]
					math_b.append(self.gui_entry_parameters(input_data_b, tests, "BIN", int_size, frac_size))
					
					if (op == '+'):
						math_b_real_result = binary_to_real(single_negative_right_vectors[i]) + binary_to_real(single_positive_left_vectors[i])
					elif (op == '-'):
						math_b_real_result = binary_to_real(single_negative_right_vectors[i]) - binary_to_real(single_positive_left_vectors[i])
					elif (op == '*'):
						math_b_real_result = binary_to_real(single_negative_right_vectors[i]) * binary_to_real(single_positive_left_vectors[i])
					elif (op == '/'):
						math_b_real_result = binary_to_real(single_negative_right_vectors[i]) / binary_to_real(single_positive_left_vectors[i])
					
					math_b_real = binary_to_real(binary_string_to_int_list(math_b[i]))
					
					if (math_b_real_result != math_b_real):
						print("Mismatch: output B = ", math_b_real, "actual = ", math_b_real_result)
		
if __name__ == '__main__':
    unittest.main()				