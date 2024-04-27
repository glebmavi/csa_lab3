import sys
from pathlib import Path

from isa import IN_ADDR, MAX_ADDRESS, OUT_ADDR, CommandTypes, OpCode

INPUT_EXTENSION = ".asmm"
OUTPUT_EXTENSION = ".asmx"

labels = {}
variables = {"IN": IN_ADDR, "OUT": OUT_ADDR}


class Instructions:
    """
    Represents a list of instructions

    Attributes:
    list: List of instructions
    last_address: Last memory address used
    """

    def __init__(self):
        self.list = []
        self.last_address = 0

    def append(self, instruction):
        if not isinstance(instruction, Instruction):
            raise InvalidInstructionError(instruction)
        if instruction.index in [i.index for i in self.list]:
            raise MemoryAlreadyAllocatedError(instruction.index)
        if instruction.index > MAX_ADDRESS - 3:  # to avoid stack and input/output addresses
            raise MemoryOutOfRangeError(instruction.index)
        self.list.append(instruction)
        self.last_address += 1

    def __str__(self):
        return ",\n".join(str(instruction) for instruction in self.list)


class Instruction:
    """
    Represents a single instruction

    Attributes:
    index: Memory address
    opcode: Instruction type
    value: Value of data or address to jump. Otherwise, 0
    relative: If the value is a relative address
    """
    def __init__(self, index, opcode: OpCode, value, relative=None):
        self.index = index
        self.opcode = opcode
        self.value = value
        self.relative = relative

    def __str__(self):
        base_str = (f'"index": {self.index:4}, '
                    f'"opcode": "{self.opcode:4}", '
                    f'"value": {self.value:10}')
        if self.relative is not None:
            base_str += f', "relative": {self.relative!s:5}'
        return base_str


def trimmer(code):
    result = []
    for line in code:
        if not line:
            continue
        if ";" in line:
            line = line[:line.index(";")]
        line = line.strip()
        if line:
            result.append(line)
    return result


def section_split(source):
    data = []
    code = []
    in_data = False
    in_code = False
    for line in source:
        if "section .data" in line:
            in_data = True
            in_code = False
            continue
        if "section .code" in line:
            in_data = False
            in_code = True
            continue
        if in_data:
            data.append(line)
        if in_code:
            code.append(line)
    return data, code


def process_index_line(line, instructions):
    instructions.last_address = int(line.split(" ")[1])


def process_data_line(line, instructions):
    line = line.split(":")
    if len(line) == 2:
        if line[0] == "IN" or line[0] == "OUT":
            raise ReservedVariableError(line[0])
        value = line[1].strip()
        if "'" in value:
            process_string_value(line, value, instructions)
        else:
            process_numeric_value(line, instructions, value)
    else:
        raise InvalidDataLineError(line)


def process_string_value(line, value, instructions):
    value = value[1:-1]
    variables[line[0].strip()] = instructions.last_address
    for i in range(len(value)):
        if value[i] == value[-1]:
            instructions.append(
                Instruction(instructions.last_address, OpCode["NOP"], f"'{value[i]}'"))
            instructions.append(Instruction(instructions.last_address, OpCode["NOP"], "'\\0'"))
        else:
            instructions.append(
                Instruction(instructions.last_address, OpCode["NOP"], f"'{value[i]}'"))


def process_numeric_value(line, instructions, value):
    variables[line[0].strip()] = instructions.last_address
    instructions.append(Instruction(instructions.last_address, OpCode["NOP"], value))


def build_data(data, instructions: Instructions):
    for line in data:
        if "index" in line:
            process_index_line(line, instructions)
        else:
            process_data_line(line, instructions)


def process_instruction_line(line, instructions):
    opcode = OpCode[line[0]]
    if len(line) == 2:
        if line[1] in variables and opcode.get_type() == CommandTypes.DATA:
            instructions.append(
                Instruction(instructions.last_address, opcode, variables[line[1]], relative=False))
        elif line[1] in labels and opcode.get_type() == CommandTypes.JUMP:
            instructions.append(Instruction(instructions.last_address, opcode, labels[line[1]]))
        elif "$" in line[1] and opcode.get_type() == CommandTypes.DATA:
            var = line[1][1:]
            instructions.append(
                Instruction(instructions.last_address, opcode, variables[var], relative=True))
        else:
            try:
                instructions.append(Instruction(instructions.last_address, opcode, int(line[1])))
            except ValueError:
                raise InvalidValueError(line[1])
    elif len(line) == 1:
        instructions.append(Instruction(instructions.last_address, opcode, 0))


