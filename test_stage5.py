#!/usr/bin/env python3
import os
import subprocess
import sys

def run_command(cmd, description):
    print(f" {description}")
    print(f"   Команда: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        return False, error_msg


def test_example(yaml_file, description, mem_range, expected_commands=None):
    print(f"\n{'=' * 60}")
    print(f" ТЕСТ: {description}")
    print(f"{'=' * 60}")

    if not os.path.exists(yaml_file):
        print(f"    Файл {yaml_file} не найден")
        return False

    bin_file = "temp_test.bin"
    dump_file = "temp_test.xml"

    # Ассемблирование
    success, output = run_command([
        sys.executable, 'assembler.py',
        yaml_file,
        bin_file
    ], "Ассемблирование")

    if not success:
        print(f"    {output}")
        return False

    print(f"    {output}")

    # Проверка количества команд если указано
    if expected_commands and output:
        cmd_count = output.split(": ")[-1] if ": " in output else output
        if cmd_count.isdigit() and int(cmd_count) == expected_commands:
            print(f"    Ожидаемое количество команд: {expected_commands}")
        else:
            print(f"   ️  Неожиданное количество команд: {cmd_count} (ожидалось: {expected_commands})")

    # Запуск интерпретатора с диапазоном памяти
    success, output = run_command([
        sys.executable, 'interpreter.py',
        bin_file,
        dump_file,
        '--dump-range', mem_range
    ], "Выполнение программы")

    if not success:
        print(f"    {output}")
        # Очистка
        for f in [bin_file, dump_file]:
            if os.path.exists(f): os.remove(f)
        return False

    print(f"    {output}")

    # Показываем краткий результат из дампа
    if os.path.exists(dump_file):
        print("    Результаты в памяти:")
        try:
            with open(dump_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Ищем не нулевые значения
                lines = [line for line in content.split('\n') if 'value="0"' not in line and 'byte address' in line]
                for line in lines[:10]:  # Показываем первые 10 ненулевых
                    print(f"      {line.strip()}")
                if len(lines) > 10:
                    print(f"      ... и еще {len(lines) - 10} значений")
        except Exception as e:
            print(f"  ️  Не удалось прочитать дамп: {e}")

    # Очистка
    for f in [bin_file, dump_file]:
        if os.path.exists(f): os.remove(f)

    return True


def test_vector_pow():
    print(f"\n{'=' * 60}")
    print(f" Поэлементный POW над векторами")
    print(f"{'=' * 60}")

    yaml_file = 'examples/vector_pow_working.yaml'
    if not os.path.exists(yaml_file):
        print(f" Файл {yaml_file} не найден")
        return False

    bin_file = "vector_test.bin"
    dump_file = "vector_test.xml"

    # Ассемблирование
    success, output = run_command([
        sys.executable, 'assembler.py',
        yaml_file,
        bin_file
    ], "Ассемблирование основной задачи")

    if not success:
        print(f" {output}")
        return False

    print(f" {output}")

    # Запуск интерпретатора с конкретным диапазоном
    success, output = run_command([
        sys.executable, 'interpreter.py',
        bin_file,
        dump_file,
        '--dump-range', '1000-3006'
    ], "Выполнение программы с дампом памяти")

    if not success:
        print(f" {output}")
        # Очистка
        for f in [bin_file, dump_file]:
            if os.path.exists(f): os.remove(f)
        return False

    print(f" {output}")

    # Анализ результатов
    print("\n АНАЛИЗ РЕЗУЛЬТАТОВ:")

    try:
        with open(dump_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Извлекаем значения векторов
        vector_a = []
        vector_b = []
        vector_c = []

        for line in content.split('\n'):
            if 'byte address' in line:
                addr_start = line.find('address="') + 9
                addr_end = line.find('"', addr_start)
                addr = int(line[addr_start:addr_end])

                value_start = line.find('value="') + 7
                value_end = line.find('"', value_start)
                value = int(line[value_start:value_end])

                if 1000 <= addr <= 1006:
                    vector_a.append(value)
                elif 2000 <= addr <= 2006:
                    vector_b.append(value)
                elif 3000 <= addr <= 3006:
                    vector_c.append(value)

        print(f"   Вектор A (основания): {vector_a}")
        print(f"   Вектор B (показатели): {vector_b}")
        print(f"   Вектор C (результаты): {vector_c}")

        # Проверяем вычисления
        expected_results = [
            vector_a[0] ** vector_b[0],  # 2^1 = 2
            vector_a[1] ** vector_b[1],  # 3^2 = 9
            vector_a[2] ** vector_b[2],  # 4^3 = 64
            vector_a[3] ** vector_b[3],  # 5^2 = 25
            vector_a[4] ** vector_b[4],  # 6^1 = 6
            vector_a[5] ** vector_b[5],  # 7^2 = 49
            vector_a[6] ** vector_b[6],  # 8^3 = 512
        ]

        print(f"   Ожидаемые результаты: {expected_results}")

        if vector_c == expected_results:
            print("    ВСЕ ВЫЧИСЛЕНИЯ КОРРЕКТНЫ!")
            success = True
        else:
            print("    Ошибка в вычислениях!")
            success = False

    except Exception as e:
        print(f"    Ошибка анализа: {e}")
        success = False

    # Очистка
    for f in [bin_file, dump_file]:
        if os.path.exists(f): os.remove(f)

    return success


def main():

    print(" ТЕСТИРОВАНИЕ ЭТАПА 5: Выполнение тестовой задачи")
    print("=" * 70)
    # Тестируем три примера программ с правильными диапазонами памяти
    examples = [
        ('examples/simple_calc.yaml', 'Простые арифметические операции', '1000-1005', 7),
        ('examples/copy_array.yaml', 'Копирование массива', '500-600', 14),
        ('examples/pow_simple.yaml', 'Простые вычисления степеней', '1000-3001', 13),
    ]

    success_count = 0
    total_count = len(examples)

    for yaml_file, description, mem_range, expected_cmds in examples:
        if test_example(yaml_file, description, mem_range, expected_cmds):
            success_count += 1
            print("    ТЕСТ ПРОЙДЕН")
        else:
            print("    ТЕСТ ПРОВАЛЕН")

    # Тестируем основную задачу
    if test_vector_pow():
        success_count += 1

    total_count += 1
    print(f"\n{'=' * 70}")
    print(f" ИТОГИ ТЕСТИРОВАНИЯ ЭТАПА 5:")
    print(f"   Пройдено тестов: {success_count}/{total_count}")

    if success_count == total_count:
        print("   ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print("     Некоторые тесты не пройдены")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()