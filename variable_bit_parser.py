binary_str = "101.11"  # Your isolated first operand from the regex

# 1. Look for the binary point and split the sections
if '.' in binary_str:
    int_part, frac_part = binary_str.split('.')
else:
    int_part = binary_str
    frac_part = ""  # No fractional bits if there's no binary point

# 2. Count the number of bits on either side
int_bit_count = len(int_part)
frac_bit_count = len(frac_part)

print(f"Integer section: '{int_part}' ({int_bit_count} bits)")
print(f"Fractional section: '{frac_part}' ({frac_bit_count} bits)")
