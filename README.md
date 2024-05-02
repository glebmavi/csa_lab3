# csa_lab3

 - Маликов Глеб Игоревич, P3224
 - Вариант: `asm | acc | neum | hw | tick | struct | trap | mem | cstr | prob2`
 - Базовый вариант

## Язык программирования

### Синтаксис

#### Форма Бэкуса-Наура

```enbf
<программа> ::=
    "section .data" <перенос строки> {<данные> | <индекс>} <перенос строки>
    "section .code" <перенос строки> {<инструкция> | <метка> | <индекс>} <перенос строки> <EOF>
    
<данные> ::= <метка переменной> ":" <переменная> [комментарий] <перенос строки>
<инструкция> ::= <адресная команда> <операнд> [комментарий] <перенос строки> | <безадресная команда> [комментарий] <перенос строки> | <команда перехода> <метка перехода> [комментарий] <перенос строки>
<метка> ::= <идентификатор> ":" [комментарий] <перенос строки>
<индекс> ::= "index" <число> [комментарий] <перенос строки>

<команда перехода> ::= "JMP" | "JMN" | "JMNN" | "JMZ" | "JMNZ" | "JMC" | "JMNC"
<адресная команда> ::= "LOAD" | "SAVE" | "ADD" | "SUB" | "CMP" 
<безадресная команда> ::= "INC" | "DEC" | "SHL" | "SHR" | "CLR" | "HLT" | "IRET" | "NOP"
<операнд> ::= <число> | <метка переменной> | "$" <метка переменной>
<метка перехода> ::= <идентификатор> | <число>

<метка переменной> ::= <слово>
<переменная> ::= <число> | "'"<слово>"'"

<идентификатор> ::= "_"<слово>
<комментарий> ::= ";" {<слово> | <число>}

<перенос строки> ::= "\n"
<слово> ::= <буква> {<буква>}
<число> ::= ["-"]<цифра> {<цифра>}
<буква> ::= a | b | c | ... | z | A | B | C | ... | Z
<цифра> ::= 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
```

#### Объяснение

Вся программа описывается в виде двух секций: `.data` и `.code`.
 - В секции `.data` описываются переменные, которые могут использоваться в секции `.code`.
 - В секции `.code` описываются инструкции, которые выполняются процессором.

Каждая непустая строка программы это одно из нижеперечисленных:
 - Переменная: 
   - Может быть числом или строкой.
   - Строка заключается в одинарные кавычки.
   - Указывается значение посредством `:` после названия переменной.
 - Инструкция:
   - Команда может быть адресной или безадресной.
   - Состоит из команды и в случае адресной команды - операнда.
   - Операнд может быть числом, меткой переменной или меткой инструкции.
   - Команда должна быть записана в верхнем регистре.
 - Метка:
   - Используется для обозначения места в коде, к которому можно выполнить переход.
   - Метка должна начинаться с символа `_`.
 - Индекс:
   - Используется для обозначения ячейки памяти, в которую записываются последующие инструкции и данные.
   - Указывается ключевое слово `index` и число через пробел.
 - Адрес:
   - Указывается название переменной.
   - Если требуется ввод или вывод с устройства, то можно использовать параметры `IN`, `OUT`.
   - Может указываться название переменной с префиксом `$` для косвенной адресации.
   - Может указываться число как адрес.

#### Пример

Пример программы, вычисляющей С = A + B:

```asm
section .data
index 0
A: 5
B: 3
C: 0

section .code
index 100
_start
    LOAD A
    ADD B
    SAVE C
    HLT
```

### Семантика

- Видимость данных -- глобальная.
- Поддерживаются целочисленные литералы, находящиеся в диапазоне от $-2^{31}$ до $2^{31}-1$.
- Поддерживаются строковые литералы, символы стоки необходимо заключить в одинарные кавычки.
- Код выполняется последовательно.
- Программа обязательно должна включать метку `_start`, указывающую на 1-ю выполняемую инструкцию.
- Название метки не должно совпадать с названием команды и не может начинаться с цифры.
- Переменные и метки не могут повторяться.
- Переменные должны быть объявлены только в секции `.data`.
- Метки должны быть объявлены только в секции `.code` и должны начинаться с символа `_`.
- Все числа в программе должны быть записаны в десятичной системе счисления.
- Метки должны быть объявлены до их использования.
- Пустые строки игнорируются, количество пробелов в начале и конце строки не влияет на работу программы.
- Любой текст, расположенный в конце строки после символа `;` трактуется как комментарий.


