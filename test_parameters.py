from dataclasses import dataclass

@dataclass
class TestCase:
	integer_bits: str
	fraction_bits: str
	input_mode: str
	output_mode: str
	input_string: str
	expected: str
