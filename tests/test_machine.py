import logging
import os
import re
import tempfile

import pytest
from machine import main as computer
from translator import main as perform_translator


def replace_multiple_spaces_with_one(s):
    return re.sub(r"\s+", " ", s)


@pytest.mark.golden_test("golden/*.yml")
def test_bar(golden, caplog, request):
    caplog.set_level(logging.DEBUG)


    with tempfile.TemporaryDirectory() as tmpdir:
        source_file = os.path.join(tmpdir, "source.asm")
        target_file = os.path.join(tmpdir, "source.json")
        input_file = os.path.join(tmpdir, "input.txt")
        with open(input_file, "w", encoding="utf-8") as inp_file:
            inp_file.write(golden["stdin"])
        with open(source_file, "w", encoding="utf-8") as file:
            file.write(golden["source_code"])
        print("=" * 5)
        print("source_code")
        print(golden["source_code"])
        perform_translator(source_file, target_file)
        print("=" * 5)
        print("target_file")
        #show target_file content
        with open(target_file, encoding="utf-8") as file:
            print(file.read())
        computer(target_file, input_file)

        with open(target_file, encoding="utf-8") as file:
            human_readable = file.read()

        expected_code_readable = replace_multiple_spaces_with_one(human_readable.rstrip("\n"))
        golden_code_readable = replace_multiple_spaces_with_one(golden.out["out_code_readable"].rstrip("\n"))



        assert expected_code_readable == golden_code_readable

        open("file_log.txt", "w").write(caplog.text)
        expected_log = replace_multiple_spaces_with_one(caplog.text.rstrip("\n").replace("\t", "   "))
        golden_log = replace_multiple_spaces_with_one(golden.out["out_log"].rstrip("\n").replace("\t", "    "))


        assert expected_log == golden_log

