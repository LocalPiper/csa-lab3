#!/usr/bin/env python3

from __future__ import annotations

import re
import sys

from isa import Command, Opcode, Variable, write_to_json

SECTION_DATA = "section .data:"
SECTION_TEXT = "section .code:"


def remove_comment(line: str) -> str:
    return re.sub(r";.*", "", line)


def remove_extra_spaces(line: str) -> str:
    line = line.strip()
    return re.sub(r"\s+", " ", line)


def clean_source(source: str) -> str:
    lines = source.splitlines()

    lines = map(remove_comment, lines)
    lines = map(remove_extra_spaces, lines)
    lines = filter(bool, lines)

    return "\n".join(lines)


def is_integer(value: str) -> bool:
    return bool(re.fullmatch(r"^-?\d+$", value))


def is_string(value: str) -> bool:
    return bool(re.fullmatch(r"^(\".*\")|(\'.*\')$", value))


def translate_section_data(section_data, address, variables):
    lines = section_data.splitlines()
    reference_variables = {}

    for line in lines:
        name, value = map(str.strip, line.split(":", 1))

        if is_integer(value):
            value = int(value)
            variable = Variable(name, address, [value], False)
            variables[name] = variable
            address += 1
        elif is_string(value):
            value = value.replace(r"\n", "\n")
            chars = [ord(char) for char in value[1:-1]] + [0]
            variable = Variable(name, address, chars, True)
            variables[name] = variable
            address += len(chars)
        elif value.startswith("bf"):
            _, size = value.split(" ", 1)
            size = int(size)
            variable = Variable(name, address, [0] * size, False)
            variables[name] = variable
            address += size
        else:
            variable = Variable(name, address, [0], False)
            variables[name] = variable
            reference_variables[name] = value
            address += 1

    for reference_variable_name in reference_variables:
        target_variable_name = reference_variables[reference_variable_name]
        variables[reference_variable_name].data = [
            variables[target_variable_name].address
        ]
    return variables, address


def translate_section_text_stage_1(section_text, address):
    lines = section_text.splitlines()
    labels = {}
    commands = []

    for line in lines:
        if line.startswith("."):
            labels[line[:-1]] = address
        else:
            commands.append(line)
            address += 1
    return "\n".join(commands), labels


def translate_command(line, variables, labels):
    parts = line.split(" ")
    opcode = Opcode(parts[0])

    if len(parts)  < 2:
        return Command(opcode)

    if is_integer(parts[1]):
        value = int(parts[1])
    else:
        if parts[1] in variables:
            value = variables[parts[1]].address
        else:
            if parts[1] in labels:
                value = labels[parts[1]]
            else:
                value = parts[1]
    return Command(opcode, value)



def translate_section_text_stage_2(section_text, variables, labels):
    lines = section_text.splitlines()
    commands = []

    for line in lines:
        commands.append(translate_command(line, variables, labels))

    return commands


def translate_variables(
    variables,
    address: int,
    memory: list[tuple[str, str]],
):
    for variable in variables.values():
        for cell in variable.data:
            if variable.is_string and cell != 0:
                memory.append((str(address), str(cell)))
            elif variable.is_string and cell == 0:
                memory.append((str(address), "0"))
            else:
                memory.append((str(address), str(cell)))
            address += 1
    return memory, address


def translate_commands(
    commands, address, code: list[tuple[str, str, str]]
):
    for command in commands:
        code.append((str(address), str(command.opcode), ""))
        address += 1
        if command.operand is not None:
            code[-1] = (code[-1][0], code[-1][1], str(command.operand))
    return code, address


def translate_source(source):
    source = clean_source(source)
    section_data_index = source.find(SECTION_DATA)
    section_text_index = source.find(SECTION_TEXT)
    section_data = source[
        section_data_index + len(SECTION_DATA) + 1 : section_text_index
    ]
    section_text = source[section_text_index + len(SECTION_TEXT) + 1 :]
    variables = {}
    variables, memory_address = translate_section_data(section_data, 3, variables)
    section_text_address = 0
    section_text, labels = translate_section_text_stage_1(
        section_text, section_text_address
    )
    commands = translate_section_text_stage_2(section_text, variables, labels)
    code : list[tuple[str,str,str]] = []
    memory : list[tuple[str,str]] = []
    command_address = 0
    memory_address = 3
    memory, memory_address = translate_variables(
        variables, memory_address, memory
    )
    code, command_address = translate_commands(
        commands, command_address, code
    )

    return code, memory


def main(source, target):
    with open(source, encoding="utf-8") as f:
        source = f.read()

    code, memory = translate_source(source)

    write_to_json(target, code, memory)

    print(
        f"source LoC: {len(source.splitlines())} code instr: {len(code)}"
    )


if __name__ == "__main__":
    assert (
        len(sys.argv) == 3
    ), "Invalid usage: python translator.py <source_file> <target_file>"
    _, source, target = sys.argv
    main(source, target)
