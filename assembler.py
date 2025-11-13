import yaml
import sys
import argparse


class Assembler:
    def __init__(self):
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
        return parser.parse_args()

    def load_program(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def assemble_load(self, command):
        a = self.command_codes['load']
        b = command['constant']
        c = command['address']

        # Ограничим константу 12 битами (0-4095)
        if b > 4095:
            raise ValueError(f"Константа {b} слишком большая, максимум 4095")
        if c > 7:
            raise ValueError(f"Адрес регистра {c} слишком большой, максимум 7")

        byte1 = a
        byte2 = b & 0xFF
        byte3 = ((b >> 8) & 0x0F) | ((c & 0x07) << 4)

        bytes_list = [byte1, byte2, byte3]

        for byte in bytes_list:
            if not (0 <= byte <= 255):
                raise ValueError(f"Byte выходит за диапазон: {byte}")

        return bytes_list, {'A': a, 'B': b, 'C': c}

    def assemble_read(self, command):
        a = self.command_codes['read']
        b = command['result_reg']
        c = command['offset']
        d = command['address_reg']

        if not (0 <= b <= 0x1F):
            raise ValueError(f"Адрес регистра результата {b} выходит за диапазон 0-31")
        if not (0 <= c <= 0xFF):
            raise ValueError(f"Смещение {c} выходит за диапазон 0-255")
        if d > 7:
            raise ValueError(f"Адрес регистра {d} слишком большой, максимум 7")

        byte1 = a
        byte2 = (b & 0x1F) | ((d & 0x07) << 5)
        byte3 = c

        return [byte1, byte2, byte3], {'A': a, 'B': b, 'C': c, 'D': d}

    def assemble_write(self, command):
        a = self.command_codes['write']
        b = command['value_reg']
        c = command['address_reg']
        d = command['offset']

        if not (0 <= b <= 0x1F):
            raise ValueError(f"Адрес регистра значения {b} выходит за диапазон 0-31")
        if c > 7:
            raise ValueError(f"Адрес регистра адреса {c} слишком большой, максимум 7")
        if not (0 <= d <= 0xFF):
            raise ValueError(f"Смещение {d} выходит за диапазон 0-255")

        byte1 = a
        byte2 = (b & 0x1F) | ((c & 0x07) << 5)
        byte3 = d

        return [byte1, byte2, byte3], {'A': a, 'B': b, 'C': c, 'D': d}

    def assemble_pow(self, command):
        a = self.command_codes['pow']
        b = command['value2_reg']
        c = command['result_reg']
        d = command['value1_addr']

        if not (0 <= b <= 0x1F):
            raise ValueError(f"Адрес регистра {b} выходит за диапазон 0-31")
        if not (0 <= c <= 0x1F):
            raise ValueError(f"Адрес регистра результата {c} выходит за диапазон 0-31")
        if not (0 <= d <= 0x3FFFFFF):
            raise ValueError(f"Адрес памяти {d} выходит за диапазон 0-67108863")

        byte1 = a
        byte2 = b
        byte3 = c
        byte4 = (d >> 0) & 0xFF
        byte5 = (d >> 8) & 0xFF
        byte6 = (d >> 16) & 0xFF

        bytes_list = [byte1, byte2, byte3, byte4, byte5, byte6]

        for byte in bytes_list:
            if not (0 <= byte <= 255):
                raise ValueError(f"Byte выходит за диапазон: {byte}")

        return bytes_list, {'A': a, 'B': b, 'C': c, 'D': d}

    def assemble_command(self, command):
        cmd_type = command['command']

        if cmd_type == 'load':
            return self.assemble_load(command)
        elif cmd_type == 'read':
            return self.assemble_read(command)
        elif cmd_type == 'write':
            return self.assemble_write(command)
        elif cmd_type == 'pow':
            return self.assemble_pow(command)
        else:
            raise ValueError(f"Неизвестная команда: {cmd_type}")

    def assemble(self, program):
        binary_code = []
        intermediate_representation = []

        for i, command in enumerate(program):
            try:
                bytes_list, fields = self.assemble_command(command)

                # Проверим каждый байт
                for byte in bytes_list:
                    if not (0 <= byte <= 255):
                        raise ValueError(f"Byte выходит за диапазон: {byte}")

                binary_code.extend(bytes_list)
                intermediate_representation.append({
                    'index': i,
                    'command': command['command'],
                    'fields': fields,
                    'bytes': bytes_list
                })

            except Exception as e:
                raise ValueError(f"Ошибка в команде {i + 1}: {e}")

        return binary_code, intermediate_representation

    def save_binary(self, binary_code, filename):
        with open(filename, 'wb') as f:
            f.write(bytes(binary_code))

    def display_test_output(self, intermediate_repr, binary_code):
        print("ПРОМЕЖУТОЧНОЕ ПРЕДСТАВЛЕНИЕ ПРОГРАММЫ:")
        print("=" * 50)

        for item in intermediate_repr:
            print(f"Команда {item['index'] + 1}: {item['command'].upper()}")
            print(f"Поля: {item['fields']}")
            hex_bytes = [f"0x{byte:02x}" for byte in item['bytes']]
            print(f"Байты: {hex_bytes}")
            print()

        print("РЕЗУЛЬТАТ:")
        hex_output = [f"0x{byte:02x}" for byte in binary_code]
        print(f"Байтовый вывод: {hex_output}")
        print(f"Всего байт: {len(binary_code)}")
        print(f"Ассемблировано команд: {len(intermediate_repr)}")


def main():
    assembler = Assembler()
    args = assembler.parse_arguments()

    try:
        program = assembler.load_program(args.input_file)
        binary_code, intermediate_repr = assembler.assemble(program)

        # Запись в двоичный файл
        assembler.save_binary(binary_code, args.output_file)

        if args.test:
            # Расширенный вывод в тестовом режиме
            assembler.display_test_output(intermediate_repr, binary_code)
        else:
            # Только число команд в обычном режиме
            print(f"Ассемблировано команд: {len(intermediate_repr)}")

    except Exception as e:
        print(f"Ошибка ассемблирования: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()