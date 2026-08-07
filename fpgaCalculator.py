import tkinter as tk
from tkinter import ttk
import struct
from binaryConversions import binary_to_fixed_point
from binaryConversions import fixed_point_to_binary
from ieee754Conversions import ieee754_hex_to_float
from ieee754Conversions import float_to_ieee754_hex
from decimal import Decimal

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
	def create_widgets(self):
		# 1. Main Display
		main_display_frame = ttk.Frame(self.root, padding=10)
		main_display_frame.pack(fill="x")
		
		self.main_display = ttk.Entry(main_display_frame, textvariable=self.main_display_var, font=("Courier", 12), justify="right")
		self.main_display.pack(fill="x", ipady=10)

		# 2. Configuration Panel (Bit Widths)
		config_frame = ttk.LabelFrame(self.root, text=" Binary Output Defaults ", padding=10)
		config_frame.pack(fill="x", padx=10, pady=5)
		
		ttk.Label(config_frame, text="Integer Bits:").grid(row=0, column=0, sticky="w")
		ttk.Entry(config_frame, textvariable=self.int_bits, width=5).grid(row=0, column=1, padx=5)
		
		ttk.Label(config_frame, text="Fraction Bits:").grid(row=0, column=2, sticky="w", padx=10)
		ttk.Entry(config_frame, textvariable=self.frac_bits, width=5).grid(row=0, column=3, padx=5)

		# 2. Secondary display
		aux_display_frame = ttk.Frame(self.root, padding=10)
		aux_display_frame.pack(fill="x")
		
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
			ttk.Radiobutton(out_lbl, text=text, variable=self.output_mode, value=mode).pack(anchor="w")

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
		if char == 'R':
			self.main_display_var.set("")
			self.aux_display_var.set("")
			self.integer_size1 = 0
			self.fraction_size1 = 0
			self.integer_size2 = 0
			self.fraction_size2 = 0
		elif char in ('=', 'Enter'):
			operand1, operand2, operator = self.get_operands()
			operand1_data_error = False
			operand2_data_error = False
			operand_error = False
			
			print("operand2 present ", self.operand2_present)
			
			# Error checking
			if (self.input_mode.get() == "REAL"):
				operand1_data_error = self.verify_real_input(operand1)
				
				if (operand2 != ""):
					operand2_data_error = self.verify_real_input(operand2)
			elif (self.input_mode.get() == "HEX"):
				if (len(operand1) < self.nibble_size):
					operand1_padding = self.nibble_size
					
					if (any(item in operand1[0] for item in self.hex_negative_list)):
						operand1 = operand1.rjust(operand1_padding, "F")
					else:
						operand1 = operand1.rjust(operand1_padding, "0")
					
				operand1_data_error = self.verify_hex_input(operand1)
				
				if (self.operand2_present == True):
					if (len(operand2) < self.nibble_size):
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
			elif (self.input_mode.get() == "FP32"):
				operand1_data_error = self.verify_fp32_input(operand1)
				
				if (self.operand2_present == True):
					operand2_data_error = self.verify_fp32_input(operand2)
			elif (self.input_mode.get() == "FP64"):
				operand1_data_error = self.verify_fp64_input(operand1)
				
				if (self.operand2_present == True):
					operand2_data_error = self.verify_fp64_input(operand2)

			operator_error = self.verify_operator(operator)
			
			if (operand1_data_error == False) and (operand2_data_error == False) and (operator_error == False):
				if (self.input_mode.get() == "BIN"):
					self.integer_size1, self.fraction_size1 = self.count_input_bits(operand1)

					if (self.operand2_present == True):
						self.integer_size2, self.fraction_size2 = self.count_input_bits(operand2)
				else:
					operand1_float, operand2_float = self.get_float_operands(operand1, operand2, operator)	
				
				if (self.input_mode.get() == "BIN"):
					if (self.operand2_present == True):
						result_math, result_int_size, result_frac_size, bin_math_error = self.calculate_binary_result(operand1, operand2, operator)
					else:
						operand1_int = binary_to_fixed_point(operand1, self.integer_size1, self.fraction_size1)
						result_math = operand1_int >> self.fraction_size1
						result_int_size = self.integer_size1
						result_frac_size = self.fraction_size1
						bin_math_error = False
					
					if (bin_math_error == False):
						result_requested = self.convert_output_binary(result_math, result_int_size, result_frac_size)
					else:
						result_requested = "ERROR"
				else:
					if (self.operand2_present == True):
						result_math = self.calculate_real_result(operand1_float, operand2_float, operator)
					else:
						result_math = operand1_float
					
					if (self.output_mode.get() != "BIN"):
						result_requested = self.convert_output_float(result_math)
					else:
						result_scaled_int = int(result_math * 2**self.frac_bits.get())
						result_requested = self.convert_output_binary(result_scaled_int, self.int_bits.get(), self.frac_bits.get())
						
					bin_math_error = False

				print(result_requested, result_math)
				self.main_display_var.set("")
				self.main_display_var.set(result_requested)

				if (bin_math_error == False):
					if (self.input_mode.get() == "BIN") and (result_frac_size > 0) and (self.operand2_present == True):
						self.aux_display_var.set(result_math/2**result_frac_size)
					else:								
						self.aux_display_var.set(result_math)
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

	def convert_text_to_type(self, input_string):
		if (self.input_mode.get() == "REAL"):
			operand_float = float(input_string)
		elif (self.input_mode.get() == "HEX"):
			if (any(item in input_string[0] for item in self.hex_negative_list)):
				operand_float = float(int(input_string, 16) - (1 << (len(input_string*4))))
			else:
				operand_float = float(int(input_string, 16))
		elif (self.input_mode.get() == "FP32"):
			operand_float = ieee754_hex_to_float(input_string, False)
		elif (self.input_mode.get() == "FP64"):
			operand_float = ieee754_hex_to_float(input_string, True)
		else:
			print('Unknown data format for operand')
		return operand_float

	def get_float_operands(self, operand1, operand2, operator):
		operand1_float = self.convert_text_to_type(operand1)
		
		if self.operand2_present == True:			
			operand2_float = self.convert_text_to_type(operand2)
		else:
			operand2_float = 0
			
		return operand1_float, operand2_float
		
	def calculate_real_result(self, operand1, operand2, operator):
		# TODO: Implement expression splitting (val1, op, val2) 
		# and conversions based on self.input_mode / self.output_mode
		print(operand1, operand2, operator)
		
		if (operator == "+"):
			result = operand1 + operand2
		elif (operator == "-"):
			result = operand1 - operand2
		elif (operator == "*"):
			result = operand1 * operand2
		elif (operator == "/"):
			result = operand1 / operand2
		else:
			result = operand1
			
		return result
		
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
						input_index = input_index + 1
						state = 'First_Operand'
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

					if (input_string[input_index] not in ("")):
						state = 'Second_Operand'
					else:
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
		
	def convert_output_float(self, input_float):
		print(input_float)
		
		if (self.output_mode.get() == "REAL"):
			output_data = input_float
		elif (self.output_mode.get() == "HEX"):
			input_scaled = input_float * (2**self.frac_bits.get())
			self.nibble_size = self.int_bits.get()//4
			input_int = int(input_scaled)
			output_data = hex(input_int)
		elif (self.output_mode.get() == "BIN"):
			output_data = float.hex(input_float)
		elif (self.output_mode.get() == "FP32"):
			output_data = float_to_ieee754_hex(input_float, False)
		elif (self.output_mode.get() == "FP64"):
			output_data = float_to_ieee754_hex(input_float, True)
		else:
			print('Unknown data format for output')
		
		return output_data
	
	def calculate_binary_result(self, input_string1, input_string2, operator):
		binary_error = False
		
		# 1. Align the binary points
		if (self.fraction_size1 > self.fraction_size2):
			padded_integer1 = input_string1
			padded_integer2 = input_string2 + ("0" * (self.fraction_size1 - self.fraction_size2))
			fractional_bits = self.fraction_size1
			fraction_difference = self.fraction_size1 - self.fraction_size2
		elif (self.fraction_size1 < self.fraction_size2):
			padded_integer1 = input_string1 + ("0" * (self.fraction_size2 - self.fraction_size1))
			padded_integer2 = input_string2
			fractional_bits = self.fraction_size2
			fraction_difference = self.fraction_size2 - self.fraction_size1
		else:
			padded_integer1 = input_string1
			padded_integer2 = input_string2
			fractional_bits = self.fraction_size1
			fraction_difference = 0

		if (self.integer_size1 == 1) and (input_string1[0] == "0"):
			math_int_size1 = 0
		else:
			math_int_size1 = self.integer_size1
			
		if (self.integer_size2 == 1) and (input_string2[0] == "0"):
			math_int_size2 = 0
		else:
			math_int_size2 = self.integer_size2
			
		# 2. Drop the binary point and convert to integer
		if (math_int_size1 == 0):
			integer_val1 = int(padded_integer1[2:], 2)
			scaled_integer1 = integer_val1
		elif (self.fraction_size1 > 0):
			integer_val1 = binary_to_fixed_point(padded_integer1, math_int_size1, fractional_bits)
			scaled_integer1 = integer_val1
		else:
			integer_val1 = int(padded_integer1, 2)
			
			if (integer_val1 & (1 << (self.integer_size1 + fraction_difference - 1))) and (self.integer_size1 > 0):
				scaled_integer1 = integer_val1 - (1 << (self.integer_size1 + fraction_difference))		
			else:
				scaled_integer1 = integer_val1

		extended_integer1 = scaled_integer1
		
		if (operator != ""):
			if (math_int_size2 == 0):
				integer_val2 = int(padded_integer2[2:], 2)
				scaled_integer2 = integer_val2
			elif (self.fraction_size2 > 0):
				integer_val2 = binary_to_fixed_point(padded_integer2, math_int_size2, fractional_bits)
				scaled_integer2 = integer_val2
			else:
				integer_val2 = int(padded_integer2, 2)

				if (integer_val2 & (1 << (self.integer_size2 + fraction_difference - 1))):
					scaled_integer2 = integer_val2 - (1 << (self.integer_size2 + fraction_difference))
				else:
					scaled_integer2 = integer_val2
		else:
			scaled_integer2 = 0
		
		# Sign extend
