#!/usr/bin/python3


from __future__ import annotations

import logging
import sys

from definitions import INPUT_ADDRESS, OUTPUT_ADDRESS, OUTPUT_NUM
from isa import Command, Opcode, read_from_json


class DataPath:
    data_memory_size: int

    data_memory: list[int]

    data_address: int

    tos: int

    buffer_register: int

    data_stack: list[int]


    input_buffer: list

    output_buffer: list

    def __init__(self, data_memory_size, input_buffer):
        assert data_memory_size > 0, "Data_memory size should be non-zero"
        self.data_memory_size = data_memory_size
        self.data_memory = [0] * data_memory_size
        self.data_address = 0
        self.tos = 0
        self.buffer_register = 0
        self.data_address = 3
        self.data_stack = []
        self.input_buffer = input_buffer
        self.output_buffer = []

    def signal_address(self):
        self.data_address = self.tos

    def signal_latch_br(self, val):
        self.buffer_register = val

    def signal_data_push(self):
        self.data_stack.append(self.tos)

    def signal_data_pop(self):
        self.tos = self.data_stack.pop()
        return self.tos

    def signal_mem_to_tos(self):
        self.tos = self.get_char()

    def signal_bf_to_tos(self):
        self.signal_latch_tos(self.buffer_register)

    def signal_latch_tos(self, value):
        self.tos = value

    def get_char(self):
        if self.data_address == INPUT_ADDRESS:
            if len(self.input_buffer) == 0:
                return ord("\0")
            symbol = self.input_buffer.pop(0)
            symbol_code = ord(symbol)
            assert -128 <= symbol_code <= 127, "input token is out of bound: {}".format(
                symbol_code
            )
            logging.debug("input: %s", repr(symbol))
            return symbol_code
        logging.info("data_address: %s", self.data_address)
        return self.data_memory[self.data_address]

    def signal_wr(self):
        logging.info("data_address: %s", self.data_address)
        if self.data_address  == OUTPUT_ADDRESS:
            symbol = chr(self.tos)
            logging.debug(
                "output: %s << %s", repr("".join(self.output_buffer)), repr(symbol)
            )
            self.output_buffer.append(symbol)
        elif self.data_address  == OUTPUT_NUM:
            symbol = str(self.tos)
            logging.debug(
                "output: %s << %s", repr("".join(self.output_buffer)), repr(symbol)
            )
            self.output_buffer.append(symbol)
        else:
            logging.info("Memory set: data_address: %s, tos: %s", self.data_address, self.tos)
            self.data_memory[self.data_address] = self.tos


    def swap(self):
        self.signal_latch_br(self.tos)
        self.signal_data_pop()
        self.buffer_register, self.tos = self.tos, self.buffer_register
        self.signal_data_push()
        self.signal_latch_tos(self.buffer_register)
    def zero(self):
        return self.tos == 0

    def negative(self):
        return self.tos < 0


