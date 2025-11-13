import os
import xml.etree.ElementTree as ET
from assembler import Assembler
from interpreter import UVMInterpreter


def test_array_copy():
    print(" ТЕСТ ЭТАПА 3: Копирование массива")
    print("=" * 60)

    assembler = Assembler()
    program = assembler.load_program('examples/array_copy.yaml')
    binary_code, _ = assembler.assemble(program)

    with open('test_array.bin', 'wb') as f:
        f.write(bytes(binary_code))

    interpreter = UVMInterpreter()
    interpreter.load_program('test_array.bin')

    interpreter.pc = 0
    command_count = 0
    max_commands = 50

    while interpreter.pc < len(interpreter.memory) and command_count < max_commands:
        try:
            command_type, params = interpreter.decode_command()
            if command_type is None:
                break
            interpreter.execute_command(command_type, params)
            command_count += 1
        except Exception as e:
            print(f"Ошибка: {e}")
            break

    print("\nПроверка копирования массива:")
    source_data = interpreter.memory[1000:1003]  # 1000, 1001, 1002
    dest_data = interpreter.memory[2000:2003]    # 2000, 2001, 2002

    print(f"Исходный массив (1000-1002): {source_data}")
    print(f"Скопированный массив (2000-2002): {dest_data}")

    interpreter.create_memory_dump(1000, 2002, 'memory_dump.xml')

    if source_data == dest_data:
        print(" МАССИВ УСПЕШНО СКОПИРОВАН!")
        return True
    else:
        print(" ОШИБКА КОПИРОВАНИЯ МАССИВА!")
        return False


def test_xml_dump():
    print("\n ТЕСТ XML ДАМПА")
    print("=" * 60)

    if os.path.exists('memory_dump.xml'):
        tree = ET.parse('memory_dump.xml')
        root = tree.getroot()

        print(f"Корневой элемент: {root.tag}")
        print(f"Диапазон адресов: {root.get('start')}-{root.get('end')}")

        bytes_count = len(root.findall('byte'))
        print(f"Количество байт в дампе: {bytes_count}")

        print("\nПримеры данных из дампа:")
        for i, byte_elem in enumerate(root.findall('byte')[:5]):
            print(f"  Адрес {byte_elem.get('address')}: {byte_elem.text}")

        print(" XML ДАМП СОЗДАН КОРРЕКТНО!")
        return True
    else:
        print(" ФАЙЛ ДАМПА НЕ СОЗДАН!")
        return False


def main():
    print("ТЕСТИРОВАНИЕ ЭТАПА 3: ИНТЕРПРЕТАТОР И ПАМЯТЬ")
    print("=" * 60)

    test1_passed = test_array_copy()
    test2_passed = test_xml_dump()

    print("\n" + "=" * 60)
    print("ИТОГ ТЕСТИРОВАНИЯ ЭТАПА 3:")
    print(f"Копирование массива: {'ПРОЙДЕН' if test1_passed else 'НЕ ПРОЙДЕН'}")
    print(f" XML дамп памяти: {'ПРОЙДЕН' if test2_passed else 'НЕ ПРОЙДЕН'}")

    for file in ['test_array.bin', 'memory_dump.xml']:
        if os.path.exists(file):
            os.remove(file)

    if test1_passed and test2_passed:
        print(" ЭТАП 3 ВЫПОЛНЕН УСПЕШНО!")
    else:
        print(" ЭТАП 3 ТРЕБУЕТ ДОРАБОТОК!")


if __name__ == "__main__":
    main()