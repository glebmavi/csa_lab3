import sys

from control_unit import ControlUnit
from data_path import DataPath


def main(code_file, input_file):
    with open(code_file) as file:
        code = eval(file.read())
    with open(input_file) as file:
        input_data = eval(file.read())
    data_path = DataPath()
    control_unit = ControlUnit(data_path, code, input_data, 3000)
    output, ticks, instructions = control_unit.run()
    print(f"Output: {output}\nInstruction number: {instructions}\nTicks: {ticks}")


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: machine.py <code_file> <input_file>"
    _, code_file, input_file = sys.argv
    main(code_file, input_file)
