import os
from assembler import Assembler

def run_test(test_name, input_file, expected_bytes):
    print(f" Тестируем: {test_name}")
    print(f" Файл: {input_file}")

    try:
        assembler = Assembler()
        program = assembler.load_program(input_file)
        binary_code, intermediate_repr = assembler.assemble(program)

        # Сохраняем во временный файл для проверки
        with open('test_output.bin', 'wb') as f:
            f.write(bytes(binary_code))

        # Читаем и проверяем байты
        with open('test_output.bin', 'rb') as f:
            binary_data = f.read()

        actual_bytes = [f"0x{byte:02x}" for byte in binary_data]
        print(f"Сгенерировано: {actual_bytes}")
        print(f" Ожидалось:    {expected_bytes}")

        if actual_bytes == expected_bytes:
            print(" ТЕСТ ПРОЙДЕН!")
            return True
        else:
            print(" ТЕСТ НЕ ПРОЙДЕН!")
            return False

    except Exception as e:
        print(f"ОШИБКА: {e}")
        return False


def main():
    print("ТЕСТИРОВАНИЕ АССЕМБЛЕРА")
    tests = [
        {
            'name': 'LOAD (A=6, B=152, C=21)',
            'file': 'examples/test_load.yaml',
            'expected': ['0x06', '0x26', '0xa8']
        },
        {
            'name': 'READ (A=22, B=14, C=245, D=24)',
            'file': 'examples/test_read.yaml',
            'expected': ['0x96', '0xab', '0xc7']
        },
        {
            'name': 'WRITE (A=26, B=16, C=28, D=127)',
            'file': 'examples/test_write.yaml',
            'expected': ['0x1a', '0xe4', '0x7f']
        },
        {
            'name': 'POW (A=42, B=8, C=5, D=470)',
            'file': 'examples/test_pow.yaml',
            'expected': ['0x2a', '0x2a', '0xd6', '0x01', '0x00', '0x00']
        }
    ]

    passed = 0
    for test in tests:
        success = run_test(test['name'], test['file'], test['expected'])
        if success:
            passed += 1
        print()

    print(f"ИТОГ: {passed}/{len(tests)} тестов пройдено")

    # Очистка
    if os.path.exists('test_output.bin'):
        os.remove('test_output.bin')


if __name__ == "__main__":
    main()