import tkinter as tk
from tkinter import ttk
import struct
import time
import math
import numpy as np
from dataclasses import dataclass
from typing import List, Literal
from binary_support import precision_profile, lookup_table, twos_complement, binary_string_to_int_list, int_list_to_binary_string, binary_point_removal, twos_complement_bin_rational
from binary_conversions import real_to_twos_comp_binary, hexadecimal_to_binary, ieee754_hex_to_binary, binary_to_real, binary_to_hexadecimal, binary_to_ieee754
from binary_math import binary_division, binary_multiplier, binary_adder, binary_subtraction

class FpgaCalculator:
	def __init__(self, root):
		self.root = root
		self.root.title("FPGA Developer Calculator")
		self.root.geometry("450x600")
		
		# --- Variables ---
		self.main_display_var = tk.StringVar(value="")
		self.aux_display_var = tk.StringVar(value="")
		self.input_mode = tk.StringVar(value="REAL")
		self.output_mode = tk.StringVar(value="REAL")
		
		self.int_bits = tk.IntVar(value=16)
		self.frac_bits = tk.IntVar(value=16)
		
		self.integer_size1 = 0
		self.fraction_size1 = 0
		self.integer_size2 = 0
		self.fraction_size2 = 0
		
		# Place holders that will eventually get calculated
		self.integer_size_out = 16
		self.fraction_size_out = 16
		self.nibble_size = 4
		
		self.create_widgets()
		
		self.hex_negative_list = ["8", "9", "A", "B", "C", "D", "E", "F", "a", "b", "c", "d", "e", "f", ]
		self.operand1_present = False
		self.operator_present = False
		self.operand2_present = False
		self.math_operation = ""
		self.button_push_result = ""
		self.MAX_FLOAT_SINGLE = 3.4028234663852886e+38
		self.MAX_FLOAT_DOUBLE = 1.7976931348623157e+308
		self.integer_component = 0
		self.float_sign1 = 0
		self.exponent_op1 = 0
		self.mantissa_op1 = 0
		self.float_sign2 = 0
		self.exponent_op2 = 0
		self.mantissa_op2 = 0
		self.float_sign_result = 0
		self.exponent_op_result = 0
		self.mantissa_op_result = 0
		self.current_profile = precision_profile["SINGLE"]
	def create_widgets(self):
		# 1. Main Display
		main_display_frame = ttk.Frame(self.root, padding=10)
		main_display_frame.pack(fill="x")
		
		main_display_label = ttk.Label(main_display_frame, text="Input Window")
		main_display_label.pack(side="top", anchor="w", pady=(0, 5)) 
		
		self.main_display = ttk.Entry(main_display_frame, textvariable=self.main_display_var, font=("Courier", 12), justify="right")
		self.main_display.pack(fill="x", ipady=10)

		# 2. Configuration Panel (Bit Widths)
		config_frame = ttk.LabelFrame(self.root, text="Binary Division and Hexadecimal Output Defaults ", padding=10)
		config_frame.pack(fill="x", padx=10, pady=5)
		
		ttk.Label(config_frame, text="Integer Bits:").grid(row=0, column=0, sticky="w")
		ttk.Entry(config_frame, textvariable=self.int_bits, width=5).grid(row=0, column=1, padx=5)
		
		ttk.Label(config_frame, text="Fraction Bits:").grid(row=0, column=2, sticky="w", padx=10)
		ttk.Entry(config_frame, textvariable=self.frac_bits, width=5).grid(row=0, column=3, padx=5)

		# 2. Secondary display
		aux_display_frame = ttk.Frame(self.root, padding=10)
		aux_display_frame.pack(fill="x")
		
		aux_display_label = ttk.Label(aux_display_frame, text="Output Window")
		aux_display_label.pack(side="top", anchor="w", pady=(0, 5)) 
		
		self.aux_display = ttk.Entry(aux_display_frame, textvariable=self.aux_display_var, font=("Courier", 12), justify="right")
		self.aux_display.pack(fill="x", ipady=10)
		
		# 3. Format Selectors
		format_frame = ttk.Frame(self.root, padding=10)
		format_frame.pack(fill="x", padx=10)

		# Input Modes (Left side)
		in_lbl = ttk.LabelFrame(format_frame, text=" Input Format ", padding=5)
		in_lbl.pack(side="left", fill="both", expand=True, padx=5)
		self.modes = [("Real", "REAL"), ("Hex", "HEX"), ("2's Comp Bin", "BIN"), ("IEEE-754 Single", "FP32"), ("IEEE-754 Double", "FP64")]
		
		for text, mode in self.modes:
			ttk.Radiobutton(in_lbl, text=text, variable=self.input_mode, value=mode, command=self.input_mode_changed).pack(anchor="w")
			
		# Output Modes (Right side)
		out_lbl = ttk.LabelFrame(format_frame, text=" Output Format ", padding=5)
		out_lbl.pack(side="right", fill="both", expand=True, padx=5)
		for text, mode in self.modes:
			ttk.Radiobutton(out_lbl, text=text, variable=self.output_mode, value=mode, command=self.output_mode_changed).pack(anchor="w")

		# 4. Calculator Buttons
		btn_frame = ttk.Frame(self.root, padding=10)
		btn_frame.pack(fill="both", expand=True, padx=10, pady=5)
		
		buttons = [
			('7', '8', '9', '/'),
			('4', '5', '6', '*'),
			('1', '2', '3', '-'),
			('0', '.', 'R', '+'),
			('A', 'B', 'C', 'D'),
			('E', 'F', 'Enter', '=')
		]
		
		for r, row in enumerate(buttons):
			for c, val in enumerate(row):
				# Map spanning for Enter or extra buttons if needed
				btn = ttk.Button(btn_frame, text=val, command=lambda v=val: self.on_button_click(v))
				btn.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
				
		for i in range(6):
			btn_frame.rowconfigure(i, weight=1)
		for i in range(4):
			btn_frame.columnconfigure(i, weight=1)

	def on_button_click(self, char):
		self.button_push_result = char
		
		if char == 'R':
			self.main_display_var.set("")
			self.aux_display_var.set("")
			self.integer_size1 = 0
			self.fraction_size1 = 0
			self.integer_size2 = 0
			self.fraction_size2 = 0
		elif char in ('=', 'Enter'):
			operand1, operand2, operator = self.get_operands()
			self.math_operation = operator
			operand1_data_error = False
			operand2_data_error = False
			operand_error = False
			bin_math_error = False
			self.nibble_size = self.int_bits.get()//4
			
			# Error checking
			if (self.input_mode.get() == "REAL"):
				operand1_data_error = self.verify_real_input(operand1)
				
				if (operand2 != ""):
					operand2_data_error = self.verify_real_input(operand2)
			elif (self.input_mode.get() == "HEX"):
				if (len(operand1) < self.nibble_size) and (len(operand1) > 0):
					operand1_padding = self.nibble_size
					
					if (any(item in operand1[0] for item in self.hex_negative_list)):
						operand1 = operand1.rjust(operand1_padding, "F")
					else:
						operand1 = operand1.rjust(operand1_padding, "0")
					
				operand1_data_error = self.verify_hex_input(operand1)
				
				if (self.operand2_present == True):
					if (len(operand2) < self.nibble_size) and (len(operand2) > 0):
						operand2_padding = self.nibble_size

						if (any(item in operand2[0] for item in self.hex_negative_list)):
							operand2 = operand2.rjust(operand2_padding, "F")
						else:
							operand2 = operand2.rjust(operand2_padding, "0")
							
					operand2_data_error = self.verify_hex_input(operand2)
			elif (self.input_mode.get() == "BIN"):
				operand1_data_error = self.verify_bin_input(operand1)
				
				if (operand2 != ""):
					operand2_data_error = self.verify_bin_input(operand2)
				elif (self.operator_present == True) and (self.operand2_present == False):
					operand2_data_error = True
			elif (self.input_mode.get() == "FP32"):
				self.exponent_size = 7
				self.mantissa_size = 23
				operand1_data_error = self.verify_fp32_input(operand1)
				
				if (self.operand2_present == True):
					operand2_data_error = self.verify_fp32_input(operand2)
			elif (self.input_mode.get() == "FP64"):
				self.exponent_size = 11
				self.mantissa_size = 52
				operand1_data_error = self.verify_fp64_input(operand1)
				
				if (self.operand2_present == True):
					operand2_data_error = self.verify_fp64_input(operand2)

			operator_error = self.verify_operator(operator)
			
			if (operand1_data_error == False) and (operand2_data_error == False) and (operator_error == False):
				operand1_binary = self.convert_to_binary(operand1, self.input_mode.get())
				
				if (self.operand2_present == True):
					operand2_binary = self.convert_to_binary(operand2, self.input_mode.get())
					binary_result = self.binary_math_operation(operand1_binary, operand2_binary, operator)
					calculator_result = self.convert_from_binary(binary_result, self.output_mode.get())
				else:
					calculator_result = self.convert_from_binary(operand1_binary, self.output_mode.get())

				self.aux_display_var.set(calculator_result)
			else:
				self.main_display_var.set("")
				self.aux_display_var.set("ERROR")
		else:
			current = self.main_display_var.get()
			self.main_display_var.set(current + str(char))

	def get_operands(self):
		raw_input = self.main_display_var.get()
		operand1, operator, operand2 = self.parse_input_string(raw_input)
		return operand1, operand2, operator
		
	def parse_input_string(self, input_string):
		# No regex options would work here, so this is a brute force state machine
		state = 'Empty_String_Check'
		data_length = len(input_string)
		input_index = 0
		left = ""
		op = ""
		right = ""
		self.operand1_present = False
		self.operator_present = False
		self.operand2_present = False
		
