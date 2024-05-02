from enum import Enum
from typing import NamedTuple

# Constants:
SYS_BITS = 32
ADDRESS_RANGE = 11
VALUE_RANGE = SYS_BITS - 1
MAX_ADDRESS = (1 << ADDRESS_RANGE) - 1
MIN_VALUE = -(1 << VALUE_RANGE)
MAX_VALUE = (1 << VALUE_RANGE) - 1
IN_ADDR = MAX_ADDRESS - 1
OUT_ADDR = MAX_ADDRESS
INTERRUPT_START = MAX_ADDRESS - 2
INTERRUPT_RETURN = MAX_ADDRESS - 3
STACK_START = MAX_ADDRESS - 4


class CommandTypes(Enum):
    DATA = "data"
    JUMP = "jump"
    NOP = "nop"


class OperationInfo(NamedTuple):
    opcode: str
    command_type: CommandTypes


class OpCode(OperationInfo, Enum):
    LOAD = OperationInfo("LOAD", CommandTypes.DATA)
    SAVE = OperationInfo("SAVE", CommandTypes.DATA)
    PUSH = OperationInfo("PUSH", CommandTypes.NOP)
    POP = OperationInfo("POP", CommandTypes.NOP)
    INC = OperationInfo("INC", CommandTypes.NOP)
    DEC = OperationInfo("DEC", CommandTypes.NOP)
    ADD = OperationInfo("ADD", CommandTypes.DATA)
    SUB = OperationInfo("SUB", CommandTypes.DATA)
    CMP = OperationInfo("CMP", CommandTypes.DATA)
    JMP = OperationInfo("JMP", CommandTypes.JUMP)
    SHL = OperationInfo("SHL", CommandTypes.NOP)
    SHR = OperationInfo("SHR", CommandTypes.NOP)
    JMN = OperationInfo("JMN", CommandTypes.JUMP)
    JMNN = OperationInfo("JMNN", CommandTypes.JUMP)
    JMZ = OperationInfo("JMZ", CommandTypes.JUMP)
    JMNZ = OperationInfo("JMNZ", CommandTypes.JUMP)
    JMC = OperationInfo("JMC", CommandTypes.JUMP)
    JMNC = OperationInfo("JMNC", CommandTypes.JUMP)
    CLR = OperationInfo("CLR", CommandTypes.NOP)
    HLT = OperationInfo("HLT", CommandTypes.NOP)
    IRET = OperationInfo("IRET", CommandTypes.NOP)
    NOP = OperationInfo("NOP", CommandTypes.NOP)

    def get_type(self):
        return self.value[1]

    def __str__(self):
        return self.value[0]