## Организация памяти

 - Память команд и данныx -- общая, в соответствии с моделью фон Неймана 
 - Размер машинного слова -- `32` бит 
 - Память содержит `2^11` ячеек
 - Адрес `2044` является указателем стека при старте процессора. Стек растет вверх.
 - Адрес `2045` является вектором прерываний. При возникновении прерывания процессор переходит к выполнению инструкции по адресу, указанному в этой ячейке.
 - Адрес `2046` является адресом ввода.
 - Адрес `2047` является адресом вывода.

```
            memory
+----------------------------+
| 00 :      ...              |
|     variables and code     |
|           ...              |
| 2043 : Stack Start         |
| 2044 : Interrupt Return    |
| 2045 : Interrupt Start     |
| 2046 : Input Address       |
| 2047 : Output Address      |
+----------------------------+
```

 - Поддерживаются следующие виды адресаций:
   - Прямая адресация: `LOAD A` - загружает значение из ячейки памяти с адресом `A` в аккумулятор. Например, `A: 5` - загружает значение `5`.
   - Косвенная адресация: `LOAD $A` - загружает значение из ячейки памяти с адресом, хранящимся в ячейке памяти с адресом `A` в аккумулятор. Например, `A: 5`, `index 5 \n B: 10`, `LOAD $A` - загружает значение `10` в аккумулятор.
 - Регистры:
   - Аккумулятор (ACC) -- хранит результаты вычислений.
   - Регистр адреса (AR) -- хранит адрес ячейки памяти.
   - Счетчик инструкций (IP) -- хранит адрес следующей инструкции.
   - Регистр данных (DR) -- хранит данные для передачи в память.
   - Указатель стека (SP) -- хранит адрес вершины стека.
   - Регистр команд (CR) -- хранит текущую инструкцию.
   - Регистр состояния (PS) -- хранит флаги состояния процессора в виде битов:
     - `N` - флаг отрицательности
     - `Z` - флаг нуля
     - `C` - флаг переноса
     - Биты расположены в следующем порядке: `N`, `Z`, `C`


## Система команд

Особенности процессора:

- Машинное слово -- `32` бита, знаковое.
- В качестве аргументов команды принимают `11` битные беззнаковые адреса ячеек памяти.

Работа каждой инструкции выполняется в нескольких тактах:
 - Чтение команды из памяти (2 такта):
   - Счетчик команд (IP) указывает на адрес в памяти, откуда следует выбрать команду. Значение из этого адреса загружается в регистр команд (CR).
   - `IP -> AR, mem[IP] -> CR, IP + 1 -> IP` 
 - Чтение операндов из памяти (если требуется):
   - Адрес операнда из регистра команд (CR) загружается в регистр данных (DR), который затем передается в регистр адреса (AR). Значение из этого адреса в памяти загружается обратно в регистр данных (DR).
   - 2 такта
   - `CR[addr] -> AR, mem[AR] -> DR`
   - Если читается относительный адрес, то выполняется еще одно чтение операнда. +2 такта
   - `DR -> AR, mem[AR] -> DR`
 - Выполнение операции:
   - Производятся действия необходимые для выполнения команды. Результат сохраняется в аккумуляторе (AC).
 - Проверка прерываний:
   - Если установлен флаг прерывания, то происходит переход к обработке прерывания.


### Набор команд