#		print('parser input string = ', input_string)
		
		while (True):
			match state:
				case 'Empty_String_Check':
					if not input_string:
						return left, op, right
					else:
						state = 'First_Character'
				case 'First_Character':
					if (input_string[input_index] == '+'):
						state = 'First_Operand'
					elif (input_string[input_index] == '-') or (input_string[input_index].isalnum()):
						left += input_string[input_index]
						
						if (len(input_string) > 1):
							input_index = input_index + 1
							state = 'First_Operand'
						else:
							return left, op, right
					else:
						return left, op, right
				case 'First_Operand':
					while input_string[input_index] not in ("+", "-", "*", "/", ""):
						left += input_string[input_index]

						if (input_index < data_length-1):
							input_index = input_index + 1
						else:
							self.operand1_present = True
							return left, op, right
					else:
						self.operand1_present = True
						self.operator_present = True
						op = input_string[input_index]
						input_index = input_index + 1

					if (input_index < len(input_string)):
						if (input_string[input_index] not in ("")):
							state = 'Second_Operand'
						else:
							self.operand2_present = False
							return left, op, right
					else:
						self.operand2_present = False
						return left, op, right
				case 'Second_Operand':
					while input_string[input_index] not in (""):
						right += input_string[input_index]
						
						if (input_index < data_length-1):
							input_index = input_index + 1
						else:
							self.operand2_present = True
							return left, op, right

					self.operand2_present = True
					return left, op, right
		
	def verify_real_input(self, input_string):
		try:
			float(input_string)
			return False
		except ValueError:
			return True
	
	def verify_hex_input(self, input_string):
		try:
			int(input_string, 16)
			
			if (len(input_string) > (self.int_bits.get() + self.frac_bits.get())/4):
				return True
			
			return False
		except ValueError:
			return True
	
	def verify_bin_input(self, input_string):
		try:
			int(input_string.replace('.', ''), 2) # Enforces 0s and 1s only
			return ((input_string.count('.') > 1) or ((input_string[0] != '0') and (input_string[0] != '1')) or (input_string[-1] == '.'))
		except ValueError:
			return True

	def is_valid_hex(self, s):
		"""Returns True if valid hex, False if invalid."""
		try:
			int(s, 16)
			return True
		except ValueError:
			return False	
			
	def verify_fp32_input(self, input_string):
		return len(input_string) != 8 or not self.is_valid_hex(input_string)
		
	def verify_fp64_input(self, input_string):
		return len(input_string) != 16 or not self.is_valid_hex(input_string)

	def verify_operator(self, input_string):
		return input_string not in "+-*/"

	def convert_to_binary(self, operand, input_mode):
		if (input_mode == "REAL"):
			n_binary_string = real_to_twos_comp_binary(operand, self.int_bits.get(), self.frac_bits.get())
			n_int_list = binary_string_to_int_list(n_binary_string)
		elif (input_mode == "HEX"):
			n_binary_string = hexadecimal_to_binary(operand, self.int_bits.get(), self.frac_bits.get(), lookup_table)
			n_int_list = binary_string_to_int_list(n_binary_string)
		elif (input_mode == "FP32"):
			self.current_profile = precision_profile["SINGLE"]
			p = self.current_profile
			n_binary_string = ieee754_hex_to_binary(operand, p, lookup_table)
			n_int_list = n_binary_string
		elif (input_mode == "FP64"):
			self.current_profile = precision_profile["DOUBLE"]
			p = self.current_profile
			n_binary_string = ieee754_hex_to_binary(operand, p, lookup_table)
			n_int_list = n_binary_string
		else: 
			n_int_list = binary_string_to_int_list(operand)
			
		return n_int_list
	
	def binary_math_operation(self, operand1, operand2, operator):
		if (operator == "/"):
			if (self.output_mode.get() == "FP32"):
				self.current_profile = precision_profile["SINGLE"]
				p = self.current_profile

				if (1 + p.exponent_size + p.mantissa_size) < (self.int_bits.get() + self.frac_bits.get()):
					max_size = self.int_bits.get() + self.frac_bits.get()
				else:
					max_size = 64
			elif (self.output_mode.get() == "FP64"):
				self.current_profile = precision_profile["DOUBLE"]
				p = self.current_profile
				
				if (1 + p.exponent_size + p.mantissa_size) < (self.int_bits.get() + self.frac_bits.get()):
					max_size = self.int_bits.get() + self.frac_bits.get()
				else:
					max_size = 128
			else:
				max_size = self.int_bits.get() + self.frac_bits.get()
			
			if ('.' in operand1) or ('.' in operand2):
				operand1_no_bin_point, operand2_no_bin_point, op1_radix_index, op2_radix_index, fraction_size = binary_point_removal(operand1, operand2)
			else:
				operand1_no_bin_point = operand1
				operand2_no_bin_point = operand2
				fraction_size = 0
			
			if (operand1[0] == 1):
				operand1_2s_comp, op1_carry = twos_complement(operand1_no_bin_point)
				sign_operand1 = 1
			else:
				operand1_2s_comp = operand1_no_bin_point
				sign_operand1 = 0
			
			if (operand2[0] == 1):
				operand2_2s_comp, op2_carry = twos_complement(operand2_no_bin_point)
				sign_operand2 = 1
			else:
				operand2_2s_comp = operand2_no_bin_point
				sign_operand2 = 0
			
