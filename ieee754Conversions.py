import struct
import math

def float_to_ieee754_hex(val: float, double_precision=False) -> str:
    """Converts a standard Python float into an IEEE-754 Hex string."""
    if double_precision:
        return f"{struct.unpack('<Q', struct.pack('<d', val))[0]:016X}"
    return f"{struct.unpack('<I', struct.pack('<f', val))[0]:08X}"

def ieee754_hex_to_float(hex_str: str, double_precision=False) -> float:
    """Converts an IEEE-754 Hex string back into a Python float."""
    val = int(hex_str, 16)
    if double_precision:
        return struct.unpack('<d', struct.pack('<Q', val))[0]
    return struct.unpack('<f', struct.pack('<I', val))[0]

def safe_float_to_fixed_point(float_val, fraction_size):
	"""
	Safely converts any fp64 value to a fixed-point integer without 
	ever triggering an 'inf' overflow during the scaling process.
	"""
	# 1. Separate the float into fraction and integer components
	# math.modf(12.375) -> (0.375, 12.0)
	# Both outputs remain floats, but the integer part is isolated
	float_fraction, float_integer = math.modf(float_val)

	print('float_fraction = ', float_fraction, 'float_integer = ', float_integer)

	# 2. Convert the integer component safely to a giant Python int
	# Python ints have arbitrary precision and will NEVER hit 'inf'
	pure_int_component = int(float_integer)

	print('pure_int_component = ', pure_int_component)

	# 3. Scale the isolated integer component safely using a bit-shift
	scaled_integer_part = pure_int_component << fraction_size

	print('scaled_integer_part = ', scaled_integer_part)

	# 4. Scale the fractional component while it is small
	# Because float_fraction is always < 1.0, this will never overflow
	scaled_fraction_part = math.floor(float_fraction * (2 ** fraction_size))

	print('scaled_fraction_part = ', scaled_fraction_part)

	# 5. Recombine them safely using pure integer addition
	final_fixed_point = scaled_integer_part + scaled_fraction_part

	return final_fixed_point, pure_int_component
		


