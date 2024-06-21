class DataPath:
    data_memory_size: int
    
    data_memory: list[int]

    data_address: int

    tos: int

    buffer_register: int

    data_stack: list[int]

    address_register: int

    input_buffer: list

    output_buffer: list

def __init__(self, data_memory_size, input_buffer):
        assert data_memory_size > 0, "Data_memory size should be non-zero"
        self.data_memory_size = data_memory_size
        self.data_memory = [0] * data_memory_size
        self.data_address = 0
        self.address_register = 0
        self.tos = 0
        self.buffer_register = 0
        self.data_address = 3
        self.data_stack = []
        self.input_buffer = input_buffer
        self.output_buffer = []

    def signal_latch_ar(self):
        self.address_register = self.tos

    def signal_address(self):
        self.data_address = self.address_register

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


    def swap(self):
        self.signal_latch_br(self.data_stack[-1])
        self.data_stack.pop()
        self.signal_data_push()
        self.signal_bf_to_tos()


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
        if self.data_address  == OUTPUT_ADDRESS:
            self.signal_data_pop()
            if isinstance(self.tos, int):
                symbol = chr(self.tos)
            else:
                symbol = self.tos
            logging.debug(
                "output: %s << %s", repr("".join(self.output_buffer)), repr(symbol)
            )
            self.output_buffer.append(symbol)
        elif self.data_address  == OUTPUT_NUM:
            self.signal_data_pop()
            symbol = str(self.tos)
            logging.debug(
                "output: %s << %s", repr("".join(self.output_buffer)), repr(symbol)
            )
            self.output_buffer.append(symbol)
        else:
            self.data_memory[self.data_address] = self.signal_data_pop()

    def zero(self):
        return self.tos == 0

    def negative(self):
        return self.tos < 0


class ControlUnit:
    pass


def main():
    pass


if __name__ == "__main__":
    pass