#			print("Fraction size = ", fraction_size)
			
			if ('.' in operand1):
				operand1_bin_point = operand1_2s_comp[:(len(operand1_2s_comp) - fraction_size)] + ['.'] + operand1_2s_comp[(len(operand1_2s_comp) - fraction_size):]
			else:
				if (len(operand1) < len(operand1_2s_comp)):
					operand1_bin_point = operand1_2s_comp[:len(operand1)] + ['.'] + operand1_2s_comp[len(operand1):]
				else:
					operand1_bin_point = operand1_2s_comp + ['.']

			if ('.' in operand2):
				operand2_bin_point = operand2_2s_comp[:(len(operand2_2s_comp) - fraction_size)] + ['.'] + operand2_2s_comp[(len(operand2_2s_comp) - fraction_size):]
			else:
				if (len(operand2) < len(operand2_2s_comp)):
					operand2_bin_point = operand2_2s_comp[:len(operand2)] + ['.'] + operand2_2s_comp[len(operand2):]
				else:
					operand2_bin_point = operand2_2s_comp + ['.']
			
			quotient = binary_division(operand1_bin_point, operand2_bin_point, max_size)
			
#			print("quotient raw = ", "".join(map(str, quotient)))
			
			if ((sign_operand1 ^ sign_operand2) == 1):
				quotient_no_bin_point, null_output, quotient_radix_index, null_radix_index, fraction_size = binary_point_removal(quotient, [''])
				
				if (self.int_bits.get() > quotient_radix_index):
					quotient_extended = [0]*(self.int_bits.get() - quotient_radix_index) + quotient_no_bin_point
					quotient_2s_comp, carry_quotient = twos_complement(quotient_extended)
					quotient_2s_comp_bin_point = quotient_2s_comp[:self.int_bits.get()] + ['.'] + quotient_2s_comp[self.int_bits.get():]
				else:
					quotient_extended = quotient_no_bin_point
					quotient_2s_comp, carry_quotient = twos_complement(quotient_extended)
					quotient_2s_comp_bin_point = quotient_2s_comp[:quotient_radix_index] + ['.'] + quotient_2s_comp[quotient_radix_index:]
				
				