def process_label_line(line, instructions, start_found, start_addr, interrupt_found, interrupt_addr):
    label = line[0][1:]
    if label == "start":
        start_found = True
        start_addr = instructions.last_address
    elif label == "int":
        interrupt_found = True
        interrupt_addr = instructions.last_address

    labels[label] = instructions.last_address
    return start_found, start_addr, interrupt_found, interrupt_addr


def build_code(code, instructions: Instructions):
    start_label_found, interrupt_label_found = False, False
    start_address, interrupt_address = -1, -1

    for line in code:
        if "index" in line:
            process_index_line(line, instructions)
        else:
            line = line.split()
            if "_" in line[0]:
                start_label_found, start_address, interrupt_label_found, interrupt_address = process_label_line(
                    line, instructions, start_label_found, start_address, interrupt_label_found, interrupt_address)
            else:
                if line[0] in OpCode.__members__:
                    process_instruction_line(line, instructions)
                else:
                    raise InvalidCommandError(line[0])
    if not start_label_found:
        raise LabelNotFoundError("start")
    if not interrupt_label_found:
        raise LabelNotFoundError("int")

    return start_address, interrupt_address


def json_builder(instructions: Instructions):

    result = []
    for instruction in instructions.list:
        line = "{" + instruction.__str__() + "}"
        line += "," if instruction != instructions.list[-1] else ""
        result.append(line)
    return result


def translate(asmm):
    result = trimmer(asmm)
    data, code = section_split(result)
    ins = Instructions()
    build_data(data, ins)
    start_address, interrupt_address = build_code(code, ins)
    result = json_builder(ins)
    return result, start_address, interrupt_address


def write_code(target, start_address, code, interrupt_address):
    with open(target, "w", encoding="utf-8") as file:
        file.write("[\n")
        file.write("""{"start_address": """ + str(start_address) + " },\n")
        file.write("""{"interrupt_address": """ + str(interrupt_address) + " },\n")
        for line in code:
            file.write(f"{line}\n")
        file.write("]\n")


def main(source, target):
    ext = Path(source).suffix
    if ext != INPUT_EXTENSION:
        raise ExtensionError(ext)

    ext = Path(target).suffix
    if ext != OUTPUT_EXTENSION:
        raise ExtensionError(ext)

    with open(source, encoding="utf-8") as file:
        code_source = file.read().split("\n")
    code, start_address, interrupt_address = translate(code_source)
    if len(code) == 0:
        raise EmptyCodeError()
    write_code(target, start_address, code, interrupt_address)


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: translator.py <source_file> <target_file>"
    _, source_file, target_file = sys.argv
    main(source_file, target_file)


class ExtensionError(Exception):
    def __init__(self, ext):
        self.message = f"Invalid extension: {ext}"
        super().__init__(self.message)


class EmptyCodeError(Exception):
    def __init__(self):
        self.message = "No code to translate"
        super().__init__(self.message)


class LabelNotFoundError(Exception):
    def __init__(self, label):
        self.message = f"Label not found: _{label}"
        super().__init__(self.message)


class InvalidCommandError(Exception):
    def __init__(self, command):
        self.message = f"Invalid command: {command}"
        super().__init__(self.message)


class InvalidValueError(Exception):
    def __init__(self, value):
        self.message = f"Invalid value: {value}"
        super().__init__(self.message)


class InvalidDataLineError(Exception):
    def __init__(self, line):
        self.message = f"Invalid data line: {line}"
        super().__init__(self.message)


class ReservedVariableError(Exception):
    def __init__(self, variable):
        self.message = f"Cannot use reserved variable name: {variable}"
        super().__init__(self.message)


class MemoryOutOfRangeError(Exception):
    def __init__(self, address):
        self.message = f"Memory address out of range: {address}"
        super().__init__(self.message)


class MemoryAlreadyAllocatedError(Exception):
    def __init__(self, address):
        self.message = f"Memory already allocated: {address}"
        super().__init__(self.message)


class InvalidInstructionError(Exception):
    def __init__(self, instruction):
        self.message = f"Invalid instruction: {instruction}"
        super().__init__(self.message)