| Команда | Адресная | Ветвление | Количество тактов<br/>(Включая чтение команды и операнда) | Описание                                                               |
|:--------|:---------|-----------|:----------------------------------------------------------|:-----------------------------------------------------------------------|
| LOAD    | +        | -         | 5 (+2 для относительного адреса)                          | Загрузить значение из заданной ячейки в аккумулятор                    |
| SAVE    | +        | -         | 5 (+2 для относительного адреса)                          | Записать значение из аккумулятора в заданную ячейку                    |
| PUSH    | -        | -         | 4                                                         | Положить значение из аккумулятора на стек                              |
| POP     | -        | -         | 4                                                         | Вытащить значение из стека в аккумулятор                               |
| INC     | -        | -         | 3                                                         | Прибавить 1 к значению в аккумуляторе                                  |
| DEC     | -        | -         | 3                                                         | Вычесть 1 из значения в аккумуляторе                                   |
| ADD     | +        | -         | 5 (+2 для относительного адреса)                          | Сложить значение из ячейки с аккумулятором                             |
| SUB     | +        | -         | 5 (+2 для относительного адреса)                          | Вычесть значение ячейки из аккумулятора                                |
| CMP     | +        | -         | 5 (+2 для относительного адреса)                          | Сравнить значение аккумулятора с значением из ячейки                   |
| JMP     | +        | -         | 5                                                         | Перейти к заданной ячейке                                              |
| SHL     | -        | -         | 3                                                         | Сдвинуть значение в аккумуляторе влево, AC[15] -> C                    |
| SHR     | -        | -         | 3                                                         | Сдвинуть значение в аккумуляторе вправо, AC[0] -> C                    |
| JMN     | +        | +         | 5                                                         | Перейти в заданную ячейку если значение в аккумуляторе отрицательное   |
| JMNN    | +        | +         | 5                                                         | Перейти в заданную ячейку если значение в аккумуляторе неотрицательное |
| JMZ     | +        | +         | 5                                                         | Перейти в заданную ячейку если значение в аккумуляторе равно нулю      |
| JMNZ    | +        | +         | 5                                                         | Перейти в заданную ячейку если значение в аккумуляторе не равно нулю   |
| JMC     | +        | +         | 5                                                         | Перейти в заданную ячейку если установлен флаг переноса                |
| JMNC    | +        | +         | 5                                                         | Перейти в заданную ячейку если флаг переноса не установлен             |
| CLR     | -        | -         | 3                                                         | Очистить аккумулятор (записать в него 0)                               |
| HLT     | -        | -         | 3                                                         | Остановить работу программы                                            |
| IRET    | -        | -         | 3                                                         | Вернуться из прерывания                                                |
| NOP     | -        | -         | 3                                                         | Нет операции                                                           |

### Кодирование команд

 - Команды сериализуются в список JSON
 - Каждая команда представляется объектом с полями:
    - `index` - ячейка памяти
    - `opcode` - код операции. Для записи констант используется `NOP`
    - `value` - значение операнда. Для команд без операндов используется 0
    - `relative` - указывает если команда использует относительный адрес.

Пример сериализации команд:

 - Исходный код:
```asm
section .data
loc: 30
asdf: 2
result: 0
index 30
A: 5

section .code
_start
    LOAD $loc
    ADD asdf
    SAVE result
    HLT
```
 - Сериализованный код:
```json
[
{"start_address": 31 },
{"index": 0, "opcode": "NOP", "value": 30},
{"index": 1, "opcode": "NOP", "value": 2},
{"index": 2, "opcode": "NOP", "value": 0},
{"index": 30, "opcode": "NOP", "value": 5},
{"index": 31, "opcode": "LOAD", "value": 0, "relative": true},
{"index": 32, "opcode": "ADD", "value": 1, "relative": false},
{"index": 33, "opcode": "SAVE", "value": 2, "relative": false},
{"index": 34, "opcode": "HLT", "value": 0}
]
```

## Транслятор

Интерфейс командной строки: `translator.py <source_file> <target_file>`

Реализован в модуле [translator.py](./translator.py).

