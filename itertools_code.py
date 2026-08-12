import unittest
import itertools

# Your existing calculator code here...

class TestCalculatorMatrix(unittest.TestCase):

    def test_all_125_permutations(self):
        input_types = ["int", "float", "hex", "bin", "fixed"]
        output_types = ["int", "float", "hex", "bin", "fixed"]
        operations = ["add", "sub", "mul", "div", "shift"]

        # Generate the 125 paths
        matrix = itertools.product(input_types, output_types, operations)

        for in_type, out_type, op in matrix:
            # subTest ensures that if path #14 fails, paths 15-125 still run!
            with self.subTest(in_type=in_type, out_type=out_type, op=op):
                
                # Replace this with your actual calculator call
                # result = my_calc(in_type, out_type, op)
                
                # Example assertion
                self.assertTrue(True) 

if __name__ == '__main__':
    unittest.main()
