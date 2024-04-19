# csa_lab3

 - Маликов Глеб Игоревич, P3224
 - Вариант: `asm | acc | neum | hw | tick | struct | trap | mem | cstr | prob2`
 - Базовый вариант

## Язык программирования

### Синтаксис

#### Форма Бэкуса-Наура

```
TODO
```

#### Объяснение

#### Пример

```asm
TODO
```

### Семантика


## Организация памяти


## Система команд


### Набор команд

| Команда | Адресная | Ветвление | Количество тактов | Описание                                                               |
|:--------|:---------|-----------|:------------------|:-----------------------------------------------------------------------|
| LOAD    | +        | -         | ?                 | Загрузить значение из заданной ячейки в аккумулятор                    |
| SAVE    | +        | -         | ?                 | Записать значение из аккумулятора в заданную ячейку                    |
| PUSH    | +        | -         | ?                 | Положить значение из аккумулятора на стек                              |
| POP     | +        | -         | ?                 | Вытащить значение из стека в аккумулятор                               |
| INC     | -        | -         | ?                 | Прибавить 1 к значению в аккумуляторе                                  |
| DEC     | -        | -         | ?                 | Вычесть 1 из значения в аккумуляторе                                   |
| ADD     | +        | -         | ?                 | Сложить значение из ячейки с аккумулятором                             |
| SUB     | +        | -         | ?                 | Вычесть значение ячейки из аккумулятора                                |
| MUL     | +        | -         | ?                 | Умножить значение аккумулятора на значение из ячейки                   |
| DIV     | +        | -         | ?                 | Разделить значение аккумулятора на значение из ячейки                  |
| CMP     | +        | -         | ?                 | Сравнить значение аккумулятора с значением из ячейки                   |
| JMP     | +        | -         | ?                 | Перейти к заданной ячейке                                              |
| SHL     | -        | -         | ?                 | Сдвинуть значение в аккумуляторе влево, AC[15] -> C                    |
| SHR     | -        | -         | ?                 | Сдвинуть значение в аккумуляторе вправо, AC[0] -> C                    |
| JMN     | +        | +         | ?                 | Перейти в заданную ячейку если значение в аккумуляторе отрицательное   |
| JMNN    | +        | +         | ?                 | Перейти в заданную ячейку если значение в аккумуляторе неотрицательное |
| JMZ     | +        | +         | ?                 | Перейти в заданную ячейку если значение в аккумуляторе равно нулю      |
| JMZN    | +        | +         | ?                 | Перейти в заданную ячейку если значение в аккумуляторе не равно нулю   |
| JMC     | +        | +         | ?                 | Перейти в заданную ячейку если установлен флаг переноса                |
| JMNC    | +        | +         | ?                 | Перейти в заданную ячейку если флаг переноса не установлен             |
| CLR     | -        | -         | ?                 | Очистить аккумулятор (записать в него 0)                               |
| HLT     | -        | -         | ?                 | Остановить работу программы                                            |
| IRET    | -        | -         | ?                 | Вернуться из прерывания                                                |

### Кодирование команд


## Транслятор

Интерфейс командной строки: `translator.py <input_file> <target_file>`

Реализовано в модуле [translator.py](./translator.py).

## Модель процессора

Интерфейс командной строки: `machine.py <code_file> <input_file>`

Реализовано в модуле [machine.py](./machine.py).

### DataPath


### ControlUnit


## Тестирование