Этапы работы транслятора:
1. Чтение исходного файла: Транслятор сначала открывает исходный файл и читает его содержимое. Каждая строка кода считывается и сохраняется в списке.
2. Обработка комментариев и пустых строк (`trimmer`): Транслятор затем обрабатывает каждую строку, удаляя комментарии и пропуская пустые строки.
3. Разделение на секции (`section_split`): Код разделяется на две секции: .data и .code. Секция .data содержит объявления переменных, а секция .code содержит инструкции.
4. Обработка секции данных (`build_data`): В секции данных транслятор обрабатывает каждую строку, определяя тип данных (число или строка) и сохраняя его в соответствующие инструкции.
5. Обработка секции кода (`build_code`): В секции кода транслятор обрабатывает каждую строку, определяя тип инструкции и ее операнды. Он также обрабатывает метки, сохраняя их адреса для последующего использования.
6. Сериализация (`json_builder`): После обработки всего кода, транслятор сериализует результат в формат JSON и записывает его в целевой файл.

Правила трансляции:
 - Одна переменная - одна строка. 
 - Одна команда - одна строка. 
 - Метки пишутся в отдельной строке. 
 - Названия секций пишутся в отдельной строке. 
 - Ссылаться можно только на существующие переменные и метки.


## Модель процессора

Интерфейс командной строки: `machine.py <code_file> <input_file>`

Реализован в модуле [machine.py](./machine.py).

### DataPath

Реализован в модуле [data_path.py](data_path.py).

![data_path.drawio.svg](schemes/data_path.drawio.svg)
Синим цветом указаны сигналы, которые из ALU, для удобства отображения.

Класс `data_path` реализует управление памятью и регистрами процессора.
 - `fetch_instruction`: Загружает инструкцию из памяти. Счетчик команд (IP) указывает на адрес в памяти, откуда следует выбрать команду. Значение из этого адреса загружается в регистр команд (CR).
 - `read_operand` : Читает операнд из памяти. Адрес операнда из регистра команд (CR) загружается в регистр данных (DR), который затем передается в регистр адреса (AR). Значение из этого адреса в памяти загружается обратно в регистр данных (DR).

`data_path` также имеет экземпляр класса `ALU`, который реализует арифметическо-логическое устройство процессора.
 - `set_flags`: Устанавливает флаги N, Z и C на основе результата операции.
 - `get_flags_as_int`: Конвертирует флаги N, Z и C в одно целое число, для регистра состояния процессора.

### ControlUnit

Реализован в модуле [control_unit.py](control_unit.py).

![control_unit.drawio.svg](schemes/control_unit.drawio.svg)

Класс `control_unit` реализует управление процессором.
 - `load_program`: Загружает программу в память, устанавливая адреса начала программы и программы прерываний.
 - `tick`: Увеличивает счетчик тактов и проверяет наличие входных данных.
 - `instruction_step`: Выполняет один шаг инструкции, включая чтение инструкции из памяти, чтение операндов (если требуется) и выполнение операции.
 - `run`: Запускает выполнение программы до возникновения прерывания.
 - `execute_instruction`: Выполняет текущую инструкцию, указанную в регистре команд.

Особенности работы модели:
 - Цикл симуляции осуществляется в функции `run`.
 - Шаг моделирования соответствует одному такту процессора с выводом состояния в журнал.
 - Для журнала состояний процессора используется стандартный модуль `logging`.
 - Количество тактов для моделирования лимитировано.
 - Проверка прерываний осуществляется после каждого запуска `instruction_step`.
 - Остановка моделирования осуществляется при:
   - установлении в любом месте программы `self.interrupt = InterruptType.ERROR`
   - достижении лимита тактов
   - выполнении инструкции `HLT`


## Тестирование
 - Тестирование осуществляется при помощи golden test-ов.
 - Настройка golden тестирования находится в [модуле](./golden_test.py).
 - Конфигурация golden test-ов лежит в [директории](./golden).

Реализованные тесты
1. [cat](./examples/asm/cat.asmm) - Программа, копирующая ввод в вывод.
2. [hello user](./examples/asm/hellouser.asmm) - Программа ожидает имени пользователя и выводит приветствие.
3. [hello world](./examples/asm/helloworld.asmm) - Программа выводит "Hello, World!".
4. [prob2](./examples/asm/prob2.asmm) - Программа находит сумму всех четных чисел Фибоначчи, не превышающих `4 000 000`.

CI при помощи Github Actions:

