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

        print(f"DEBUG LOAD: b={b}, c={c}")

        # Ограничим константу 12 битами (0-4095)
        if b > 4095:
            raise ValueError(f"Константа {b} слишком большая, максимум 4095")
        if not (0 <= c <= 0x1F):
            raise ValueError(f"Адрес {c} выходит за диапазон 0-31")

        # ИСПРАВЛЕННАЯ упаковка:
        byte1 = a  # код операции
        byte2 = b & 0xFF  # младшие 8 бит константы
        byte3 = ((b >> 8) & 0x0F) | ((c & 0x1F) << 4)  # старшие 4 бита константы + адрес

        # Проверим что byte3 в диапазоне
        # (b>>8)&0x0F = 0-15, c<<4 = 0-496 → максимум 15+496=511 ❌ все еще может быть >255!

        # РЕШЕНИЕ: ограничим адрес 3 битами (0-7) вместо 5 битов
        if c > 7:
            raise ValueError(f"Адрес регистра {c} слишком большой, максимум 7")

        byte3 = ((b >> 8) & 0x0F) | ((c & 0x07) << 4)  # старшие 4 бита константы + адрес (3 бита)
        # Максимум: 15 + (7<<4)=15+112=127 ✅

        bytes_list = [byte1, byte2, byte3]

        for i, byte in enumerate(bytes_list):
            print(f"DEBUG LOAD Byte {i + 1}: {byte} (0x{byte:02x})")
            if not (0 <= byte <= 255):
                raise ValueError(f"Byte {i + 1} выходит за диапазон: {byte}")

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
        if not (0 <= d <= 0x1F):
            raise ValueError(f"Адрес регистра {d} выходит за диапазон 0-31")

        # ИСПРАВЛЕННАЯ упаковка для READ
        byte1 = a  # код операции (22)
        byte2 = (b & 0x1F) | ((d & 0x07) << 5)  # result_reg + address_reg (младшие 3 бита)
        byte3 = c  # offset

        print(f"DEBUG ASSEMBLE READ: b={b}, c={c}, d={d} -> bytes=[0x{byte1:02x}, 0x{byte2:02x}, 0x{byte3:02x}]")

        return [byte1, byte2, byte3], {'A': a, 'B': b, 'C': c, 'D': d}

    def assemble_write(self, command):
        a = self.command_codes['write']
        b = command['value_reg']
        c = command['address_reg']
        d = command['offset']

        if not (0 <= b <= 0x1F):
            raise ValueError(f"Адрес регистра значения {b} выходит за диапазон 0-31")
        if not (0 <= c <= 0x1F):
            raise ValueError(f"Адрес регистра адреса {c} выходит за диапазон 0-31")
        if not (0 <= d <= 0xFF):
            raise ValueError(f"Смещение {d} выходит за диапазон 0-255")

        # ПРАВИЛЬНАЯ упаковка для WRITE
        byte1 = a  # код операции (26)
        byte2 = (b & 0x1F) | ((c & 0x1F) << 5)  # value_reg (0-31) + address_reg (0-31)
        # byte2: 0-31 | 0-31<<5 = 0-31 | 0-992 = 0-1023 ❌ Выходит за 255!

        # ИСПРАВЛЕНИЕ: ограничим сдвиг
        byte2 = (b & 0x1F) | ((c & 0x07) << 5)  # value_reg (0-31) + address_reg (0-7) - ограничиваем!
        byte3 = d  # offset (0-255)

        return [byte1, byte2, byte3], {'A': a, 'B': b, 'C': c, 'D': d}

    def assemble_pow(self, command):
        a = self.command_codes['pow']
        b = command['value2_reg']
        c = command['result_reg']
        d = command['value1_addr']

        print(f"DEBUG POW: a={a}, b={b}, c={c}, d={d}")

        if not (0 <= b <= 0x1F):
            raise ValueError(f"Адрес регистра {b} выходит за диапазон 0-31")
        if not (0 <= c <= 0x1F):
            raise ValueError(f"Адрес регистра результата {c} выходит за диапазон 0-31")
        if not (0 <= d <= 0x3FFFFFF):
            raise ValueError(f"Адрес памяти {d} выходит за диапазон 0-67108863")

        # СУПЕР-ПРОСТАЯ упаковка (6 байт)
        byte1 = a  # код операции = 42
        byte2 = b  # value2_reg = 4
        byte3 = c  # result_reg = 5
        byte4 = (d >> 0) & 0xFF  # D[0:7] = 1000 & 0xFF = 232
        byte5 = (d >> 8) & 0xFF  # D[8:15] = (1000 >> 8) & 0xFF = 3
        byte6 = (d >> 16) & 0xFF  # D[16:23] = (1000 >> 16) & 0xFF = 0

        bytes_list = [byte1, byte2, byte3, byte4, byte5, byte6]

        # Проверим каждый байт
        for i, byte in enumerate(bytes_list):
            print(f"DEBUG Byte {i + 1}: {byte} (0x{byte:02x})")
            if not (0 <= byte <= 255):
                raise ValueError(f"Byte {i + 1} выходит за диапазон: {byte}")

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
            print(f"DEBUG: Обрабатываем команду {i + 1}: {command}")

            try:
                bytes_list, fields = self.assemble_command(command)
                print(f"DEBUG: Получены байты: {bytes_list}")

                # Проверим каждый байт
                for j, byte in enumerate(bytes_list):
                    if not (0 <= byte <= 255):
                        print(f"ERROR: Byte {j} выходит за диапазон: {byte}")
                        raise ValueError(f"Byte {j} выходит за диапазон: {byte}")

                binary_code.extend(bytes_list)
                intermediate_representation.append({
                    'index': i,
                    'command': command['command'],
                    'fields': fields,
                    'bytes': bytes_list
                })
                print(f"DEBUG: Команда {i + 1} успешно ассемблирована")

            except Exception as e:
                print(f"DEBUG: Ошибка в команде {i + 1}: {e}")
                raise

        return binary_code, intermediate_representation

    def save_binary(self, binary_code, filename):
        with open(filename, 'wb') as f:
            f.write(bytes(binary_code))

    def display_test_output(self, intermediate_repr):
        print("ПРОМЕЖУТОЧНОЕ ПРЕДСТАВЛЕНИЕ ПРОГРАММЫ:")

        for item in intermediate_repr:
            print(f"Команда {item['index'] + 1}: {item['command'].upper()}")
            print(f"Поля: {item['fields']}")
            hex_bytes = [f"0x{byte:02x}" for byte in item['bytes']]
            print(f"Байты: {hex_bytes}")
            print()

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

        #  Запись в двоичный файл
        assembler.save_binary(binary_code, args.output_file)

        if args.test:
            #  Расширенный вывод в тестовом режиме
            assembler.display_test_output(intermediate_repr, binary_code)
        else:
            # Вывод числа команд в обычном режиме
            print(f"Ассемблировано команд: {len(intermediate_repr)}")

    except Exception as e:
        print(f"Ошибка ассемблирования: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()