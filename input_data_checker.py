from dataclasses import dataclass
from typing import Optional
import re

# =====================================================================
# 1. DATA STRUCTURES (Your Hardware-Style "Structs")
# =====================================================================

@dataclass
class ValidationRecord:
    """Universal structural template for standard inputs."""
    is_valid: bool
    cleaned_string: str
    error_message: Optional[str] = None

@dataclass
class BinaryFixedPointRecord(ValidationRecord):
    """Specialized structural template for fixed-point hardware tracking."""
    bit_width: int = 0
    fraction_width: int = 0


# =====================================================================
# 2. VALIDATION ENGINE (Pure Logic, No UI Side-Effects)
# =====================================================================

def check_fpga_input(user_input: str, expected_type: str):
    """
    Verifies if characters match the expected FPGA data type constraints.
    Returns a ValidationRecord or BinaryFixedPointRecord tracking data specs.
    """
    # Clear leading/trailing whitespace
    s = user_input.strip()
    
    # -----------------------------------------------------------------
    # TYPE 1: REAL (Decimal floating points)
    # -----------------------------------------------------------------
    if expected_type == "real":
        try:
            float(s)
            return ValidationRecord(is_valid=True, cleaned_string=s)
        except ValueError:
            return ValidationRecord(
                is_valid=False, 
                cleaned_string=s, 
                error_message="Not a valid real/decimal number."
            )

    # -----------------------------------------------------------------
    # TYPE 2: HEX (Pure hexadecimal, no prefixes allowed)
    # -----------------------------------------------------------------
    elif expected_type == "hex":
        try:
            int(s, 16)
            return ValidationRecord(is_valid=True, cleaned_string=s)
        except ValueError:
            return ValidationRecord(
                is_valid=False, 
                cleaned_string=s, 
                error_message="Not a valid hexadecimal value."
            )

    # -----------------------------------------------------------------
    # TYPE 3: TWO'S COMPLEMENT BINARY WITH OPTIONAL POINT
    # -----------------------------------------------------------------
    elif expected_type == "twos-complement-binary-point":
        # Match only 0s, 1s, and a maximum of one single decimal point
        if not re.match(r"^[01]+(\.[01]+)?$", s):
            return BinaryFixedPointRecord(
                is_valid=False, 
                cleaned_string=s, 
                error_message="Binary must only contain 0, 1, or a single embedded '.'"
            )
        
        # Extrapolate bus size and radix fraction placement parameters
        if "." in s:
            integer_part, fractional_part = s.split(".")
            bit_width = len(integer_part) + len(fractional_part)
            fraction_width = len(fractional_part)
        else:
            bit_width = len(s)
            fraction_width = 0
            
        return BinaryFixedPointRecord(
            is_valid=True, 
            cleaned_string=s, 
            bit_width=bit_width, 
            fraction_width=fraction_width
        )

    # -----------------------------------------------------------------
    # TYPE 4: IEEE754 SINGLE (Strictly 32-bit width hex representation)
    # -----------------------------------------------------------------
    elif expected_type == "ieee754-single":
        try:
            int(s, 16)
            if len(s) == 8:
                return ValidationRecord(is_valid=True, cleaned_string=s)
            return ValidationRecord(
                is_valid=False, 
                cleaned_string=s, 
                error_message=f"IEEE754 Single requires exactly 8 hex characters (32-bit bus). Got {len(s)}."
            )
        except ValueError:
            return ValidationRecord(
                is_valid=False, 
                cleaned_string=s, 
                error_message="Invalid characters for an IEEE754 Single field."
            )

    # -----------------------------------------------------------------
    # TYPE 5: IEEE754 DOUBLE (Strictly 64-bit width hex representation)
    # -----------------------------------------------------------------
    elif expected_type == "ieee754-double":
        try:
            int(s, 16)
            if len(s) == 16:
                return ValidationRecord(is_valid=True, cleaned_string=s)
            return ValidationRecord(
                is_valid=False, 
                cleaned_string=s, 
                error_message=f"IEEE754 Double requires exactly 16 hex characters (64-bit bus). Got {len(s)}."
            )
        except ValueError:
            return ValidationRecord(
                is_valid=False, 
                cleaned_string=s, 
                error_message="Invalid characters for an IEEE754 Double field."
            )

    # Safety trap for undefined types
    return ValidationRecord(
        is_valid=False, 
        cleaned_string=s, 
        error_message="Requested data verification type is unknown."
    )
