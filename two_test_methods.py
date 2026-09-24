class TestBench(unittest.TestCase):
    # ... setUpClass and other configurations ...

    def test_matrix_safe_zone_coverage(self):
        """UVM Sequence 1: Full cross-coverage of all 5 paths using safe bit-widths."""
        output_types = ["REAL", "HEX", "BIN", "IEEE754_SINGLE", "IEEE754_DOUBLE"]
        
        # Constrain vectors to fit safely in 23 bits of significance
        safe_vectors = self.generate_constrained_vectors(max_bits=23)
        
        for op1, op2 in safe_vectors:
            for out_type in output_types:
                with self.subTest(op1=op1, op2=op2, target_out=out_type):
                    # Loopback test here -> will be 100% bit-exact across ALL 5 types
                    pass

    def test_matrix_extreme_precision_stress(self):
        """UVM Sequence 2: High-precision stress test bypassing IEEE formats."""
        # Exclude IEEE formats because they physically cannot hold this precision
        high_precision_outputs = ["REAL", "HEX", "BIN"]
        
        # Unleash arbitrarily large test vectors (e.g., 64-bit, 128-bit patterns)
        extreme_vectors = self.generate_extreme_vectors()
        
        for op1, op2 in extreme_vectors:
            for out_type in high_precision_outputs:
                with self.subTest(op1=op1, op2=op2, target_out=out_type):
                    # Loopback test here -> tests extreme bit depths cleanly
                    pass
