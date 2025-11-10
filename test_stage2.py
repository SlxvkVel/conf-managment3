import os
from assembler import Assembler

def test_combined_program():
    print(" ТЕСТ ЭТАПА 2")
    
    assembler = Assembler()
    
    try:
        # Загружаем комбинированную программу
        program = assembler.load_program('examples/all_commands.yaml')
        binary_code, intermediate_repr = assembler.assemble(program)
        
        # Проверяем ожидаемые байты из спецификации
        expected_bytes = [
            # LOAD: 0x06, 0x26, 0xa8
            0x06, 0x26, 0xa8,
            # READ: 0x96, 0xab, 0xc7
            0x96, 0xab, 0xc7,
            # WRITE: 0x1a, 0xe4, 0x7f
            0x1a, 0xe4, 0x7f,
            # POW: 0x2a, 0x2a, 0xd6, 0x01, 0x00, 0x00
            0x2a, 0x2a, 0xd6, 0x01, 0x00, 0x00
        ]
        
        actual_bytes = list(binary_code)
        actual_hex = [f"0x{byte:02x}" for byte in actual_bytes]
        expected_hex = [f"0x{byte:02x}" for byte in expected_bytes]
        
        print(f" Сгенерировано: {actual_hex}")
        print(f" Ожидалось:    {expected_hex}")
        
        if actual_bytes == expected_bytes:
            print("ВСЕ ТЕСТОВЫЕ ПОСЛЕДОВАТЕЛЬНОСТИ СОВПАДАЮТ!")
            print(f" Ассемблировано команд: {len(intermediate_repr)}")
            print(f" Всего байт: {len(binary_code)}")
            return True
        else:
            print(" ТЕСТ НЕ ПРОЙДЕН!")
            return False
            
    except Exception as e:
        print(f" ОШИБКА: {e}")
        return False

def test_binary_output():
    print("\n ТЕСТ ЗАПИСИ В ДВОИЧНЫЙ ФАЙЛ")
    assembler = Assembler()
    
    try:
        # Ассемблируем и сохраняем
        program = assembler.load_program('examples/all_commands.yaml')
        binary_code, intermediate_repr = assembler.assemble(program)
        assembler.save_binary(binary_code, 'test_output.bin')
        
        # Проверяем что файл создан и имеет правильный размер
        if os.path.exists('test_output.bin'):
            file_size = os.path.getsize('test_output.bin')
            expected_size = len(binary_code)
            
            print(f" Файл создан: test_output.bin")
            print(f" Размер файла: {file_size} байт")
            print(f" Ожидаемый размер: {expected_size} байт")
            
            if file_size == expected_size:
                print(" РАЗМЕР ФАЙЛА СООТВЕТСТВУЕТ!")
                return True
            else:
                print(" РАЗМЕР ФАЙЛА НЕ СОВПАДАЕТ!")
                return False
        else:
            print(" ФАЙЛ НЕ СОЗДАН!")
            return False
            
    except Exception as e:
        print(f" ОШИБКА: {e}")
        return False

def main():
    print("ТЕСТИРОВАНИЕ ЭТАПА 2: ФОРМИРОВАНИЕ МАШИННОГО КОДА")
    print("=" * 60)
    
    test1_passed = test_combined_program()
    test2_passed = test_binary_output()

    print("ИТОГ ТЕСТИРОВАНИЯ ЭТАПА 2:")
    print(f" Комбинированная программа: {'ПРОЙДЕН' if test1_passed else 'НЕ ПРОЙДЕН'}")
    print(f" Запись в двоичный файл: {'ПРОЙДЕН' if test2_passed else 'НЕ ПРОЙДЕН'}")
    
    # Очистка
    if os.path.exists('test_output.bin'):
        os.remove('test_output.bin')
    
    if test1_passed and test2_passed:
        print(" ЭТАП 2 ВЫПОЛНЕН УСПЕШНО!")
    else:
        print(" ЭТАП 2 ТРЕБУЕТ ДОРАБОТОК!")

if __name__ == "__main__":
    main()