import json
from enum import Enum


class Variable:
    def __init__(self, name, address, data, is_string):
        self.name = name
        self.address = address
        self.data = data
        self.is_string = is_string

    def to_dict(self):

        return {
            "name": self.name,
            "address": self.address,
            "data": self.data,
            "is_string": self.is_string
        }

    @staticmethod
    def from_dict(data):
        return Variable(data["name"], data["address"], data["data"], data["is_string"])

class Opcode(str, Enum):
    NOP = "nop"
    SWAP = "swap"
    PUSH = "push"
    POP = "pop"
    LD = "ld"
    ST = "st"
    DUP = "dup"
    JMP = "jmp"
    JZ = "jz"
    JNZ = "jnz"
    CMP = "cmp"
    JL = "jl"
    JLE = "jle"
    JG = "jg"
    JGE = "jge"
    CALL = "call"
    RET = "ret"
    INC = "inc"
    ADD = "add"
    SUB = "sub"
    OR = "or"
    AND = "and"
    LIT = "lit"
    HALT = "hlt"

    def __str__(self):
        return str(self.value)


class Command:
    def __init__(self, opcode=Opcode.NOP, operand=None):
        self.opcode = opcode
        self.operand = operand

    def __str__(self):
        return (
            f"{self.opcode}"
            if self.operand is not None
            else f"{self.opcode}"
        )

    def to_dict(self):
        return {"opcode": str(self.opcode), "operand": self.operand}

    @staticmethod
    def from_dict(data):
        return Command(Opcode(data["opcode"]), data.get("operand"))


def to_json_struct(obj):
    if isinstance(obj, tuple):
        return list(obj)
    if isinstance(obj, list):
        return [to_json_struct(item) for item in obj]
    if isinstance(obj, dict):
        return {key: to_json_struct(value) for key, value in obj.items()}
    return obj

def write_to_json(filename: str, code_lines: list, memory: list):
    data = {
        "code": [to_json_struct(line) for line in code_lines],
        "memory": [to_json_struct(var) for var in memory],
    }
    with open(filename, mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def read_from_json(filename: str):
    with open(filename) as f:
        data = json.load(f)
        return data["code"], data["memory"]

def write_code(filename: str, code: str):
    with open(filename, mode="bw") as f:
        f.write(code.encode("utf-8"))


def read_code(filename):
    with open(filename, mode="rb") as f:
        code = f.read()
        code = str(code, encoding="utf-8").splitlines()
        return list(code)
