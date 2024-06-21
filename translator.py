def main(source, target):
    with open(source, encoding="utf-8") as f:
        source = f.read()

    code, memory = translate_source(source)

    write_to_json(target, code, memory)

    print(
        f"source LoC: {len(source.splitlines())} code instr: {len(code)}"
    )


if __name__ == "__main__":
    assert (
        len(sys.argv) == 3
    ), "Invalid usage: python translator.py <source_file> <target_file>"
    _, source, target = sys.argv
    main(source, target)