class ControlUnit:
    output_buffer = None

    instruction_memory_size: int

    instruction_memory: list[Command]

    instruction_stack: list[int]

    program: list

    program_counter: int

    data_path: DataPath

    address_command_reg: int

    def signal_ret_push(self):
        self.instruction_stack.append(self.program_counter + 1)

    def signal_ret_pop(self):
        self.signal_latch_pc(self.instruction_stack.pop())

    def signal_instr_addr(self):
        self.address_instr_mem = self.program_counter

    def signal_latch_pc(self, value):
        self.program_counter = value

    def __init__(self, program, data_path, instruction_memory_size):
        self.program_counter = 0
        self.data_path = data_path
        self.instruction_stack = []
        self.instruction_memory_size = instruction_memory_size
        self.instruction_memory = list([Command()] * instruction_memory_size)
        self.program = program

    def signal_latch_program_counter(self, sel_next=True):
        if sel_next:
            self.program_counter += 1
        else:
            self.program_counter = self.address_instr_mem

    def signal_bf_to_tos(self):
        self.data_path.signal_latch_tos(self.data_path.buffer_register)

    def is_control_flow_instruction(self, opcode):
        return opcode in [
            Opcode.JMP,
            Opcode.JZ,
            Opcode.JNZ,
        ]

    def decode_and_execute_control_flow_instruction(self, opcode, address):
        self.data_path.data_stack.append(address)
        if opcode is Opcode.JMP:
            self.data_path.swap()
            self.program_counter = self.data_path.tos
            self.address_instr_mem = self.program_counter
            self.data_path.signal_data_pop()
            return True

        if opcode is Opcode.JZ:
            if self.data_path.zero():
                self.data_path.swap()
                self.program_counter = self.data_path.tos
                self.address_instr_mem = self.program_counter
                self.data_path.signal_data_pop()
                return True
            self.data_path.swap()
            self.data_path.signal_data_pop()

            return False


        if opcode is Opcode.JNZ:
            if not self.data_path.zero():
                self.data_path.swap()
                self.program_counter = self.data_path.tos
                self.address_instr_mem = self.program_counter
                self.data_path.signal_data_pop()
                return True
            self.data_path.swap()
            self.data_path.signal_data_pop()

            return False

        if opcode is Opcode.JL:
            if self.data_path.negative() and not self.data_path.zero():
                self.data_path.swap()
                self.program_counter = self.data_path.tos
                self.address_instr_mem = self.program_counter
                self.data_path.signal_data_pop()
                return True
            self.data_path.swap()
            self.data_path.signal_data_pop()

            return False


        if opcode is Opcode.JLE:
            if self.data_path.negative() or self.data_path.zero():
                self.data_path.swap()
                self.program_counter = self.data_path.tos
                self.address_instr_mem = self.program_counter
                self.data_path.signal_data_pop()
                return True
            self.data_path.swap()
            self.data_path.signal_data_pop()

            return False



        if opcode is Opcode.CALL:
            self.data_path.swap()
            self.signal_ret_push()
            self.program_counter = self.data_path.tos
            self.address_instr_mem = self.data_path.tos
            self.data_path.signal_data_pop()
            return True

        if opcode is Opcode.RET:
            self.signal_ret_pop()
            self.address_command_reg = self.program_counter
            self.address_instr_mem = self.program_counter
            return True
        self.data_path.data_stack.pop()
        return False

    def decode_and_execute_instruction(self):
        instr = self.instruction_memory[self.program_counter]
        opcode = instr.opcode


        if instr.operand is not None:
            if self.decode_and_execute_control_flow_instruction(opcode, int(instr.operand)):
                return
            if not self.is_control_flow_instruction(opcode):
                    logging.info("Instruction has operand: %s", instr.operand)
                    self.data_path.signal_data_push()
                    self.data_path.signal_latch_tos(int(instr.operand))

        if opcode is Opcode.HALT:
            raise StopIteration()

        if opcode == Opcode.NOP:
            return

        if opcode == Opcode.PUSH:
            pass

        if opcode == Opcode.POP:
            self.data_path.signal_data_pop()

        if opcode == Opcode.ST:
            self.data_path.signal_address()
            self.data_path.signal_data_pop()
            logging.info("We are executing ST, TOS is %s", self.data_path.tos)
            self.data_path.signal_wr()


        if opcode == Opcode.LD:
            self.data_path.signal_address()
            self.data_path.signal_mem_to_tos()


        if opcode == Opcode.INC:
            self.data_path.signal_latch_tos(
                1 + self.data_path.tos
            )

        if opcode == Opcode.ADD:
            self.data_path.signal_latch_tos(
                    self.data_path.data_stack[-1] + self.data_path.tos
            )

        if opcode == Opcode.SUB:
            self.data_path.signal_latch_tos(
                -self.data_path.data_stack[-1]+ self.data_path.tos
            )
            self.data_path.data_stack.pop()

        if opcode == Opcode.OR:
            self.data_path.signal_latch_tos(
                self.data_path.data_stack[-1] | self.data_path.tos
            )
            self.data_path.signal_latch_tos(self.data_path.signal_data_pop())

        if opcode == Opcode.AND:
            self.data_path.signal_latch_tos(
                self.data_path.data_stack[-1] & self.data_path.tos
            )
            self.data_path.data_stack.pop()
        if opcode == Opcode.SWAP:
            self.data_path.signal_latch_br(self.data_path.data_stack[-1])
            self.data_path.data_stack.pop()
            self.data_path.signal_data_push()
            self.data_path.signal_bf_to_tos()

        if opcode == Opcode.DUP:
            self.data_path.signal_data_push()

        if opcode is Opcode.RET:
            self.signal_ret_pop()
            self.address_command_reg = self.program_counter
            self.address_instr_mem = self.program_counter
            return

        self.signal_latch_program_counter(sel_next=True)

    def __repr__(self):
        state_repr = "PC: {:3} ADDR: {:3} MEM_OUT: {:3} TOS: {:3} COMMAND {:3} ".format(
            self.program_counter,
            self.data_path.data_address,
            self.data_path.data_memory[self.data_path.data_address],
            self.data_path.tos,
            str(self.instruction_memory[self.program_counter])
        )

        instr = self.instruction_memory[self.program_counter]
        opcode = instr.opcode
        instr_repr = str(opcode)

        if instr.operand is not None:
            instr_repr += " {}".format(instr.operand)

        return "{} \t{}".format(state_repr, instr_repr)


def simulation(code, memory, input_tokens, data_memory_size, limit):
    data_path = DataPath(data_memory_size, input_tokens)
    for data in memory:
        data_path.data_memory[int(data[0])] = int(data[1])
    control_unit = ControlUnit(code, data_path, limit)
    for command in code:
        if(command[2] == ""):
            control_unit.instruction_memory[int(command[0])] = Command(Opcode(command[1]))
        else:
            control_unit.instruction_memory[int(command[0])] = Command(Opcode(command[1]), command[2])
    instr_counter = 0

    logging.debug("%s", control_unit)
    try:
        while instr_counter < limit:
            control_unit.decode_and_execute_instruction()
            instr_counter += 1
            logging.info("TOS: %s", data_path.tos)
            logging.info("STACK: %s", data_path.data_stack)
            logging.debug("%s", control_unit)
    except StopIteration:
        pass

    if instr_counter >= limit:
        logging.warning("Limit exceeded!")

    logging.info("output_buffer: %s", repr("".join(data_path.output_buffer)))
    return "".join(data_path.output_buffer), instr_counter


def main(code_file, input_file):
    code, memory = read_from_json(code_file)
    with open(input_file, encoding="utf-8") as file:
        input_text = file.read()
        input_token = []
        for char in input_text:
            input_token.append(char)

    output, instr_counter = simulation(
        code,
        memory,
        input_tokens=input_token,
        data_memory_size=300,
        limit=1000
    )

    print("".join(output))
    print("instr_counter: ", instr_counter)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    assert len(sys.argv) == 3, "Wrong arguments: machine.py <code_file> <input_file>"
    _, code_file, input_file = sys.argv
    main(code_file, input_file)

