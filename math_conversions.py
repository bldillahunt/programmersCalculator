import struct
from decimal import Decimal
import time
from fixedpoint import FixedPoint
import math
import numpy as np

def real_to_ieee754 (n, precision):
	if (precision == "SINGLE"):
		exponent_size = 7
		mantissa_size = 23
		exp_bias = 127
		exp_mask = 0x7F
		mantissa_mask = 0x7FFFFF
		exp_nibble_size = 2
		mantissa_nibble_size = 6
	elif (precision == "DOUBLE"):
		exponent_size = 11
		mantissa_size = 52
		exp_bias = 1023
		exp_mask = 0x7FF
		mantissa_mask = 0x3FFFFFFFFFFFFF
		exp_nibble_size = 3
		mantissa_nibble_size = 14
	else
		return "ERROR"

	min_exp = 0
	max_exp = 2**exponent_size - 1
	min_mant = 0 
	max_mant = 2**mantissa_size - 1
	
	if (n < 0):
		sign_bit = "1"
	else:
		sign_bit = "0"
	
	if (abs(n) == 0):
		float_output_hex = f"{(1+exponent_size+mantissa_size)*'0'}"
	else:
		exponent = math.floor(math.log2(abs(n)))
		mantissa = ((n/2**exponent) - 1) * 2**mantissa_size
		exponent_biased = exponent + exp_bias
		exponent_masked = exponent_biased & mask
		
		if (exponent_masked >= min_exp) and (exponent_masked =< max_exp):
			exponent_hex = f"{exponent_masked:0{exp_nibble_size}X}"
		else:
			return "ERROR"
		
		mantissa_masked = mantissa & mantissa_mask

		if (mantissa_masked >= min_mant) and (mantissa_masked <= max_mant):
			mantissa_hex = f"{mantissa_masked:0{mantissa_nibble_size}X}"
		else:
			return "ERROR"

	float_output_hex = f"{sign_bit}{exponent_hex[1:]}{mantissa_hex}"
	return float_output_hex

float_input = input("Enter floating point number: ")
precision_input = input("Select SINGLE or DOUBLE: ")

hex_output = real_to_ieee754(float_input, precision_output)
print(hex_output)

			