import os
import sys
from assembler import Assembler
from interpreter import UVMInterpreter


def test_pow_operation():
    print(" ТЕСТ ЭТАПА 4: Команда POW")
    print("=" * 60)

    assembler = Assembler()

    try:
        # Ассемблируем тестовую программу
        print("Ассемблируем программу...")
        program = assembler.load_program('examples/pow_test.yaml')
        binary_code, _ = assembler.assemble(program)

        with open('test_pow.bin', 'wb') as f:
            f.write(bytes(binary_code))
        print(f"Создан файл test_pow.bin ({len(binary_code)} байт)")

        # Запускаем интерпретатор
        print("Запускаем интерпретатор...")
        interpreter = UVMInterpreter()
        interpreter.load_program('test_pow.bin')

        interpreter.pc = 0
        command_count = 0
        max_commands = 40  # увеличим лимит

        while interpreter.pc < len(interpreter.memory) and command_count < max_commands:
            try:
                command_type, params = interpreter.decode_command()
                if command_type is None:
                    print("Достигнут конец программы")
                    break
                interpreter.execute_command(command_type, params)
                command_count += 1
            except Exception as e:
                print(f"Ошибка выполнения: {e}")
                break

        print(f"Выполнено команд: {command_count}")

        # Проверяем результаты
        print("\n" + "=" * 50)
        print("ПРОВЕРКА РЕЗУЛЬТАТОВ POW:")
        print("=" * 50)

        # Ожидаемые результаты
        expected_2_3 = 8  # 2^3 = 8
        expected_5_2 = 25  # 5^2 = 25

        # Теперь результаты в R[0] и R[1]
        actual_2_3 = interpreter.registers[0]
        actual_5_2 = interpreter.registers[1]

        print(f"2^3: R[0] = {actual_2_3} (ожидается {expected_2_3})")
        print(f"5^2: R[1] = {actual_5_2} (ожидается {expected_5_2})")

        # Проверяем что результаты записались в память
        memory_2_3 = interpreter.memory[700]
        memory_5_2 = interpreter.memory[701]

        print(f"Память[700] = {memory_2_3} (ожидается {expected_2_3})")
        print(f"Память[701] = {memory_5_2} (ожидается {expected_5_2})")

        # Проверяем корректность
        success = (actual_2_3 == expected_2_3 and
                   actual_5_2 == expected_5_2 and
                   memory_2_3 == expected_2_3 and
                   memory_5_2 == expected_5_2)

        if success:
            print(" КОМАНДА POW РАБОТАЕТ КОРРЕКТНО!")
            return True
        else:
            print(" ОШИБКА В ВЫЧИСЛЕНИЯХ POW!")
            return False

    except Exception as e:
        print(f" ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("ТЕСТИРОВАНИЕ ЭТАПА 4: АРИФМЕТИКО-ЛОГИЧЕСКОЕ УСТРОЙСТВО")
    print("=" * 60)

    test_passed = test_pow_operation()

    print("\n" + "=" * 60)
    print("ИТОГ ТЕСТИРОВАНИЯ ЭТАПА 4:")
    print(f" Команда POW: {'ПРОЙДЕН' if test_passed else 'НЕ ПРОЙДЕН'}")

    # Очистка
    if os.path.exists('test_pow.bin'):
        os.remove('test_pow.bin')
        print("Файл test_pow.bin удален")

    if test_passed:
        print(" ЭТАП 4 ВЫПОЛНЕН УСПЕШНО!")
        return 0
    else:
        print("ЭТАП 4 ТРЕБУЕТ ДОРАБОТОК!")
        return 1


if __name__ == "__main__":
    sys.exit(main())