import contextlib
import io
import logging
import os
import tempfile

import machine
import pytest
import translator


@pytest.mark.golden_test("golden/*.yml")
def test_translator_and_machine(golden, caplog):
    caplog.set_level(logging.INFO)

    # Создаём временную папку для тестирования приложения.
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Готовим имена файлов для входных и выходных данных.
        source = os.path.join(tmpdirname, "source.asmm")
        input_text = os.path.join(tmpdirname, "input.txt")
        target = os.path.join(tmpdirname, "target.asmx")

        # Записываем входные данные в файлы. Данные берутся из теста.
        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["in_source"])
        with open(input_text, "w", encoding="utf-8") as file:
            file.write(golden["in_stdin"])

        # Запускаем транслятор и собираем весь стандартный вывод в переменную
        # stdout
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            translator.main(source, target)
            print("============================================================")
            machine.main(target, input_text)

        # Выходные данные также считываем в переменные.
        with open(target, encoding="utf-8") as file:
            code = file.read()

        caplog_text = caplog.text.replace("\x00", " ")  # Проблема с нулевыми байтами.

        # Проверяем, что ожидания соответствуют реальности.
        assert code == golden.out["out_code"]
        assert stdout.getvalue() == golden.out["out_stdout"]
        assert caplog_text == golden.out["out_log"]