```
name: csa_lab3

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.12

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry
          poetry install

      - name: Run tests and collect coverage
        run: |
          poetry run coverage run -m pytest .
          poetry run coverage report -m
        env:
          CI: true

  lint:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.12

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry
          poetry install

      - name: Check code formatting with Ruff
        run: poetry run ruff format --check .

      - name: Run Ruff linters
        run: poetry run ruff check .
```

где:
 - `test` - запускает тесты и собирает покрытие кода.
 - `lint` - проверяет форматирование кода и запускает линтеры.

Пример использования и журнал работы процессора на примере программы [sum](./examples/asm/sum.asmm):

```
> ./translator.py ./examples/asm/sum.asmm ./examples/build/sum.asmx
source LoC: 22 code instr: 10
> ./machine.py ./examples/build/sum.asmx ./examples/input/noinput.txt
INFO    control_unit:__print__     Tick:     0 |Action: Fetch instruction (IP -> AR, mem[IP] -> CR)                  |Interrupt: none  |ACC:          0 |AR:   100 |IP:   101 |DR: 0                                                                             |SP:  2043 |CR: OpCode: LOAD, Value:         10, Relative: False      |PS:  2
INFO    control_unit:__print__     Tick:     1 |Action: Fetch Instruction (IP + 1 -> IP)                             |Interrupt: none  |ACC:          0 |AR:   100 |IP:   101 |DR: 0                                                                             |SP:  2043 |CR: OpCode: LOAD, Value:         10, Relative: False      |PS:  2
INFO    control_unit:__print__     Tick:     2 |Action: Read operand (CR[addr] -> AR)                                |Interrupt: none  |ACC:          0 |AR:    10 |IP:   101 |DR: "index":   10, "opcode": "NOP ", "value":          5                          |SP:  2043 |CR: OpCode: LOAD, Value:         10, Relative: False      |PS:  2
INFO    control_unit:__print__     Tick:     3 |Action: Read operand (mem[AR] -> DR)                                 |Interrupt: none  |ACC:          0 |AR:    10 |IP:   101 |DR: "index":   10, "opcode": "NOP ", "value":          5                          |SP:  2043 |CR: OpCode: LOAD, Value:         10, Relative: False      |PS:  2
INFO    control_unit:__print__     Tick:     4 |Action: Execute instruction (LOAD: DR -> ACC, PS)                    |Interrupt: none  |ACC:          5 |AR:    10 |IP:   101 |DR: "index":   10, "opcode": "NOP ", "value":          5                          |SP:  2043 |CR: OpCode: LOAD, Value:         10, Relative: False      |PS:  0
INFO    control_unit:__print__     Tick:     5 |Action: Fetch instruction (IP -> AR, mem[IP] -> CR)                  |Interrupt: none  |ACC:          5 |AR:   101 |IP:   102 |DR: "index":   10, "opcode": "NOP ", "value":          5                          |SP:  2043 |CR: OpCode: ADD , Value:         11, Relative: True       |PS:  0
INFO    control_unit:__print__     Tick:     6 |Action: Fetch Instruction (IP + 1 -> IP)                             |Interrupt: none  |ACC:          5 |AR:   101 |IP:   102 |DR: "index":   10, "opcode": "NOP ", "value":          5                          |SP:  2043 |CR: OpCode: ADD , Value:         11, Relative: True       |PS:  0
INFO    control_unit:__print__     Tick:     7 |Action: Read operand (CR[addr] -> AR)                                |Interrupt: none  |ACC:          5 |AR:    10 |IP:   102 |DR: "index":   10, "opcode": "NOP ", "value":          5                          |SP:  2043 |CR: OpCode: ADD , Value:         11, Relative: True       |PS:  0
INFO    control_unit:__print__     Tick:     8 |Action: Read operand (mem[AR] -> DR)                                 |Interrupt: none  |ACC:          5 |AR:    10 |IP:   102 |DR: "index":   10, "opcode": "NOP ", "value":          5                          |SP:  2043 |CR: OpCode: ADD , Value:         11, Relative: True       |PS:  0
INFO    control_unit:__print__     Tick:     9 |Action: Read operand (Relative addressing: DR -> AR)                 |Interrupt: none  |ACC:          5 |AR:    10 |IP:   102 |DR: "index":   10, "opcode": "NOP ", "value":          5                          |SP:  2043 |CR: OpCode: ADD , Value:         11, Relative: True       |PS:  0
INFO    control_unit:__print__     Tick:    10 |Action: Read operand (mem[AR] -> DR)                                 |Interrupt: none  |ACC:          5 |AR:    10 |IP:   102 |DR: "index":   10, "opcode": "NOP ", "value":          5                          |SP:  2043 |CR: OpCode: ADD , Value:         11, Relative: True       |PS:  0
INFO    control_unit:__print__     Tick:    11 |Action: Execute instruction (ADD: ACC + DR -> ACC, PS)               |Interrupt: none  |ACC:         10 |AR:    10 |IP:   102 |DR: "index":   10, "opcode": "NOP ", "value":          5                          |SP:  2043 |CR: OpCode: ADD , Value:         11, Relative: True       |PS:  0
INFO    control_unit:__print__     Tick:    12 |Action: Fetch instruction (IP -> AR, mem[IP] -> CR)                  |Interrupt: none  |ACC:         10 |AR:   102 |IP:   103 |DR: "index":   10, "opcode": "NOP ", "value":          5                          |SP:  2043 |CR: OpCode: SAVE, Value:         12, Relative: False      |PS:  0
INFO    control_unit:__print__     Tick:    13 |Action: Fetch Instruction (IP + 1 -> IP)                             |Interrupt: none  |ACC:         10 |AR:   102 |IP:   103 |DR: "index":   10, "opcode": "NOP ", "value":          5                          |SP:  2043 |CR: OpCode: SAVE, Value:         12, Relative: False      |PS:  0
INFO    control_unit:__print__     Tick:    14 |Action: Read operand (CR[addr] -> AR)                                |Interrupt: none  |ACC:         10 |AR:    12 |IP:   103 |DR: "index":   12, "opcode": "NOP ", "value":          0                          |SP:  2043 |CR: OpCode: SAVE, Value:         12, Relative: False      |PS:  0
INFO    control_unit:__print__     Tick:    15 |Action: Read operand (mem[AR] -> DR)                                 |Interrupt: none  |ACC:         10 |AR:    12 |IP:   103 |DR: "index":   12, "opcode": "NOP ", "value":          0                          |SP:  2043 |CR: OpCode: SAVE, Value:         12, Relative: False      |PS:  0
INFO    control_unit:__print__     Tick:    16 |Action: Execute instruction (SAVE: ACC -> mem[AR])                   |Interrupt: none  |ACC:         10 |AR:    12 |IP:   103 |DR: "index":   12, "opcode": "NOP ", "value":          0                          |SP:  2043 |CR: OpCode: SAVE, Value:         12, Relative: False      |PS:  0
INFO    control_unit:__print__     Tick:    17 |Action: Fetch instruction (IP -> AR, mem[IP] -> CR)                  |Interrupt: none  |ACC:         10 |AR:   103 |IP:   104 |DR: "index":   12, "opcode": "NOP ", "value":          0                          |SP:  2043 |CR: OpCode: JMP , Value:         13, Relative: None       |PS:  0
INFO    control_unit:__print__     Tick:    18 |Action: Fetch Instruction (IP + 1 -> IP)                             |Interrupt: none  |ACC:         10 |AR:   103 |IP:   104 |DR: "index":   12, "opcode": "NOP ", "value":          0                          |SP:  2043 |CR: OpCode: JMP , Value:         13, Relative: None       |PS:  0
INFO    control_unit:__print__     Tick:    19 |Action: Read operand (CR[addr] -> AR)                                |Interrupt: none  |ACC:         10 |AR:    13 |IP:   104 |DR: "index":   13, "opcode": "LOAD", "value":         12, "relative": False       |SP:  2043 |CR: OpCode: JMP , Value:         13, Relative: None       |PS:  0
INFO    control_unit:__print__     Tick:    20 |Action: Read operand (mem[AR] -> DR)                                 |Interrupt: none  |ACC:         10 |AR:    13 |IP:   104 |DR: "index":   13, "opcode": "LOAD", "value":         12, "relative": False       |SP:  2043 |CR: OpCode: JMP , Value:         13, Relative: None       |PS:  0
INFO    control_unit:__print__     Tick:    21 |Action: Execute instruction (JMP: DR -> IP)                          |Interrupt: none  |ACC:         10 |AR:    13 |IP:    13 |DR: "index":   13, "opcode": "LOAD", "value":         12, "relative": False       |SP:  2043 |CR: OpCode: JMP , Value:         13, Relative: None       |PS:  0
INFO    control_unit:__print__     Tick:    22 |Action: Fetch instruction (IP -> AR, mem[IP] -> CR)                  |Interrupt: none  |ACC:         10 |AR:    13 |IP:    14 |DR: "index":   13, "opcode": "LOAD", "value":         12, "relative": False       |SP:  2043 |CR: OpCode: LOAD, Value:         12, Relative: False      |PS:  0
INFO    control_unit:__print__     Tick:    23 |Action: Fetch Instruction (IP + 1 -> IP)                             |Interrupt: none  |ACC:         10 |AR:    13 |IP:    14 |DR: "index":   13, "opcode": "LOAD", "value":         12, "relative": False       |SP:  2043 |CR: OpCode: LOAD, Value:         12, Relative: False      |PS:  0
INFO    control_unit:__print__     Tick:    24 |Action: Read operand (CR[addr] -> AR)                                |Interrupt: none  |ACC:         10 |AR:    12 |IP:    14 |DR: "index":   12, "opcode": "NOP ", "value":         10                          |SP:  2043 |CR: OpCode: LOAD, Value:         12, Relative: False      |PS:  0
INFO    control_unit:__print__     Tick:    25 |Action: Read operand (mem[AR] -> DR)                                 |Interrupt: none  |ACC:         10 |AR:    12 |IP:    14 |DR: "index":   12, "opcode": "NOP ", "value":         10                          |SP:  2043 |CR: OpCode: LOAD, Value:         12, Relative: False      |PS:  0
INFO    control_unit:__print__     Tick:    26 |Action: Execute instruction (LOAD: DR -> ACC, PS)                    |Interrupt: none  |ACC:         10 |AR:    12 |IP:    14 |DR: "index":   12, "opcode": "NOP ", "value":         10                          |SP:  2043 |CR: OpCode: LOAD, Value:         12, Relative: False      |PS:  0
INFO    control_unit:__print__     Tick:    27 |Action: Fetch instruction (IP -> AR, mem[IP] -> CR)                  |Interrupt: none  |ACC:         10 |AR:    14 |IP:    15 |DR: "index":   12, "opcode": "NOP ", "value":         10                          |SP:  2043 |CR: OpCode: SAVE, Value:       2047, Relative: False      |PS:  0
INFO    control_unit:__print__     Tick:    28 |Action: Fetch Instruction (IP + 1 -> IP)                             |Interrupt: none  |ACC:         10 |AR:    14 |IP:    15 |DR: "index":   12, "opcode": "NOP ", "value":         10                          |SP:  2043 |CR: OpCode: SAVE, Value:       2047, Relative: False      |PS:  0
INFO    control_unit:__print__     Tick:    29 |Action: Read operand (CR[addr] -> AR)                                |Interrupt: none  |ACC:         10 |AR:  2047 |IP:    15 |DR: "index": 2047, "opcode": "NOP ", "value":          0                          |SP:  2043 |CR: OpCode: SAVE, Value:       2047, Relative: False      |PS:  0
INFO    control_unit:__print__     Tick:    30 |Action: Read operand (mem[AR] -> DR)                                 |Interrupt: none  |ACC:         10 |AR:  2047 |IP:    15 |DR: "index": 2047, "opcode": "NOP ", "value":          0                          |SP:  2043 |CR: OpCode: SAVE, Value:       2047, Relative: False      |PS:  0
INFO    control_unit:__print__     Tick:    31 |Action: Output: 10                                                   |Interrupt: none  |ACC:         10 |AR:  2047 |IP:    15 |DR: "index": 2047, "opcode": "NOP ", "value":          0                          |SP:  2043 |CR: OpCode: SAVE, Value:       2047, Relative: False      |PS:  0
INFO    control_unit:__print__     Tick:    31 |Action: Execute instruction (SAVE: ACC -> mem[AR])                   |Interrupt: none  |ACC:         10 |AR:  2047 |IP:    15 |DR: "index": 2047, "opcode": "NOP ", "value":          0                          |SP:  2043 |CR: OpCode: SAVE, Value:       2047, Relative: False      |PS:  0
INFO    control_unit:__print__     Tick:    32 |Action: Fetch instruction (IP -> AR, mem[IP] -> CR)                  |Interrupt: none  |ACC:         10 |AR:    15 |IP:    16 |DR: "index": 2047, "opcode": "NOP ", "value":          0                          |SP:  2043 |CR: OpCode: HLT , Value:          0, Relative: None       |PS:  0
INFO    control_unit:__print__     Tick:    33 |Action: Fetch Instruction (IP + 1 -> IP)                             |Interrupt: none  |ACC:         10 |AR:    15 |IP:    16 |DR: "index": 2047, "opcode": "NOP ", "value":          0                          |SP:  2043 |CR: OpCode: HLT , Value:          0, Relative: None       |PS:  0
INFO    control_unit:__print__     Tick:    34 |Action: Execute instruction (HLT)                                    |Interrupt: halt  |ACC:         10 |AR:    15 |IP:    16 |DR: "index": 2047, "opcode": "NOP ", "value":          0                          |SP:  2043 |CR: OpCode: HLT , Value:          0, Relative: None       |PS:  0
INFO    control_unit:__print__     Tick:    35 |Action: Halt                                                         |Interrupt: halt  |ACC:         10 |AR:    15 |IP:    16 |DR: "index": 2047, "opcode": "NOP ", "value":          0                          |SP:  2043 |CR: OpCode: HLT , Value:          0, Relative: None       |PS:  0
Output: [10]
Instruction number: 7
Ticks: 36
```

