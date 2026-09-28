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

#			if ('.' in operand1) or ('.' in operand2):
#				operand1_no_bin_point, operand2_no_bin_point, op1_radix_index, op2_radix_index, fraction_size = binary_point_removal(operand1, operand2)
#			else:
#				operand1_no_bin_point = operand1
#				operand2_no_bin_point = operand2
#				fraction_size = 0
		operand1_no_bin_point, operand2_no_bin_point, operand1_fraction_size, operand2_fraction_size = binary_point_alignment(operand1, operand2, False)

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

		quotient = binary_division(operand1_2s_comp, operand2_2s_comp, max_size)

		if (self.enable_print_statements == True):
			print("No binary points = ", list_to_string(operand1_no_bin_point), list_to_string(operand2_no_bin_point))
			print("quotient raw = ", "".join(map(str, quotient)))
			print("Inputs = ", list_to_string(operand1_bin_point), list_to_string(operand2_bin_point))

		if ((sign_operand1 ^ sign_operand2) == 1):
#				quotient_no_bin_point, null_output, quotient_radix_index, null_radix_index, fraction_size = binary_point_removal(quotient, [''])
			quotient_size = len(quotient)

			if ('.' in quotient):
				quotient_radix_index = quotient.index('.')
				quotient.pop(quotient_radix_index)
			else:
				quotient_radix_index = quotient_size

			if (quotient_radix_index < quotient_size):
				quotient_fraction_size = quotient_size - (quotient_radix_index + 1)
			else:
				quotient_fraction_size = 0

			quotient_no_bin_point = quotient
			quotient_2s_comp, carry_quotient = twos_complement(quotient_no_bin_point)

#				if (sign_operand1 == 1):
#					quotient_2s_comp_bin_point = quotient_2s_comp[:quotient_size - quotient_fraction_size + 1] + ['.'] + quotient_2s_comp[quotient_size - quotient_fraction_size + 1:]
#				elif (sign_operand2 == 1):
#					quotient_2s_comp_bin_point = quotient_2s_comp[:quotient_size - quotient_fraction_size - 2] + ['.'] + quotient_2s_comp[quotient_size - quotient_fraction_size - 2:]
#				else:
			quotient_2s_comp_bin_point = quotient_2s_comp[:quotient_size - quotient_fraction_size - 1] + ['.'] + quotient_2s_comp[quotient_size - quotient_fraction_size - 1:]

			if False:
				if (self.int_bits.get() > quotient_radix_index):
					quotient_extended = [0]*(self.int_bits.get() - quotient_radix_index) + quotient_no_bin_point
					quotient_2s_comp, carry_quotient = twos_complement(quotient_extended)
					quotient_2s_comp_bin_point = quotient_2s_comp[:self.int_bits.get()] + ['.'] + quotient_2s_comp[self.int_bits.get():]
				else:
					quotient_extended = quotient_no_bin_point
					quotient_2s_comp, carry_quotient = twos_complement(quotient_extended)
					quotient_2s_comp_bin_point = quotient_2s_comp[:quotient_radix_index] + ['.'] + quotient_2s_comp[quotient_radix_index:]

#				print("quotient 2s comp = ", "".join(map(str, quotient_2s_comp_bin_point)))

			if (self.enable_print_statements == True):
				print(quotient_radix_index, list_to_string(quotient), list_to_string(quotient_no_bin_point), list_to_string(quotient_2s_comp_bin_point))

			math_result_2s_comp = quotient_2s_comp_bin_point
		else:
			math_result_2s_comp = quotient

#			print("quotient = ", "".join(map(str, math_result_2s_comp)))

		math_result = math_result_2s_comp
	elif (operator == "*"):
		math_result = binary_multiplier(operand1, operand2)
	elif (operator == "+"):
		addend_a, addend_b, operand1_fraction_size, operand2_fraction_size = binary_point_alignment(operand1, operand2, False)

		if (operand1_fraction_size > operand2_fraction_size):
			fraction_size = operand1_fraction_size
		else:
			fraction_size = operand2_fraction_size

		n_sum, n_carry = binary_adder(addend_a, addend_b)

		if ((operand1[0] == 0) and (operand2[0] == 0) and (n_sum[0] == 1)) or ((operand1[0] == 1) and (operand2[0] == 1) and (n_sum[0] == 0)):
			sum_result = [n_carry] + n_sum
		else:
			sum_result = n_sum

		binary_point_index = len(sum_result) - fraction_size

		if (self.enable_print_statements == True):
			print(list_to_string(addend_a), list_to_string(addend_b), operand1_fraction_size, operand2_fraction_size)
			print(list_to_string(n_sum), n_carry, list_to_string(sum_result), binary_point_index)

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
