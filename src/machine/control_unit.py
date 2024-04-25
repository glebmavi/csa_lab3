import logging

from src.asm.isa import *
from translator import Instruction

logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format='%(message)s',  # Set the format of the log messages
    handlers=[  # Handlers determine where the log messages go: stdout, file, etc.
        logging.StreamHandler()  # Log to stdout
    ]
)

logger = logging.getLogger(__name__)


class InterruptType(Enum):
    INPUT = "input"
    ERROR = "error"
    HALT = "halt"
    NONE = "none"


class ControlUnit:
    def __init__(self, data_path, program, input_data, limit=1000):
        self.data_path = data_path
        self._tick = 0
        self.input_data = input_data
        self.limit = limit
        self.interrupt = InterruptType.NONE
        self.data_path.load_program(program)

    def tick(self, string=""):
        self.__print__(string)
        self._tick += 1
        if self.input_data:
            if self._tick == self.input_data[0][0]:
                self.data_path.memory[IN_ADDR] = Instruction(IN_ADDR, OpCode.NOP, self.input_data[0][1])
                self.interrupt = InterruptType.INPUT
                self.input_data.pop(0)
        if self._tick >= self.limit:
            self.interrupt = InterruptType.ERROR

    def __print__(self, string=""):
        info = (
            f"Tick: {self._tick:5} |"
            f"Action: {string:75} |"
            f"Interrupt: {self.interrupt.value:5} |"
            f"{self.data_path}"
        )
        logger.info(info)

    def run(self, interrupt_type=InterruptType.NONE):
        while self.interrupt == interrupt_type:
            try:
                self.data_path.fetch_instruction()
                self.tick("Fetch instruction (IP -> AR, IP + 1 -> IP, mem[AR] -> DR, DR -> CR)")

                if self.data_path.cr.opcode.get_type() in [CommandTypes.DATA, CommandTypes.JUMP]:
                    self.data_path.read_operand()
                    self.tick("Read operand (CR[addr] -> DR, DR -> AR, mem[AR] -> DR)")

                info = self.execute_instruction()
                self.tick(f"Execute instruction ({info})")
            except Exception as e:
                logger.error(e)
                self.interrupt = InterruptType.ERROR

        if self.interrupt == InterruptType.INPUT:
            self.__print__(f"Input: {self.data_path.memory[IN_ADDR]}")
            self.data_path.memory[self.data_path.sp] = self.data_path.ip
            self.data_path.ip = self.data_path.memory[INTERRUPT_START]
            self.tick("Input interruption (IP -> mem[SP], mem[INTERRUPT_START] -> IP)")
            self.run(InterruptType.INPUT)

        elif self.interrupt == InterruptType.ERROR:
            self.__print__("Error")
        elif self.interrupt == InterruptType.HALT:
            self.__print__("Halt")
        elif self.interrupt == InterruptType.NONE:
            self.run()

    def execute_instruction(self):
        info = ""
        try:
            opcode = self.data_path.cr.opcode
            if opcode == OpCode.LOAD:
                self.data_path.alu.clr()
                self.data_path.acc = self.data_path.dr.value
                info = "LOAD: DR -> ACC"
            elif opcode == OpCode.SAVE:
                self.data_path.memory[self.data_path.ar] = (
                    Instruction(self.data_path.ar, OpCode.NOP, self.data_path.acc))
                if self.data_path.ar == OUT_ADDR:
                    self.data_path.output.append(self.data_path.acc)
                    self.__print__(f"Output: {self.data_path.acc}")
                info = "SAVE: ACC -> mem[AR]"
            elif opcode == OpCode.PUSH:
                self.data_path.sp -= 1
                self.data_path.memory[self.data_path.sp] = (
                    Instruction(self.data_path.sp, OpCode.NOP, self.data_path.acc))
                info = "PUSH: SP - 1 -> SP, ACC -> mem[SP]"
            elif opcode == OpCode.POP:
                self.data_path.acc = self.data_path.memory[self.data_path.sp].value
                self.data_path.sp += 1
                info = "POP: mem[SP] -> ACC, SP + 1 -> SP"
            elif opcode == OpCode.INC:
                self.data_path.acc = self.data_path.alu.add(self.data_path.acc, 1)
                info = "INC: ACC + 1 -> ACC"
            elif opcode == OpCode.DEC:
                self.data_path.acc = self.data_path.alu.sub(self.data_path.acc, 1)
                info = "DEC: ACC - 1 -> ACC"
            elif opcode == OpCode.ADD:
                self.data_path.acc = self.data_path.alu.add(self.data_path.acc, self.data_path.dr.value)
                info = "ADD: ACC + DR -> ACC"
            elif opcode == OpCode.SUB:
                self.data_path.acc = self.data_path.alu.sub(self.data_path.acc, self.data_path.dr.value)
                info = "SUB: ACC - DR -> ACC"
            elif opcode == OpCode.CMP:
                self.data_path.alu.cmp(self.data_path.acc, self.data_path.dr.value)
                info = "CMP: ACC - DR -> PS"
            elif opcode == OpCode.JMP:
                self.data_path.ip = self.data_path.dr.value
                info = "JMP: DR -> IP"
            elif opcode == OpCode.SHL:
                self.data_path.acc = self.data_path.alu.shl(self.data_path.acc)
                info = "SHL: ACC << 1 -> ACC"
            elif opcode == OpCode.SHR:
                self.data_path.acc = self.data_path.alu.shr(self.data_path.acc)
                info = "SHR: ACC >> 1 -> ACC"
            elif opcode == OpCode.JMN:
                if self.data_path.alu.get_flags_as_int(self.data_path.acc) >= 4:
                    self.data_path.ip = self.data_path.dr.index
                    info = "JMN: N: DR -> IP"
            elif opcode == OpCode.JMNN:
                if self.data_path.alu.get_flags_as_int(self.data_path.acc) < 4:
                    self.data_path.ip = self.data_path.dr.index
                    info = "JMNN: NOT N: DR -> IP"
            elif opcode == OpCode.JMZ:
                if self.data_path.alu.get_flags_as_int(self.data_path.acc) in [2, 3, 7]:
                    self.data_path.ip = self.data_path.dr.index
                    info = "JMZ: Z: DR -> IP"
            elif opcode == OpCode.JMNZ:
                if self.data_path.alu.get_flags_as_int(self.data_path.acc) not in [2, 3, 7]:
                    self.data_path.ip = self.data_path.dr.index
                    info = "JMNZ: NOT Z: DR -> IP"
            elif opcode == OpCode.JMC:
                if self.data_path.alu.get_flags_as_int(self.data_path.acc) in [1, 3, 5, 7]:
                    self.data_path.ip = self.data_path.dr.index
                    info = "JMC: C: DR -> IP"
            elif opcode == OpCode.JMNC:
                if self.data_path.alu.get_flags_as_int(self.data_path.acc) not in [1, 3, 5, 7]:
                    self.data_path.ip = self.data_path.dr.index
                    info = "JMNC: NOT C: DR -> IP"
            elif opcode == OpCode.CLR:
                self.data_path.alu.clr()
                info = "CLR: ALU"
            elif opcode == OpCode.HLT:
                self.interrupt = InterruptType.HALT
                info = "HALT"
            elif opcode == OpCode.IRET:
                self.data_path.ip = self.data_path.memory[self.data_path.sp]
                self.interrupt = InterruptType.NONE
                info = "IRET: mem[INTERRUPT_START] -> IP"
            elif opcode == OpCode.NOP:
                pass
            else:
                raise ValueError(f"Unknown opcode: {opcode}")
        except IndexError or ValueError as e:
            logger.error(e)
            self.interrupt = InterruptType.ERROR

        self.data_path.ps = self.data_path.alu.get_flags_as_int(self.data_path.acc)
        return info