#		if (input_string2[0] == '1'):
#			extended_integer2 = scaled_integer2 - (1 << (math_int_size + fractional_bits))
#		else:
		extended_integer2 = scaled_integer2
		
		# DEBUG
		print("MATH INPUT VALUES")
		print("Counts")
		print(fractional_bits, math_int_size1, math_int_size2)
		print("Operand1")
		print(padded_integer1, integer_val1, scaled_integer1)
	
		if (input_string2 != ""):
			print("Operand2")
			print(padded_integer2, integer_val2, scaled_integer2)
		# DEBUG
		
		if (operator == "+"):
			integer_sum = extended_integer1 + extended_integer2
			integer_size = max(math_int_size1, math_int_size2) + 1
			fraction_size = fractional_bits
			result = integer_sum
		elif (operator == "-"):
			difference = extended_integer1 - extended_integer2
			integer_size = max(math_int_size1, math_int_size2)
			fraction_size = fractional_bits
			result = difference
		elif (operator == "*"):
			product = extended_integer1 * extended_integer2
			integer_size = math_int_size1 + math_int_size2
			fraction_size = fractional_bits * 2
			result = product
		elif (operator == "/"):
			if (extended_integer2 == 0):
#				raise ZeroDivisionError("Cannot divide by zero.")			
				self.aux_display_var.set("DIVIDE BY ZERO")
				binary_error = True
				result = 0
				integer_size = 0
				fraction_size = 0
				return result, integer_size, fraction_size, binary_error

			if (self.output_mode.get() == "REAL"):
				integer_size = 0
				fraction_size = 0
				
				input_string1_upscaled = input_string1[:self.integer_size1] + input_string1[self.integer_size1+1:]
				input_string2_upscaled = input_string2[:self.integer_size2] + input_string2[self.integer_size2+1:]
				input_string1_int = int(input_string1_upscaled, 2)
				input_string2_int = int(input_string2_upscaled, 2)
					
				# Sign extend
				if (input_string1[0] == '1'):
					numerator = input_string1_int - (1 << (self.integer_size1 + self.fraction_size1))
				else:
					numerator = input_string1_int

				if (input_string2[0] == '1'):
					denominator = input_string2_int  - (1 << (self.integer_size2 + self.fraction_size2))
				else:					
					denominator = input_string2_int
					
				print(input_string1_upscaled, input_string2_upscaled, input_string1_int, input_string2_int)
				
				print('numerator = ', numerator, 'denominator = ', denominator)
				result = (float(numerator)/2**self.fraction_size1) / (float(denominator)/2**self.fraction_size2)
			else:
				integer_size = max(math_int_size1, math_int_size2)
				fraction_size = self.frac_bits.get()
			
				# Scale the numerator using the default fractional value				
				numerator = Decimal(extended_integer1)
				denominator = Decimal(extended_integer2)
				quotient = numerator / denominator
				result = int(quotient * (2**fraction_size))
				print("Divider math", numerator, denominator, quotient)
		else:
			result = extended_integer1
			integer_size = math_int_size1
			fraction_size = self.fraction_size1

		print('Binary math output = ', result)
		return result, integer_size, fraction_size, binary_error
		 
	def convert_output_binary(self, value, int_size, frac_size):
		if (self.output_mode.get() == "REAL"):
			output_data = value
		elif (self.output_mode.get() == "HEX"):
			output_data = hex(value & ((1 << (int_size + frac_size)) - 1))
		elif (self.output_mode.get() == "BIN"):
			total_bits = int_size + frac_size

			# 3. Apply the two's complement mask
			mask = (1 << total_bits) - 1
			binary_int = value & mask
			print('value = ', value, 'binary_int = ', binary_int)

			# 4. Format as binary string and manually insert the binary point
			if (frac_size > 0):
				binary_str = f"{binary_int:0{total_bits}b}"
				integer_part = binary_str[:-frac_size]
				fraction_part = binary_str[-frac_size:]
				output_data = f"{integer_part}.{fraction_part}"
			else:
				output_data = f"{binary_int:0{total_bits}b}"
		elif (self.output_mode.get() == "FP32"):
			value_float = float(value/2**frac_size)
			packed = struct.pack('>f', value_float)
			output_data = f"0x{struct.unpack('>I', packed)[0]:08X}"
		elif (self.output_mode.get() == "FP64"):
			value_float = float(value/2**frac_size)
			packed = struct.pack('>d', value_float)
			output_data = f"0x{struct.unpack('>Q', packed)[0]:16X}"
		
		print('Binary converter output = ', output_data)
		return output_data
		
	def count_input_bits(self, input_string):
		split_list = ["", ""] 

		if '.' in input_string:
			split_list = input_string.split('.')
		else:
			split_list[0] = input_string
			split_list[1] = ""
		
		int_bit_count = len(split_list[0])
		frac_bit_count = len(split_list[1])
		print('Int bit count = ', int_bit_count, 'frac_bit_count = ', frac_bit_count)
		
		return int_bit_count, frac_bit_count

	def verify_real_input(self, input_string):
		try:
			float(input_string)
			return False
		except ValueError:
			return True
	
	def verify_hex_input(self, input_string):
		try:
			int(input_string, 16)
			
			if (len(input_string) != self.nibble_size):
				return True
			
			return False
		except ValueError:
			return True
	
	def verify_bin_input(self, input_string):
		try:
			int(input_string.replace('.', ''), 2) # Enforces 0s and 1s only
			return ((input_string.count('.') > 1) or ((input_string[0] != '0') and input_string[0] != '1'))
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

	def twos_complement(self, integer_input):
		return (integer_input ^ (-1) + 1)

	def input_mode_changed(self):
		mode = self.input_mode.get()

		if mode == "HEX":
			self.aux_display_var.set("HEX BITS = INTEGER BITS")
		else:
			self.aux_display_var.set("")		