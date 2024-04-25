from src.asm.isa import *


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

    def __set_flags(self, result):
        if result < MIN_VALUE or result > MAX_VALUE:
            self.C = True  # Set carry flag
            result = result % (MAX_VALUE + 1)
        else:
            self.C = False
        self.N = result < 0
        self.Z = result == 0

    def get_flags_as_int(self, acc):
        """
        Convert the N, Z, and C flags to a single integer.
        """
        if isinstance(acc, str):
            value = ord(acc)
        else:
            value = acc
        self.__set_flags(value)
        return (int(self.N) << 2) | (int(self.Z) << 1) | int(self.C)

    def add(self, a, b):
        result = a + b
        self.__set_flags(result)
        return result

    def sub(self, a, b):
        return self.add(a, -b)

    def cmp(self, a, b):
        result = self.sub(a, b)
        return result

    def shl(self, a):
        self.C = bool(a & (1 << (SYS_BITS - 1)))  # Save the leftmost bit to Carry flag
        result = (a << 1) & ((1 << SYS_BITS) - 1)  # Shift left and mask to keep within SYS_BITS
        self.__set_flags(result)
        return result

    def shr(self, a):
        self.C = bool(a & 1)  # Save the rightmost bit to Carry flag
        result = a >> 1
        self.__set_flags(result)
        return result

    def clr(self):
        self.N = False
        self.Z = True
        self.C = False
        return 0
