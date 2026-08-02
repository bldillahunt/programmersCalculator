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
		self.display_var = tk.StringVar(value="")
		self.input_mode = tk.StringVar(value="REAL")
		self.output_mode = tk.StringVar(value="REAL")
		
		self.int_bits = tk.IntVar(value=16)
		self.frac_bits = tk.IntVar(value=16)
		modes = []
		
		self.create_widgets()

	def create_widgets(self):
		# 1. Main Display
		display_frame = ttk.Frame(self.root, padding=10)
		display_frame.pack(fill="x")
		
		self.display = ttk.Entry(display_frame, textvariable=self.display_var, font=("Courier", 18), justify="right")
		self.display.pack(fill="x", ipady=10)

		# 2. Configuration Panel (Bit Widths)
		config_frame = ttk.LabelFrame(self.root, text=" Fixed-Point Bit Configuration ", padding=10)
		config_frame.pack(fill="x", padx=10, pady=5)
		
		ttk.Label(config_frame, text="Integer Bits:").grid(row=0, column=0, sticky="w")
		ttk.Entry(config_frame, textvariable=self.int_bits, width=5).grid(row=0, column=1, padx=5)
		
		ttk.Label(config_frame, text="Fraction Bits:").grid(row=0, column=2, sticky="w", padx=10)
		ttk.Entry(config_frame, textvariable=self.frac_bits, width=5).grid(row=0, column=3, padx=5)

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
			self.display_var.set("")
		elif char in ('=', 'Enter'):
			operand1, operand2, operator = self.get_float_operands()
			
			result_float = self.calculate_result(operand1, operand2, operator)
			result_requested = self.convert_output_format(result_float)
				
			print(result_requested, result_float)
			self.display_var.set("")
			self.display_var.set(result_requested)
		else:
			current = self.display_var.get()
			self.display_var.set(current + str(char))

	def get_float_operands(self):
		raw_input = self.display_var.get()
		operand1, operator, operand2 = self.parse_input_string(raw_input)

		if (self.input_mode.get() == "BIN"):
			operand1_float = binary_to_fixed_point(operand1, self.int_bits.get(), self.frac_bits.get())
		elif (self.input_mode.get() == "FP32"):
			operand1_float = ieee754_hex_to_float(operand1, False)
		else:
			print('Unknown data format for operand 1')

		if operator is not None:			
			if (self.input_mode.get() == "BIN"):
				operand2_float = binary_to_fixed_point(operand2, self.int_bits.get(), self.frac_bits.get())
			elif (self.input_mode.get() == "FP32"):
				operand2_float = ieee754_hex_to_float(operand2, False)
			else:
				print('Unknown data format for operand 2')
		else:
			operand2_float = None
			
		return operand1_float, operand2_float, operator
		
	def calculate_result(self, operand1, operand2, operator):
		# TODO: Implement expression splitting (val1, op, val2) 
		# and conversions based on self.input_mode / self.output_mode
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
#		pattern = r"\s*(\S+)\s*([+\-*/])\s*(\S+)\s*"
#		pattern = r"\s*(\S+)(?:\s*([+\-*/])\s*(\S+))?\s*"
		pattern = r"\s*((?:(?![+\-*/])\S)+)(?:\s*([+\-*/])\s*(\S+))?\s*"
		left, op, right = re.match(pattern, input_string).groups()
#        print(left, op, right)
		return left, op, right
		
	def convert_output_format(self, input_float):
		print(input_float)
		
		if (self.output_mode.get() == "BIN"):
			output_data = fixed_point_to_binary(input_float, self.int_bits.get(), self.frac_bits.get())
		elif (self.output_mode.get() == "FP32"):
			output_data = float_to_ieee754_hex(input_float, False)
		elif (self.output_mode.get() == "REAL"):
			output_data = input_float
		else:
			print('Unknown data format for output')
		
		return output_data
		