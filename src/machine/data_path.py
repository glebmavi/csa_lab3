from alu import ALU
from src.asm.isa import *


class DataPath:
    memory = []
    alu = ALU()
    registers = {}  # TODO

    def __init__(self):
        self.memory = [0] * MAX_ADDRESS
        ...


