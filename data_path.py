from __future__ import annotations

from alu import ALU
from errors import AddressRegisterError, InstructionPointerError
from isa import MAX_ADDRESS, STACK_START, OpCode
from translator import Instruction


class DataPath:
    def __init__(self):
        self.alu = ALU()
        self.memory = [Instruction(i, OpCode.NOP, 0) for i in range(MAX_ADDRESS + 1)]
        self.acc: int | str = 0  # Accumulator
        self.ar: int = 0  # Address Register
        self.ip: int = 0  # Instruction Pointer
        self.dr: int | Instruction = 0  # Data Register
        self.sp: int = STACK_START  # Stack Pointer
        self.cr: Instruction = Instruction(0, OpCode.NOP, 0)  # Command Register
        self.ps: int = self.alu.get_flags_as_int()  # Program Status
        self.output = []  # Used only as a way to capture output for testing

    def __str__(self):
        return (
            f"ACC: {self.acc:10} |" f"AR: {self.ar:5} |" f"IP: {self.ip:5} |" f"DR: {self.dr}".ljust(120)
            + " |"
            f"SP: {self.sp:5} |"
            f"CR: OpCode: {self.cr.opcode:4}, Value: {self.cr.value:10}, "
            f"Relative: {self.cr.relative}".ljust(70)
            + " |"
            f"PS: {self.ps:2}"
        )

    def fetch_instruction(self):
        """
        Fetch the instruction from memory
        """
        self.ar = self.ip
        try:
            self.dr = self.memory[self.ar]
        except IndexError:
            raise InstructionPointerError(self.ip)
        self.cr = self.dr  # Command Register will hold the instruction
        self.ip += 1

    def read_operand(self):
        """
        Read the operand from memory
        """
        self.dr = self.cr.value
        self.ar = self.dr
        try:
            self.dr = self.memory[self.ar]
        except IndexError:
            raise AddressRegisterError(self.ar)
        if self.cr.relative:
            try:
                self.dr = self.memory[self.dr.value]
            except IndexError:
                raise AddressRegisterError(self.dr.value)
