from alu import ALU
from src.asm.isa import *


class DataPath:
    memory = []
    alu = ALU()

    def __init__(self):
        self.memory = [] * MAX_ADDRESS + 1
        self.acc = 0  # Accumulator
        self.ar = 0  # Address Register
        self.ip = 0  # Instruction Pointer
        self.dr = 0  # Data Register
        self.sp = 0  # Stack Pointer
        self.cr = 0  # Command Register
        self.ps = 0  # Program Status

    def fetch_instruction(self):
        """
        Fetch the instruction from memory
        """
        self.ar = self.ip
        self.dr = self.memory[self.ar]
        self.cr = self.dr  # Command Register will hold the instruction
        self.ip += 1

    def read_operand(self):
        """
        Read the operand from memory
        """
        self.dr = self.memory[self.ar]
