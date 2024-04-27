from isa import MAX_VALUE, MIN_VALUE, SYS_BITS


class ALU:
    """
    Arithmetic Logic Unit

    Attributes:
    N: Negative Flag
    Z: Zero Flag
    C: Carry Flag
    """

    def __init__(self):
        self.N = False  # Negative Flag
        self.Z = True  # Zero Flag
        self.C = False  # Carry Flag

    def set_flags(self, result):
        if isinstance(result, str):
            value = ord(result)
        else:
            value = result
        if value < MIN_VALUE or value > MAX_VALUE:
            self.C = True  # Set carry flag
            value = value % (MAX_VALUE + 1)
        else:
            self.C = False
        self.N = value < 0
        self.Z = value == 0

    def get_flags_as_int(self):
        """
        Convert the N, Z, and C flags to a single integer.
        """
        return (int(self.N) << 2) | (int(self.Z) << 1) | int(self.C)

    def add(self, a, b):
        result = a + b
        self.set_flags(result)
        return result

    def sub(self, a, b):
        return self.add(a, -b)

    def cmp(self, a, b):
        return self.sub(a, b)

    def shl(self, a):
        result = (a << 1) & ((1 << SYS_BITS) - 1)  # Shift left and mask to keep within SYS_BITS
        self.set_flags(result)
        self.C = bool(a & (1 << (SYS_BITS - 1)))  # Save the leftmost bit to Carry flag
        return result

    def shr(self, a):
        result = a >> 1
        self.set_flags(result)
        self.C = bool(a & 1)  # Save the rightmost bit to Carry flag
        return result

    def clr(self):
        self.N = False
        self.Z = True
        self.C = False
        return 0
