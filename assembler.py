import yaml
import sys
import argparse


class Assembler:
    def __init__(self, register_bits=5):
        """
        register_bits: количество бит для адреса регистра
        - 5 бит для этапа 1 (0-31)
        - 3 бита для этапов 2-5 (0-7)
        """
        self.register_bits = register_bits
        self.max_register = (1 << register_bits) - 1
        self.command_codes = {
            'load': 6,
            'read': 22,
            'write': 26,
            'pow': 42
        }

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='Ассемблер УВМ')
        parser.add_argument('input_file', help='Путь к исходному файлу YAML')
        parser.add_argument('output_file', help='Путь к двоичному файлу-результату')
        parser.add_argument('--test', action='store_true', help='Режим тестирования')
        parser.add_argument('--stage1', action='store_true', help='Режим этапа 1 (регистры 0-31)')
        return parser.parse_args()

    def load_program(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def assemble_load(self, command):
        """LOAD: A=6 бит, B=13 бит, C=5 бит (3 байта)"""
        a = self.command_codes['load']
        b = command['constant']
        c = command['address']

        # Проверка диапазонов
        if not (0 <= b <= 0x1FFF):  # 13 бит
            raise ValueError(f"Константа {b} выходит за диапазон 0-8191")
        if not (0 <= c <= self.max_register):
            raise ValueError(f"Адрес {c} выходит за диапазон 0-{self.max_register}")

        # Формируем 24 бита (3 байта)
        word = (a & 0x3F) | ((b & 0x1FFF) << 6) | ((c & 0x1F) << 19)

        byte1 = word & 0xFF
        byte2 = (word >> 8) & 0xFF
        byte3 = (word >> 16) & 0xFF

        return [byte1, byte2, byte3], {'A': a, 'B': b, 'C': c}

    def assemble_read(self, command):
        """READ: A=6 бит, B=5 бит, C=8 бит, D=5 бит (3 байта)"""
        a = self.command_codes['read']
        b = command['result_reg']
        c = command['offset']
        d = command['address_reg']

        # Проверка диапазонов
        if not (0 <= b <= self.max_register):
            raise ValueError(f"Адрес регистра результата {b} выходит за диапазон 0-{self.max_register}")
        if not (0 <= c <= 0xFF):
            raise ValueError(f"Смещение {c} выходит за диапазон 0-255")
        if not (0 <= d <= self.max_register):
            raise ValueError(f"Адрес регистра {d} выходит за диапазон 0-{self.max_register}")

        # Формируем 24 бита (3 байта)
        word = (a & 0x3F) | ((b & 0x1F) << 6) | ((c & 0xFF) << 11) | ((d & 0x1F) << 19)

        byte1 = word & 0xFF
        byte2 = (word >> 8) & 0xFF
        byte3 = (word >> 16) & 0xFF

        return [byte1, byte2, byte3], {'A': a, 'B': b, 'C': c, 'D': d}

    def assemble_write(self, command):
        """WRITE: A=6 бит, B=5 бит, C=5 бит, D=8 бит (3 байта)"""
        a = self.command_codes['write']
        b = command['value_reg']
        c = command['address_reg']
        d = command['offset']

        # Проверка диапазонов
        if not (0 <= b <= self.max_register):
            raise ValueError(f"Адрес регистра значения {b} выходит за диапазон 0-{self.max_register}")
        if not (0 <= c <= self.max_register):
            raise ValueError(f"Адрес регистра адреса {c} выходит за диапазон 0-{self.max_register}")
        if not (0 <= d <= 0xFF):
            raise ValueError(f"Смещение {d} выходит за диапазон 0-255")

        # Формируем 24 бита (3 байта)
        word = (a & 0x3F) | ((b & 0x1F) << 6) | ((c & 0x1F) << 11) | ((d & 0xFF) << 16)

        byte1 = word & 0xFF
        byte2 = (word >> 8) & 0xFF
        byte3 = (word >> 16) & 0xFF

        return [byte1, byte2, byte3], {'A': a, 'B': b, 'C': c, 'D': d}

    def assemble_pow(self, command):
        """POW: A=6 бит, B=5 бит, C=5 бит, D=26 бит (6 байт)"""
        a = self.command_codes['pow']
        b = command['value2_reg']
        c = command['result_reg']
        d = command['value1_addr']

        # Проверка диапазонов
        if not (0 <= b <= self.max_register):
            raise ValueError(f"Адрес регистра {b} выходит за диапазон 0-{self.max_register}")
        if not (0 <= c <= self.max_register):
            raise ValueError(f"Адрес регистра результата {c} выходит за диапазон 0-{self.max_register}")
        if not (0 <= d <= 0x3FFFFFF):
            raise ValueError(f"Адрес памяти {d} выходит за диапазон 0-67108863")

        # Формируем 48 бит (6 байт)
        word1 = (a & 0x3F) | ((b & 0x1F) << 6) | ((c & 0x1F) << 11) | ((d & 0xFF) << 16)
        word2 = (d >> 8) & 0x3FFFF  # 18 бит

        byte1 = word1 & 0xFF
        byte2 = (word1 >> 8) & 0xFF
        byte3 = (word1 >> 16) & 0xFF
        byte4 = word2 & 0xFF
        byte5 = (word2 >> 8) & 0xFF
        byte6 = (word2 >> 16) & 0xFF

        return [byte1, byte2, byte3, byte4, byte5, byte6], {'A': a, 'B': b, 'C': c, 'D': d}

    def assemble_command(self, command):
        cmd_type = command['command']
        # ... остальной код без изменений

    def assemble(self, program):
        binary_code = []
        intermediate_representation = []

        for i, command in enumerate(program):
            bytes_list, fields = self.assemble_command(command)
            binary_code.extend(bytes_list)
            intermediate_representation.append({
                'index': i,
                'command': command['command'],
                'fields': fields,
                'bytes': bytes_list
            })

        return binary_code, intermediate_representation

    def save_binary(self, binary_code, filename):
        with open(filename, 'wb') as f:
            f.write(bytes(binary_code))

    def display_test_output(self, intermediate_repr):
        print("ПРОМЕЖУТОЧНОЕ ПРЕДСТАВЛЕНИЕ ПРОГРАММЫ:")
        print("=" * 50)

        for item in intermediate_repr:
            print(f"Команда {item['index'] + 1}: {item['command'].upper()}")
            print(f"Поля: {item['fields']}")
            hex_bytes = [f"0x{byte:02x}" for byte in item['bytes']]
            print(f"Байты: {hex_bytes}")
            print()


def main():
    args = Assembler().parse_arguments()  # Сначала парсим аргументы

    # Создаем ассемблер с нужным количеством бит
    if args.stage1:
        assembler = Assembler(register_bits=5)  # Для этапа 1: 0-31
        print("🔧 Режим этапа 1: регистры 0-31")
    else:
        assembler = Assembler(register_bits=3)  # Для этапов 2-5: 0-7
        print("🔧 Режим этапов 2-5: регистры 0-7")

    try:
        program = assembler.load_program(args.input_file)
        binary_code, intermediate_repr = assembler.assemble(program)
        assembler.save_binary(binary_code, args.output_file)

        if args.test:
            assembler.display_test_output(intermediate_repr)
            print(f"Программа успешно ассемблирована!")
            print(f"Размер бинарного кода: {len(binary_code)} байт")

    except Exception as e:
        print(f"Ошибка ассемблирования: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()