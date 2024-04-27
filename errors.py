class UnknownOpcodeError(Exception):
    def __init__(self, opcode):
        super().__init__(f"Unknown opcode: {opcode}")


class InstructionPointerError(Exception):
    def __init__(self, int_pointer):
        self.message = f"Instruction Pointer out of bounds: {int_pointer}"
        super().__init__(self.message)


class AddressRegisterError(Exception):
    def __init__(self, address_register):
        self.message = f"Address Register out of bounds: {address_register}"
        super().__init__(self.message)


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
