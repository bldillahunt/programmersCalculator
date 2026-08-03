import tkinter as tk
from tkinter import ttk
import re
from binaryConversions import binary_to_fixed_point
from binaryConversions import fixed_point_to_binary
from ieee754Conversions import ieee754_hex_to_float
from ieee754Conversions import float_to_ieee754_hex

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
		
#		self.int_bits = tk.IntVar(value=16)
#		self.frac_bits = tk.IntVar(value=16)
		
		self.integer_size1 = 0
		self.fraction_size1 = 0
		self.integer_size2 = 0
		self.fraction_size2 = 0
		
		# Place holders that will eventually get calculated
		self.integer_size_out = 16
		self.fraction_size_out = 16
		
		self.create_widgets()

	def create_widgets(self):
		# 1. Main Display
		main_display_frame = ttk.Frame(self.root, padding=10)
		main_display_frame.pack(fill="x")
		
		self.main_display = ttk.Entry(main_display_frame, textvariable=self.main_display_var, font=("Courier", 12), justify="right")
		self.main_display.pack(fill="x", ipady=10)

		# 2. Configuration Panel (Bit Widths)
#		config_frame = ttk.LabelFrame(self.root, text=" Fixed-Point Bit Configuration ", padding=10)
#		config_frame.pack(fill="x", padx=10, pady=5)
		
#		ttk.Label(config_frame, text="Integer Bits:").grid(row=0, column=0, sticky="w")
#		ttk.Entry(config_frame, textvariable=self.int_bits, width=5).grid(row=0, column=1, padx=5)
		
#		ttk.Label(config_frame, text="Fraction Bits:").grid(row=0, column=2, sticky="w", padx=10)
#		ttk.Entry(config_frame, textvariable=self.frac_bits, width=5).grid(row=0, column=3, padx=5)

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
			ttk.Radiobutton(in_lbl, text=text, variable=self.input_mode, value=mode).pack(anchor="w")
			
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
		elif char in ('=', 'Enter'):
			operand1, operand2, operator = self.get_operands()
			operand1_data_error = False
			operand2_data_error = False
			operand_error = False
			
			# Error checking
			if (self.input_mode.get() == "REAL"):
				operand1_data_error = self.verify_real_input(operand1)
				
				if (operand2 != ""):
					operand2_data_error = self.verify_real_input(operand2)
			elif (self.input_mode.get() == "HEX"):
				operand1_data_error = self.verify_hex_input(operand1)
				
				if (operand2 != ""):
					operand2_data_error = self.verify_hex_input(operand2)
			elif (self.input_mode.get() == "BIN"):
				operand1_data_error = self.verify_bin_input(operand1)
				
				if (operand2 != ""):
					operand2_data_error = self.verify_bin_input(operand2)
			elif (self.input_mode.get() == "FP32"):
				operand1_data_error = self.verify_fp32_input(operand1)
				
				if (operand2 != ""):
					operand2_data_error = self.verify_fp64_input(operand2)
			elif (self.input_mode.get() == "FP64"):
				operand1_data_error = self.verify_fp64_input(operand1)
				
				if (operand2 != ""):
					operand2_data_error = self.verify_fp64_input(operand2)

			operator_error = self.verify_operator(operator)
			
			if (operand1_data_error == False) and (operand2_data_error == False) and (operator_error == False):
				if (self.input_mode.get() == "BIN"):
					self.integer_size1, self.fraction_size1 = self.count_input_bits(operand1)

					if (operand2 != ""):
						self.integer_size2, self.fraction_size2 = self.count_input_bits(operand2)

				operand1_float, operand2_float = self.get_float_operands(operand1, operand2, operator)	
				result_float = self.calculate_result(operand1_float, operand2_float, operator)
				result_requested = self.convert_output_format(result_float)

				print(result_requested, result_float)
				self.main_display_var.set("")
				self.main_display_var.set(result_requested)
				self.aux_display_var.set(result_float)
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

	def get_float_operands(self, operand1, operand2, operator):
		if (self.input_mode.get() == "BIN"):
			operand1_float = binary_to_fixed_point(operand1, self.integer_size1, self.fraction_size1)
		elif (self.input_mode.get() == "FP32"):
			operand1_float = ieee754_hex_to_float(operand1, False)
		elif (self.input_mode.get() == "REAL"):
			operand1_float = float(operand1)
		else:
			print('Unknown data format for operand 1')

		if operator != "":			
			if (self.input_mode.get() == "BIN"):
				operand2_float = binary_to_fixed_point(operand2, self.integer_size2, self.fraction_size2)
			elif (self.input_mode.get() == "FP32"):
				operand2_float = ieee754_hex_to_float(operand2, False)
			else:
				print('Unknown data format for operand 2')
		else:
			operand2_float = 0
			
		return operand1_float, operand2_float
		
	def calculate_result(self, operand1, operand2, operator):
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
		state = 'First_Character'
		data_length = len(input_string)
		input_index = 0
		left = ""
		op = ""
		right = ""
		print(input_string)
		print(left, op, right, data_length)
		
		while (True):
			match state:
				case 'First_Character':
					print('First Character')

					if (input_string[input_index] == '+'):
						state = 'First_Operand'
						print(state, input_index)
					elif (input_string[input_index] == '-') or (input_string[input_index].isalnum()):
						left += input_string[input_index]
						input_index = input_index + 1
						state = 'First_Operand'
						print(state, input_index)
					else:
						print(state, input_index, left)
						return left, op, right
				case 'First_Operand':
					while input_string[input_index] not in ("+", "-", "*", "/", ""):
						print(state, input_index, left)
						left += input_string[input_index]

						if (input_index < data_length-1):
							input_index = input_index + 1
						else:
							print(left, op, right)
							return left, op, right
					else:
						op = input_string[input_index]
						input_index = input_index + 1

					if input_string[input_index] not in (""):
						state = 'Second_Operand'
					else:
						print(left, op, right)
						return left, op, right
				case 'Second_Operand':
					while input_string[input_index] not in (""):
						print(state, input_index, right)
						right += input_string[input_index]
						
						if (input_index < data_length-1):
							input_index = input_index + 1
						else:
							return left, op, right

					return left, op, right
		
	def convert_output_format(self, input_float):
		print(input_float)
		
		if (self.output_mode.get() == "BIN"):
			output_data = fixed_point_to_binary(input_float, self.integer_size_out, self.fraction_size_out)
		elif (self.output_mode.get() == "FP32"):
			output_data = float_to_ieee754_hex(input_float, False)
		elif (self.output_mode.get() == "REAL"):
			output_data = input_float
		else:
			print('Unknown data format for output')
		
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
		return False
	
	def verify_bin_input(self, input_string):
		return False
	
	def verify_fp32_input(self, input_string):
		return False
	
	def verify_fp64_input(self, input_string):
		return False

	def verify_operator(self, input_string):
		return False