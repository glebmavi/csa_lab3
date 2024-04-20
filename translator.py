import os
import sys
from src.asm.isa import *

INPUT_EXTENSION = ".asmm"
OUTPUT_EXTENSION = ".json"

labels = {}
variables = {}


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
        """
        Appends an instruction to the list. If an attempt is made to add an instruction with an existing address, an
        exception is thrown. The last address is incremented by 1 after adding an instruction.
        :param instruction: Instruction to add
        """
        if not isinstance(instruction, Instruction):
            raise ValueError(f"Invalid instruction: {instruction}")
        if instruction.index in [i.index for i in self.list]:
            raise ValueError(f"Memory already allocated: {instruction.index}")
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
        base_str = f"\"index\": {self.index}, \"opcode\": \"{self.opcode}\", \"value\": {self.value}"
        if self.relative is not None:
            base_str += f", \"relative\": {str(self.relative).lower()}"
        return base_str


def trimmer(code):
    """
    Removes comments and empty lines from the code
    :param code: Source code
    :return: List of lines without comments and empty lines
    """
    result = []
    for line in code:
        if not line:
            continue
        if line.__contains__(";"):
            line = line[:line.index(";")]
        line = line.strip()
        if line:
            result.append(line)
    return result


def section_split(source):
    """
    Splits the source code into data and code sections
    :param source: Source code
    :return: Separated lists data and code sections
    """
    data = []
    code = []
    in_data = False
    in_code = False
    for line in source:
        if line.__contains__("section .data"):
            in_data = True
            in_code = False
            continue
        if line.__contains__("section .code"):
            in_data = False
            in_code = True
            continue
        if in_data:
            data.append(line)
        if in_code:
            code.append(line)
    return data, code


def build_data(data, instructions: Instructions):
    """
    Builds the data section of the code by adding NOP instructions with the data values to the instructions list of the
    Instructions object. The added values are stored in the "variables" dictionary.
    :param data: List of data lines
    :param instructions: Instructions object
    """
    for line in data:
        if line.__contains__("index"):
            instructions.last_address = int(line.split(" ")[1])

        else:
            line = line.split(":")
            if len(line) == 2:
                value = line[1].strip()
                if value.__contains__("'"):
                    value = value[1:-1]
                    for i in range(len(value)):
                        variables[line[0].strip()] = instructions.last_address
                        instructions.append(Instruction(instructions.last_address, OpCode["NOP"], value[i]))
                else:
                    variables[line[0].strip()] = instructions.last_address
                    instructions.append(Instruction(instructions.last_address, OpCode["NOP"], value))
            else:
                raise ValueError(f"Invalid data line: {line}")


def build_code(code, instructions: Instructions):
    """
    Builds the code section of the code by adding instructions to the instructions list of the Instructions object.
    The added instructions are NOP, DATA or JUMP instructions. The labels dictionary is used to store the memory
    addresses of the labels.
    :param code: List of code lines
    :param instructions: Instructions object
    """
    start_label_found = False
    start_address = -1
    for line in code:
        if line.__contains__("index"):
            instructions.last_address = int(line.split(" ")[1])
        else:
            line = line.split()
            if line[0].__contains__("_"):
                label = line[0][1:]
                if label == "start":
                    start_label_found = True
                    start_address = instructions.last_address
                labels[label] = instructions.last_address
            else:
                if line[0] in OpCode.__members__:
                    opcode = OpCode[line[0]]
                    if len(line) == 2:
                        if line[1] in variables and opcode.get_type() == CommandTypes.DATA:
                            instructions.append(
                                Instruction(instructions.last_address, opcode, variables[line[1]], relative=False))
                        elif line[1] in labels and opcode.get_type() == CommandTypes.JUMP:
                            instructions.append(Instruction(instructions.last_address, opcode, labels[line[1]]))
                        elif line[1].__contains__("$") and opcode.get_type() == CommandTypes.DATA:
                            var = line[1][1:]
                            instructions.append(
                                Instruction(instructions.last_address, opcode, variables[var], relative=True))
                        else:
                            try:
                                instructions.append(Instruction(instructions.last_address, opcode, int(line[1])))
                            except ValueError:
                                raise ValueError(f"Invalid value: {line[1]}")
                    elif len(line) == 1:
                        instructions.append(Instruction(instructions.last_address, opcode, 0))
                else:
                    raise ValueError(f"Invalid command: {line[0]}")
    if not start_label_found:
        raise ValueError("Start label not found")

    return start_address


def json_builder(instructions: Instructions):
    """
    Builds a JSON string from the instructions list of the Instructions object.
    The JSON string is a list of dictionaries. Do not use this function to build a JSON file.
    :param instructions: Instructions object
    :return: List of strings
    """
    result = []
    for instruction in instructions.list:
        line = "{" + instruction.__str__() + "}"
        line += "," if instruction != instructions.list[-1] else ""
        result.append(line)
    return result


def translate(asmm):
    """
    Translates the source code into a JSON string
    :param asmm: Source code
    :return: JSON string
    """
    result = trimmer(asmm)
    data, code = section_split(result)
    ins = Instructions()
    build_data(data, ins)
    start_address = build_code(code, ins)
    result = json_builder(ins)
    return result, start_address


def write_code(target, start_address, code):
    """
    Writes the JSON string to a file
    :param target: Target file
    :param start_address: Start address of the code
    :param code: JSON string
    """
    with open(target, "w", encoding="utf-8") as file:
        file.write("[\n")
        file.write("""{"start_address": """ + str(start_address) + " },\n")
        for line in code:
            file.write(f"{line}\n")
        file.write("]\n")


def main(source, target):
    """
    Main function to translate the source code into a JSON file. The source file must have a .asmm extension and the
    target file must have a .json extension.
    :param source: Source file
    :param target: Target file
    """
    _, ext = os.path.splitext(source)
    if ext != INPUT_EXTENSION:
        raise ValueError(f"Source file must have a {INPUT_EXTENSION} extension")

    _, ext = os.path.splitext(target)
    if ext != OUTPUT_EXTENSION:
        raise ValueError(f"Target file must have a {OUTPUT_EXTENSION} extension")

    with open(source, encoding="utf-8") as file:
        code_source = file.read().split("\n")
    code, start_address = translate(code_source)
    if len(code) == 0:
        raise ValueError("No code to translate")
    write_code(target, start_address, code)


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: translator.py <source_file> <target_file>"
    _, source_file, target_file = sys.argv
    main(source_file, target_file)
