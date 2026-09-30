import tkinter as tk
from tkinter import ttk
import struct
import time
import math
import numpy as np
from dataclasses import dataclass
from typing import List, Literal
from binary_support import precision_profile, lookup_table, twos_complement, binary_string_to_int_list, int_list_to_binary_string, binary_point_removal, twos_complement_bin_rational, list_to_string, remove_msbs, binary_point_alignment
from binary_conversions import real_to_twos_comp_binary, hexadecimal_to_binary, ieee754_hex_to_binary, binary_to_real, binary_to_hexadecimal, binary_to_ieee754
from binary_math import binary_division, binary_multiplier, binary_adder, binary_subtraction, binary_modulo, binary_twos_complement
from binary_logic import binary_and, binary_or, binary_xor, binary_not
from calculator_top import compute_evaluation_step

class FpgaCalculator:
	def __init__(self, root):
		self.enable_print_statements = False

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
			main_display_value, calculator_result = compute_evaluation_step(self.main_display_var.get(), self.input_mode.get(), self.output_mode.get(), self.int_bits.get(), self.frac_bits.get(), enable_print_statements=False)
			self.main_display_var.set(main_display_value)
			self.aux_display_var.set(calculator_result)
		else:
			current = self.main_display_var.get()
			self.main_display_var.set(current + str(char))
	
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
