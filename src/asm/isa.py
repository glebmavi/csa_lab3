from enum import Enum
from typing import NamedTuple

# Constants:
SYS_BITS = 32
ADDRESS_RANGE = 11
VALUE_RANGE = SYS_BITS - 1
MAX_ADDRESS = 1 << ADDRESS_RANGE
MAX_VALUE = 1 << VALUE_RANGE


class CommandTypes(Enum):
    DATA = "data"
    JUMP = "jump"
    NOP = "nop"


class OperationInfo(NamedTuple):
    opcode: str
    command_type: CommandTypes


class OpCode(OperationInfo, Enum):
    LOAD = OperationInfo("load", CommandTypes.DATA)
    SAVE = OperationInfo("save", CommandTypes.DATA)
    PUSH = OperationInfo("push", CommandTypes.NOP)
    POP = OperationInfo("pop", CommandTypes.NOP)
    INC = OperationInfo("increment", CommandTypes.NOP)
    DEC = OperationInfo("decrement", CommandTypes.NOP)
    ADD = OperationInfo("add", CommandTypes.DATA)
    SUB = OperationInfo("subtract", CommandTypes.DATA)
    MUL = OperationInfo("multiply", CommandTypes.DATA)
    DIV = OperationInfo("divide", CommandTypes.DATA)
    CMP = OperationInfo("compare", CommandTypes.DATA)
    JMP = OperationInfo("jump", CommandTypes.JUMP)
    SHL = OperationInfo("shift_left", CommandTypes.NOP)
    SHR = OperationInfo("shift_right", CommandTypes.NOP)
    JMN = OperationInfo("jump_if_negative", CommandTypes.JUMP)
    JMNN = OperationInfo("jump_if_not_negative", CommandTypes.JUMP)
    JMZ = OperationInfo("jump_if_zero", CommandTypes.JUMP)
    JMZN = OperationInfo("jump_if_not_zero", CommandTypes.JUMP)
    JMC = OperationInfo("jump_if_carry", CommandTypes.JUMP)
    JMNC = OperationInfo("jump_if_not_carry", CommandTypes.JUMP)
    CLR = OperationInfo("clear", CommandTypes.NOP)
    HLT = OperationInfo("halt", CommandTypes.NOP)
    IRET = OperationInfo("interrupt_return", CommandTypes.NOP)
    NOP = OperationInfo("no_operation", CommandTypes.NOP)

    def get_type(self):
        return self.value[1]

    def __str__(self):
        return self.value[0]
