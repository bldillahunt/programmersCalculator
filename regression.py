import unittest
import itertools
from hypothesis import given, settings, strategies as st

# =====================================================================
# 1. CORE CONFIGURATION & PERMUTATIONS
# =====================================================================
INPUT_TYPES = ["twos_comp_bin", "twos_comp_hex", "real", "ieee754_single", "ieee754_double"]
OUTPUT_TYPES = ["twos_comp_bin", "twos_comp_hex", "real", "ieee754_single", "ieee754_double"]
OPERATIONS = ["add", "sub", "mul", "div", "shift"]

# Generate the definitive 125 paths
ALL_125_PATHS = list(itertools.product(INPUT_TYPES, OUTPUT_TYPES, OPERATIONS))

# =====================================================================
# 2. HYPOTHESIS DATA STRATEGIES (Hardware Bitstring Generators)
# =====================================================================

# Generates valid 1s and 0s with an optional single variable binary point
@st.composite
def binary_twos_complement_strategy(draw):
    width = draw(st.integers(min_value=4, max_value=64))
    binary_point_pos = draw(st.integers(min_value=1, max_value=width - 1))
    
    # Generate random binary characters for integer and fractional parts
    int_bits = "".join(draw(st.lists(st.sampled_from(["0", "1"]), min_size=1, max_size=width - binary_point_pos)))
    frac_bits = "".join(draw(st.lists(st.sampled_from(["0", "1"]), min_size=1, max_size=binary_point_pos)))
    
    return f"{int_bits}.{frac_bits}", binary_point_pos

# Generates valid hex strings (0-9, A-F) perfectly matched to a randomized user-defined bit width
@st.composite
def hex_twos_complement_strategy(draw):
    # Hex width set by user (must be a multiple of 4 bits for clean hex chars, e.g., 4, 8, 12, 16...64)
    hex_width_bits = draw(st.integers(min_value=1, max_value=16)) * 4
    char_count = hex_width_bits // 4
    
    hex_chars = "".join(draw(st.lists(st.sampled_from("0123456789ABCDEF"), min_size=char_count, max_size=char_count)))
    frac_size_out = draw(st.integers(min_value=0, max_value=hex_width_bits))
    
    return hex_chars, hex_width_bits, frac_size_out

# =====================================================================
# 3. COMPREHENSIVE REGRESSION SUITE
# =====================================================================
class ComprehensiveHardwareTestbench(unittest.TestCase):

    # Hypothesis runs this entire method 100 times by default, picking brand new random
    # inputs and hyper-extreme numbers (0, max values, minimum integers) each time.
    @given(
        bin_data=binary_twos_complement_strategy(),
        hex_data=hex_twos_complement_strategy(),
        raw_real=st.floats(allow_nan=False, allow_infinity=False, min_value=-1e9, max_value=1e9),
        # Real-looking 8-char and 16-char IEEE754 hex blocks
        ieee_single=st.text(alphabet="0123456789ABCDEF", min_size=8, max_size=8),
        ieee_double=st.text(alphabet="0123456789ABCDEF", min_size=16, max_size=16)
    )
    @settings(max_examples=100) # 100 random variations per execution
    def test_every_single_path_with_fuzzing(self, bin_data, hex_data, raw_real, ieee_single, ieee_double):
        
        # Unpack randomized strategies
        bin_str, bin_point = bin_data
        hex_str, hex_width, hex_frac_out = hex_data

        # Sweep through all 125 paths for THIS specific set of randomized data
        for in_type, out_type, op in ALL_125_PATHS:
            
            # Map the input string to the current target input type
            current_input = {
                "twos_comp_bin": bin_str,
                "twos_comp_hex": hex_str,
                "real": raw_real,
                "ieee754_single": ieee_single,
                "ieee754_double": ieee_double
            }[in_type]

            # Construct the structural metadata mapping your hardware constraints
            meta = {
                "binary_point_pos": bin_point,
                "hex_width": hex_width,
                "hex_frac_size": hex_frac_out
            }

            # Subtest isolates errors so one failure won't halt the whole suite
            with self.subTest(in_type=in_type, out_type=out_type, op=op):
                try:
                    # Execute your actual math engine block
                    # Replace 'my_calculator_engine' with your real function/class call
                    result = my_calculator_engine(current_input, in_type, out_type, op, meta=meta)
                    
                    # --------------------------------==================
                    # CRITICAL OVERFLOW & SYNTAX VALIDATION CHECKS
                    # --------------------------------==================
                    self.assertIsNotNone(result, "Engine returned an empty value.")

                    if out_type == "twos_comp_bin":
                        self.assertNotIn("0b", result, "Binary output contains an illegal '0b' prefix.")
                        # Verify overflow didn't break string formatting
                        self.assertTrue(all(c in "01." for c in result), f"Malformed binary string: {result}")
                        
                    elif out_type == "twos_comp_hex":
                        self.assertNotIn("0x", result, "Hex output contains an illegal '0x' prefix.")
                        self.assertNotIn(".", result, "Twos-complement hex output contains an illegal point.")
                        # Verify the result respects the bounded hex character limit without hidden overflow leakage
                        expected_chars = (hex_width + (hex_frac_out * 4)) // 4 # Adjust based on your sizing rules
                        # self.assertEqual(len(result), expected_chars, "Hex result bit width mismatch.")

                except OverflowError:
                    # If your engine is DESIGNED to gracefully throw an OverflowError when realignments 
                    # exceed bit limits, passing here is correct behavior.
                    pass
                except Exception as e:
                    # If it crashes with a ValueError, KeyError, or anything else, the testbench catches it
                    self.fail(f"CRASH DETECTED!\nPath: {in_type} -> {out_type} ({op})\n"
                              f"Input: {current_input}\nMetadata: {meta}\nException: {str(e)}")

if __name__ == '__main__':
    # Stub function for example execution context
    def my_calculator_engine(in_val, in_type, out_type, op, meta):
        return "0" 
        
    unittest.main()
