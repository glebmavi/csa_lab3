from enum import Enum

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


class OpCode(str, Enum):
    LOAD = ("load", CommandTypes.DATA)
    SAVE = ("save", CommandTypes.DATA)
    PUSH = ("push", CommandTypes.NOP)
    POP = ("pop", CommandTypes.NOP)
    INC = ("increment", CommandTypes.NOP)
    DEC = ("decrement", CommandTypes.NOP)
    ADD = ("add", CommandTypes.DATA)
    SUB = ("subtract", CommandTypes.DATA)
    MUL = ("multiply", CommandTypes.DATA)
    DIV = ("divide", CommandTypes.DATA)
    CMP = ("compare", CommandTypes.DATA)
    JMP = ("jump", CommandTypes.JUMP)
    SHL = ("shift_left", CommandTypes.NOP)
    SHR = ("shift_right", CommandTypes.NOP)
    JMN = ("jump_if_negative", CommandTypes.JUMP)
    JMNN = ("jump_if_not_negative", CommandTypes.JUMP)
    JMZ = ("jump_if_zero", CommandTypes.JUMP)
    JMZN = ("jump_if_not_zero", CommandTypes.JUMP)
    JMC = ("jump_if_carry", CommandTypes.JUMP)
    JMNC = ("jump_if_not_carry", CommandTypes.JUMP)
    CLR = ("clear", CommandTypes.NOP)
    HLT = ("halt", CommandTypes.NOP)
    IRET = ("interrupt_return", CommandTypes.NOP)

    def get_type(self):
        return self.value[1]
