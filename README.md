
# Ассемблер для Учебной Виртуальной Машины (УВМ)

## Язык ассемблера

Программы для УВМ пишутся в формате YAML. Каждая программа - это список команд.

### Команды:

#### LOAD - Загрузка константы
Загружает число в регистр.

```yaml
- command: load
  constant: число    # от 0 до 8191
  address: число     # от 0 до 31 (номер регистра)
```

**Пример:**
```yaml
- command: load
  constant: 152
  address: 21
```

#### READ - Чтение из памяти
Читает значение из памяти в регистр.

```yaml
- command: read
  address_reg: число  # регистр с адресом (0-31)
  offset: число       # смещение (0-255)
  result_reg: число   # регистр для результата (0-31)
```

**Пример:**
```yaml
- command: read
  address_reg: 24
  offset: 245
  result_reg: 14
```

#### WRITE - Запись в память
Записывает значение из регистра в память.

```yaml
- command: write
  value_reg: число    # регистр с данными (0-31)
  address_reg: число  # регистр с адресом (0-31)
  offset: число       # смещение (0-255)
```

**Пример:**
```yaml
- command: write
  value_reg: 16
  address_reg: 28
  offset: 127
```

#### POW - Возведение в степень
Вычисляет степень и сохраняет результат.

```yaml
- command: pow
  value1_addr: число  # адрес в памяти (0-67108863)
  value2_reg: число   # регистр с показателем (0-31)
  result_reg: число   # регистр для результата (0-31)
```

**Пример:**
```yaml
- command: pow
  value1_addr: 470
  value2_reg: 8
  result_reg: 5
```

## Использование

### Обычный режим:
```bash
python assembler.py program.yaml output.bin
```

### Режим тестирования:
```bash
python assembler.py program.yaml output.bin --test
```

В режиме тестирования показывается промежуточное представление программы с полями и байтами.

## Пример программы

```yaml
- command: load
  constant: 100
  address: 1

- command: write
  value_reg: 1
  address_reg: 2
  offset: 50

- command: read
  address_reg: 2
  offset: 50
  result_reg: 3

- command: pow
  value1_addr: 200
  value2_reg: 3
  result_reg: 4
```
