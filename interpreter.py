import sys
import argparse
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


class UVMInterpreter:
    def __init__(self):
        self.memory = [0] * 65536
        self.registers = [0] * 32
        self.pc = 0
        self.halted = False

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='Интерпретатор УВМ')
        parser.add_argument('binary_file', help='Путь к бинарному файлу с программой')
        parser.add_argument('dump_file', help='Путь к файлу для дампа памяти')
        parser.add_argument('--dump-range', required=True, help='Диапазон адресов для дампа (формат: start-end)')
        parser.add_argument('--quiet', action='store_true', help='Тихий режим (без отладочного вывода)')
        return parser.parse_args()

    def load_program(self, filename):
        with open(filename, 'rb') as f:
            binary_data = f.read()

        for i, byte in enumerate(binary_data):
            if i < len(self.memory):
                self.memory[i] = byte

        print(f"Загружено {len(binary_data)} байт программы")

    def parse_dump_range(self, dump_range):
        start, end = map(int, dump_range.split('-'))
        return start, end

    def decode_command(self):
        if self.pc >= len(self.memory) - 2:
            return None, None

        first_byte = self.memory[self.pc]

        # Определяем команду по первому байту
        if first_byte == 0x06:  # LOAD
            return self.decode_load()
        elif first_byte == 0x16:  # READ
            return self.decode_read()
        elif first_byte == 0x1a:  # WRITE
            return self.decode_write()
        elif first_byte == 0x2a:  # POW
            return self.decode_pow()
        else:
            self.pc += 3
            return None, None

    def decode_load(self):
        byte1 = self.memory[self.pc]
        byte2 = self.memory[self.pc + 1]
        byte3 = self.memory[self.pc + 2]

        constant = byte2 | ((byte3 & 0x0F) << 8)
        address = (byte3 >> 4) & 0x07

        self.pc += 3
        return 'load', {'constant': constant, 'address': address}

    def decode_read(self):
        byte1 = self.memory[self.pc]
        byte2 = self.memory[self.pc + 1]
        byte3 = self.memory[self.pc + 2]

        result_reg = byte2 & 0x1F
        address_reg = (byte2 >> 5) & 0x07
        offset = byte3

        self.pc += 3
        return 'read', {'result_reg': result_reg, 'offset': offset, 'address_reg': address_reg}

    def decode_write(self):
        byte1 = self.memory[self.pc]
        byte2 = self.memory[self.pc + 1]
        byte3 = self.memory[self.pc + 2]

        value_reg = byte2 & 0x1F
        address_reg = (byte2 >> 5) & 0x07
        offset = byte3

        self.pc += 3
        return 'write', {'value_reg': value_reg, 'address_reg': address_reg, 'offset': offset}

    def decode_pow(self):
        byte1 = self.memory[self.pc]
        byte2 = self.memory[self.pc + 1]
        byte3 = self.memory[self.pc + 2]
        byte4 = self.memory[self.pc + 3]
        byte5 = self.memory[self.pc + 4]
        byte6 = self.memory[self.pc + 5]

        value2_reg = byte2
        result_reg = byte3
        value1_addr = (byte4 << 0) | (byte5 << 8) | (byte6 << 16)

        self.pc += 6
        return 'pow', {'value2_reg': value2_reg, 'result_reg': result_reg, 'value1_addr': value1_addr}

    def execute_command(self, command_type, params):
        if command_type == 'load':
            self.execute_load(params)
        elif command_type == 'read':
            self.execute_read(params)
        elif command_type == 'write':
            self.execute_write(params)
        elif command_type == 'pow':
            self.execute_pow(params)

    def execute_load(self, params):
        constant = params['constant']
        address = params['address']
        self.registers[address] = constant

    def execute_read(self, params):
        address_reg = params['address_reg']
        offset = params['offset']
        result_reg = params['result_reg']

        mem_address = self.registers[address_reg] + offset
        if mem_address < len(self.memory):
            self.registers[result_reg] = self.memory[mem_address]

    def execute_write(self, params):
        value_reg = params['value_reg']
        address_reg = params['address_reg']
        offset = params['offset']

        mem_address = self.registers[address_reg] + offset
        if mem_address < len(self.memory):
            self.memory[mem_address] = self.registers[value_reg]

    def execute_pow(self, params):
        value2_reg = params['value2_reg']
        result_reg = params['result_reg']
        value1_addr = params['value1_addr']

        value1 = self.memory[value1_addr] if value1_addr < len(self.memory) else 0
        value2_addr = self.registers[value2_reg]
        value2 = self.memory[value2_addr] if value2_addr < len(self.memory) else 0

        try:
            if value1 < 0 or value2 < 0:
                result = 0
            elif value1 == 0 and value2 == 0:
                result = 1
            else:
                result = int(value1 ** value2)
                if result > 0xFFFFFFFF:
                    result = 0xFFFFFFFF
        except:
            result = 0

        self.registers[result_reg] = result

    def create_memory_dump(self, start_addr, end_addr, filename):
        root = Element('memory_dump')
        root.set('start', str(start_addr))
        root.set('end', str(end_addr))

        for addr in range(start_addr, end_addr + 1):
            if addr < len(self.memory):
                byte_elem = SubElement(root, 'byte')
                byte_elem.set('address', str(addr))
                byte_elem.set('value', str(self.memory[addr]))
                byte_elem.text = f"0x{self.memory[addr]:02x}"

        xml_str = minidom.parseString(tostring(root)).toprettyxml(indent="  ")

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(xml_str)

        print(f"Дамп памяти сохранен в {filename} (адреса {start_addr}-{end_addr})")

    def run(self):
        args = self.parse_arguments()
        self.load_program(args.binary_file)
        start_addr, end_addr = self.parse_dump_range(args.dump_range)

        if not args.quiet:
            print("Запуск интерпретатора УВМ...")
            print("=" * 50)

        command_count = 0
        while not self.halted and self.pc < len(self.memory):
            try:
                command_type, params = self.decode_command()
                if command_type is None:
                    break
                self.execute_command(command_type, params)
                command_count += 1
            except Exception as e:
                if not args.quiet:
                    print(f"Ошибка выполнения команды по адресу {self.pc}: {e}")
                break

        if not args.quiet:
            print("=" * 50)

        print(f"Выполнено команд: {command_count}")
        self.create_memory_dump(start_addr, end_addr, args.dump_file)

        if not args.quiet:
            print("\nСостояние регистров:")
            for i in range(0, 32, 8):
                regs = [f"R[{i + j}]=0x{self.registers[i + j]:02x}" for j in range(8) if i + j < 32]
                print("  " + " | ".join(regs))


def main():
    interpreter = UVMInterpreter()
    interpreter.run()


if __name__ == "__main__":
    main()