#				print("quotient 2s comp = ", "".join(map(str, quotient_2s_comp_bin_point)))
				math_result_2s_comp = quotient_2s_comp_bin_point
			else:
				math_result_2s_comp = quotient
			
#			print("quotient = ", "".join(map(str, math_result_2s_comp)))
			math_result = math_result_2s_comp
		elif (operator == "*"):
			math_result = binary_multiplier(operand1, operand2)
		elif (operator == "+"):
			addend_a, addend_b, a_radix_index, b_radix_index, fraction_size = binary_point_removal(operand1, operand2)
			
			if (a_radix_index > b_radix_index):
				integer_size = a_radix_index
			elif (b_radix_index >= a_radix_index):
				integer_size = b_radix_index
			
			n_sum, n_carry = binary_adder(addend_a, addend_b)
			
			if (n_carry == 1):
				sum_result = [n_carry] + n_sum
			else:
				sum_result = n_sum
			
			binary_point_index = len(sum_result) - fraction_size
			math_result = sum_result[:binary_point_index] + ['.'] + sum_result[binary_point_index:]
		elif (operator == "-"):
			math_result = binary_subtraction(operand1, operand2)
	
		return math_result
	
	def convert_from_binary(self, operand, output_mode):
		if (output_mode == "REAL"):
			conversion_result = binary_to_real(operand)
		elif (output_mode == "HEX"):
			conversion_result = binary_to_hexadecimal(operand, lookup_table)
		elif (output_mode == "FP32"):
			conversion_result = binary_to_ieee754(operand, precision_profile["SINGLE"], lookup_table)
		elif (output_mode == "FP64"):
			conversion_result = binary_to_ieee754(operand, precision_profile["DOUBLE"], lookup_table)
		else:
			operand_int_list = int_list_to_binary_string(operand, len(operand))
			conversion_result = "".join(operand_int_list)
		
		return conversion_result                                                                                                                  
	
	def input_mode_changed(self):
		mode = self.input_mode.get()

		if mode == "HEX":
			dialog = tk.Toplevel(self.root)
			dialog.title("Hexadecimal Options")
			dialog.geometry("400x175")

			ttk.Label(
				dialog,
				text=f"HEX input OPTIONS",
				font=("Arial", 10, "bold")
			).pack(pady=10)

			ttk.Label(
				dialog,
				text="Set the number of integer bits and the number of fraction bits and allow enough room for the sign bit. No need for '0x' or for '.'. Sign extension will be done automatically if not enough nibbles are entered and it will be based on the most signficant nibble",
				wraplength = 350,
				justify = "left"
			).pack(padx=10, pady=10)

			dialog.after(10000, dialog.destroy)

	def output_mode_changed(self):
		mode = self.output_mode.get()

		if mode == "HEX":
			dialog = tk.Toplevel(self.root)
			dialog.title("Hexadecimal Options")
			dialog.geometry("400x175")

			ttk.Label(
				dialog,
				text=f"HEX output OPTIONS",
				font=("Arial", 10, "bold")
			).pack(pady=10)

			ttk.Label(
				dialog,
				text="The number of bits in the output will be equal to 'Integer bits' + 'Fraction_bits' if the input is 'BIN' or 'HEX'. The value will have no hexadecimal point and it will be scaled by the number of fractional bits.",
				wraplength = 350,
				justify = "left"
			).pack(padx=10, pady=10)

			dialog.after(10000, dialog.destroy)