Пример проверки исходного кода:

```
> pytest . -v --update-goldens                                                                                                                                                                               
================================================================================================================ test session starts ================================================================================================================
platform win32 -- Python 3.12.0, pytest-8.1.2, pluggy-1.5.0 -- C:\IMPRIMIR\2kurs\4Sem\AK\Lab3\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\IMPRIMIR\2kurs\4Sem\AK\Lab3
configfile: pyproject.toml
plugins: golden-0.2.2
collected 6 items                                                                                                                                                                                                                                    

golden_test.py::test_translator_and_machine[golden/cat.yml] PASSED                                                                                                                                                                             [ 16%]
golden_test.py::test_translator_and_machine[golden/cheetah.yml] PASSED                                                                                                                                                                         [ 33%]
golden_test.py::test_translator_and_machine[golden/hellouser.yml] PASSED                                                                                                                                                                       [ 50%]
golden_test.py::test_translator_and_machine[golden/helloworld.yml] PASSED                                                                                                                                                                      [ 66%]
golden_test.py::test_translator_and_machine[golden/prob2.yml] PASSED                                                                                                                                                                           [ 83%]
golden_test.py::test_translator_and_machine[golden/sum.yml] PASSED                                                                                                                                                                             [100%]

================================================================================================================= 6 passed in 1.37s ================================================================================================================= 
> ruff format --check         
8 files already formatted
```


```
| ФИО                   | алг          | LoC | code инстр. | инстр. | такт. |
| Маликов Глеб Игоревич | cat          | 17  | 9           | 32     | 154   |
| Маликов Глеб Игоревич | hellouser    | 71  | 70          | 214    | 1057  |
| Маликов Глеб Игоревич | helloworld   | 17  | 23          | 80     | 401   |
| Маликов Глеб Игоревич | prob2        | 49  | 27          | 514    | 2505  |
| Маликов Глеб Игоревич | sum          | 22  | 10          | 7      | 36    |
```