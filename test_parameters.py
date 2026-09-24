from dataclasses import dataclass

@dataclass
class BinaryTestConfiguration:
	integer_bits: str
	fraction_bits: str
	input_mode: str
	output_mode: str
	input_string: str
	expected: str
