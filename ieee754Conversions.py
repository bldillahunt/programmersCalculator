import struct

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




