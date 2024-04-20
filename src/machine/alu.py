from src.asm.isa import *


class ALU:

    def __init__(self):
        self.N = False  # Negative Flag
        self.Z = True  # Zero Flag
        self.C = False  # Carry Flag

    def set_flags(self, result):
        if result < MIN_VALUE or result > MAX_VALUE:
            self.C = True  # Set carry flag
            result = result % (MAX_VALUE + 1)
        else:
            self.C = False
        self.N = result < 0
        self.Z = result == 0

    def add(self, a, b):
        result = a + b
        self.set_flags(result)
        return result

    def sub(self, a, b):
        return self.add(a, -b)

    def cmp(self, a, b):
        result = self.sub(a, b)
        return result

    def shl(self, a):
        self.C = bool(a & (1 << (SYS_BITS - 1)))  # Save the leftmost bit to Carry flag
        result = (a << 1) & ((1 << SYS_BITS) - 1)  # Shift left and mask to keep within SYS_BITS
        self.set_flags(result)
        return result

    def shr(self, a):
        self.C = bool(a & 1)  # Save the rightmost bit to Carry flag
        result = a >> 1
        self.set_flags(result)
        return result


