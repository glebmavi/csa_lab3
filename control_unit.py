import logging
from enum import Enum

from errors import UnknownOpcodeError
from isa import IN_ADDR, INT_RETURN, INT_START, OUT_ADDR, CommandTypes, OpCode
from translator import Instruction

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s    %(name)s:%(funcName)s     %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
    encoding="utf-8",
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
        self.instruction_counter = 0

        self.load_program(program)
        self.opcode_methods = {
            OpCode.LOAD: self.execute_load,
            OpCode.SAVE: self.execute_save,
            OpCode.PUSH: self.execute_push,
            OpCode.POP: self.execute_pop,
            OpCode.INC: self.execute_inc,
            OpCode.DEC: self.execute_dec,
            OpCode.ADD: self.execute_add,
            OpCode.SUB: self.execute_sub,
            OpCode.CMP: self.execute_cmp,
            OpCode.JMP: self.execute_jmp,
            OpCode.SHL: self.execute_shl,
            OpCode.SHR: self.execute_shr,
            OpCode.JMN: self.execute_jmn,
            OpCode.JMNN: self.execute_jmnn,
            OpCode.JMZ: self.execute_jmz,
            OpCode.JMNZ: self.execute_jmnz,
            OpCode.JMC: self.execute_jmc,
            OpCode.JMNC: self.execute_jmnc,
            OpCode.CLR: self.execute_clr,
            OpCode.HLT: self.execute_hlt,
            OpCode.IRET: self.execute_iret,
            OpCode.NOP: self.execute_nop,
        }

    def load_program(self, program):
        """
        Load a program into memory.
        Program is a list of Instruction objects and a start address at ht beginning.
        """
        self.data_path.ip = program[0]["start_address"]
        self.data_path.memory[INT_START] = program[1]["interrupt_address"]
        for instruction in program[2:]:
            index: int = instruction["index"]
            opcode = OpCode[instruction["opcode"].strip().upper()]
            value = instruction["value"]
            relative = instruction.get("relative", None)
            self.data_path.memory[index] = Instruction(index, opcode, value, relative)

    def __print__(self, string=""):
        info = (
            f"Tick: {self._tick:5} |"
            f"Action: {string:60} |"
            f"Interrupt: {self.interrupt.value:5} |"
            f"{self.data_path}"
        )
        logger.info(info)

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

    def execute_instruction(self):
        info = []
        try:
            opcode = self.data_path.cr.opcode
            if opcode in self.opcode_methods:
                info = self.opcode_methods[opcode]()
            else:
                raise UnknownOpcodeError(opcode)
        except IndexError or ValueError as _:
            logger.exception(f"Exception while executing instruction: {self.data_path.cr}")
            self.interrupt = InterruptType.ERROR

        self.data_path.ps = self.data_path.alu.get_flags_as_int()
        return info

    def instruction_step(self):
        try:
            self.data_path.fetch_instruction()
            self.tick("Fetch instruction (IP -> AR, mem[IP] -> CR)")
            self.tick("Fetch Instruction (IP + 1 -> IP)")

            if self.data_path.cr.opcode.get_type() in [CommandTypes.DATA, CommandTypes.JUMP]:
                self.data_path.read_operand()
                self.tick("Read operand (CR[addr] -> AR)")
                self.tick("Read operand (mem[AR] -> DR)")
                if self.data_path.cr.relative:
                    self.tick("Read operand (Relative addressing: DR -> AR)")
                    self.tick("Read operand (mem[AR] -> DR)")

            info = self.execute_instruction()
            for i in info:
                self.tick(f"Execute instruction ({i})")
        except IndexError or ValueError as _:
            logger.exception(f"Exception during instruction: {self.data_path.cr}")
            self.interrupt = InterruptType.ERROR

    def run(self, interrupt_type=InterruptType.NONE):
        while self.interrupt == interrupt_type:
            self.instruction_step()
            self.instruction_counter += 1

        if self.interrupt == InterruptType.INPUT:
            self.__print__(f"Input: {self.data_path.memory[IN_ADDR].value}")
            self.data_path.memory[INT_RETURN] = self.data_path.ip
            self.data_path.ip = self.data_path.memory[INT_START]
            self.tick("Input interr (IP -> mem[INT_RETURN], mem[INT_START] -> IP)")
            self.run(InterruptType.INPUT)

        elif self.interrupt == InterruptType.ERROR:
            self.__print__("Error")
        elif self.interrupt == InterruptType.HALT:
            self.__print__("Halt")
        elif self.interrupt == InterruptType.NONE:
            self.run()

        return self.data_path.output, self._tick + 1, self.instruction_counter

    def execute_load(self):
        self.data_path.update_acc(self.data_path.dr.value)
        return ["LOAD: DR -> ACC, PS"]

    def execute_save(self):
        self.data_path.memory[self.data_path.ar] = Instruction(self.data_path.ar, OpCode.NOP, self.data_path.acc)
        if self.data_path.ar == OUT_ADDR:
            self.data_path.output.append(self.data_path.acc)
            self.__print__(f"Output: {self.data_path.acc}")
        return ["SAVE: ACC -> mem[AR]"]

    def execute_push(self):
        self.data_path.memory[self.data_path.sp] = Instruction(self.data_path.sp, OpCode.NOP, self.data_path.acc)
        self.data_path.sp -= 1
        return ["PUSH: ACC -> mem[SP]", "PUSH: SP - 1 -> SP"]

    def execute_pop(self):
        self.data_path.update_acc(self.data_path.memory[self.data_path.sp].value)
        self.data_path.sp += 1
        return ["POP: mem[SP] -> ACC, PS", "POP: SP + 1 -> SP"]

    def execute_inc(self):
        self.data_path.update_acc(self.data_path.alu.add(self.data_path.acc, 1))
        return ["INC: ACC + 1 -> ACC, PS"]

    def execute_dec(self):
        self.data_path.update_acc(self.data_path.alu.sub(self.data_path.acc, 1))
        return ["DEC: ACC - 1 -> ACC, PS"]

    def execute_add(self):
        self.data_path.update_acc(self.data_path.alu.add(self.data_path.acc, self.data_path.dr.value))
        return ["ADD: ACC + DR -> ACC, PS"]

    def execute_sub(self):
        self.data_path.update_acc(self.data_path.alu.sub(self.data_path.acc, self.data_path.dr.value))
        return ["SUB: ACC - DR -> ACC, PS"]

    def execute_cmp(self):
        self.data_path.alu.cmp(self.data_path.acc, self.data_path.dr.value)  # Only sets flags, acc is not updated
        return ["CMP: ACC - DR -> PS"]

    def execute_jmp(self):
        self.data_path.ip = self.data_path.dr.index
        return ["JMP: DR -> IP"]

    def execute_shl(self):
        self.data_path.update_acc(self.data_path.alu.shl(self.data_path.acc), update_flags=False)  # shl sets flags
        return ["SHL: ACC << 1 -> ACC, PS"]

    def execute_shr(self):
        self.data_path.update_acc(self.data_path.alu.shr(self.data_path.acc), update_flags=False)  # shr sets flags
        return ["SHR: ACC >> 1 -> ACC, PS"]

    def execute_jmn(self):
        if self.data_path.ps & 0b100:
            self.data_path.ip = self.data_path.dr.index
        return ["JMN: N: DR -> IP"]

    def execute_jmnn(self):
        if not (self.data_path.ps & 0b100):
            self.data_path.ip = self.data_path.dr.index
        return ["JMNN: NOT N: DR -> IP"]

    def execute_jmz(self):
        if self.data_path.ps & 0b010:
            self.data_path.ip = self.data_path.dr.index
        return ["JMZ: Z: DR -> IP"]

    def execute_jmnz(self):
        if not (self.data_path.ps & 0b010):
            self.data_path.ip = self.data_path.dr.index
        return ["JMNZ: NOT Z: DR -> IP"]

    def execute_jmc(self):
        if self.data_path.ps & 0b001:
            self.data_path.ip = self.data_path.dr.index
        return ["JMC: C: DR -> IP"]

    def execute_jmnc(self):
        if not (self.data_path.ps & 0b001):
            self.data_path.ip = self.data_path.dr.index
        return ["JMNC: NOT C: DR -> IP"]

    def execute_clr(self):
        self.data_path.update_acc(self.data_path.alu.clr(), update_flags=False)  # clr sets flags
        return ["CLR: 0 -> ACC, PS"]

    def execute_hlt(self):
        self.interrupt = InterruptType.HALT
        return ["HLT"]

    def execute_iret(self):
        self.data_path.ip = self.data_path.memory[INT_RETURN]
        self.interrupt = InterruptType.NONE
        return ["IRET: mem[INTERRUPT_START] -> IP"]

    def execute_nop(self):
        return ["NOP"]
