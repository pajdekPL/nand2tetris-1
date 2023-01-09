from sys import argv
from pathlib import Path


COMMENT_SIGN = "//"
C_INSTRUCTION = "111{a}{c1}{c2}{c3}{c4}{c5}{c6}{d1}{d2}{d3}{j1}{j2}{j3}"
all_instructions = []

PREDEFINED_SYMBOLS = {
    'R0': 0,
    'R1': 1,
    'R2': 2,
    'R3': 3,
    'R4': 4,
    'R5': 5,
    'R6': 6,
    'R7': 7,
    'R8': 8,
    'R9': 9,
    'R10': 10,
    'R11': 11,
    'R12': 12,
    'R13': 13,
    'R14': 14,
    'R15': 15,
    'SCREEN': 16384,
    'KBD': 24576,
    'SP': 0,
    'LCL': 1,
    'ARG': 2,
    'THIS': 3,
    'THAT': 4,
}
SYMBOLS_AND_LABELS = {
    'last_free_symbol': 16,
}
JUMP_BITS = {
    "JGT": ('0', '0', '1'),
    "JEQ": ('0', '1', '0'),
    "JGE": ('0', '1', '1'),
    "JLT": ('1', '0', '0'),
    "JNE": ('1', '0', '1'),
    "JLE": ('1', '1', '0'),
    "JMP": ('1', '1', '1'),
}
DESTINATION_BITS = {
    'M': ('0', '0', '1'),
    'D': ('0', '1', '0'),
    'MD': ('0', '1', '1'),
    'A': ('1', '0', '0'),
    'AM': ('1', '0', '1'),
    'AD': ('1', '1', '0'),
    'AMD': ('1', '1', '1'),
}
COMP_IF_A_BITS = {
    'M': ('1', '1', '0', '0', '0', '0'),
    '!M': ('1', '1', '0', '0', '0', '1'),
    '-M': ('1', '1', '0', '0', '1', '1'),
    'M+1': ('1', '1', '0', '1', '1', '1'),
    'M-1': ('1', '1', '0', '0', '1', '0'),
    'D+M': ('0', '0', '0', '0', '1', '0'),
    'D-M': ('0', '1', '0', '0', '1', '1'),
    'M-D': ('0', '0', '0', '1', '1', '1'),
    'D&M': ('0', '0', '0', '0', '0', '0'),
    'D|M': ('0', '1', '0', '1', '0', '1'),
}
COMP_IF_NOT_A_BITS = {
    '0': ('1', '0', '1', '0', '1', '0'),
    '1': ('1', '1', '1', '1', '1', '1'),
    '-1': ('1', '1', '1', '0', '1', '0'),
    'D': ('0', '0', '1', '1', '0', '0'),
    'A': ('1', '1', '0', '0', '0', '0'),
    '!D': ('0', '0', '1', '1', '0', '1'),
    '!A': ('1', '1', '0', '0', '0', '1'),
    '-D': ('0', '0', '1', '1', '1', '1'),
    '-A': ('1', '1', '0', '0', '1', '1'),
    'D+1': ('0', '1', '1', '1', '1', '1'),
    'A+1': ('1', '1', '0', '1', '1', '1'),
    'D-1': ('0', '0', '1', '1', '1', '0'),
    'A-1': ('1', '1', '0', '0', '1', '0'),
    'D+A': ('0', '0', '0', '0', '1', '0'),
    'D-A': ('0', '1', '0', '0', '1', '1'),
    'A-D': ('0', '0', '0', '1', '1', '1'),
    'D&A': ('0', '0', '0', '0', '0', '0'),
    'D|A': ('0', '1', '0', '1', '0', '1'),
}

def remove_all_comments_and_whitespaces_and_add_instructions(path: Path):
    with open(path) as file:
        for line in file.readlines():
            if not line:
                continue
            parsed_line = remove_comments_from_line_and_return_parsed_line(line)
            if parsed_line:
                all_instructions.append(parsed_line)


def remove_comments_from_line_and_return_parsed_line(line):
    return line[:line.find(COMMENT_SIGN)].strip().replace(" ", "")


def assign_all_labels(instructions: list[str]) -> None:
    labels_count = 0
    for idx, instruction in enumerate(instructions):
        label = get_label(instruction)
        if label:
            if SYMBOLS_AND_LABELS.get(label):
                continue
            SYMBOLS_AND_LABELS[label] = idx - labels_count
            labels_count += 1


def assign_all_symbols(instructions: list[str]) -> None:
    for instruction in instructions:
        predefined_symbol = PREDEFINED_SYMBOLS.get(instruction[1:]) if \
            PREDEFINED_SYMBOLS.get(instruction[1:]) != 0 else True
        label = get_label(instruction)
        symbol = get_symbol(instruction)
        if predefined_symbol:
            continue
        if label:
            continue
        if symbol:
            if SYMBOLS_AND_LABELS.get(symbol):
                continue
            SYMBOLS_AND_LABELS[symbol] = SYMBOLS_AND_LABELS['last_free_symbol']
            SYMBOLS_AND_LABELS['last_free_symbol'] = SYMBOLS_AND_LABELS['last_free_symbol'] + 1


def get_symbol(instruction: str) -> str:
    if instruction.startswith('@') and not instruction[1:].isnumeric():
        return instruction[1:]


def get_label(instruction: str) -> str:
    if instruction.startswith('(') and instruction.endswith(')'):
        return instruction[instruction.find('(')+1:instruction.find(')')]
    return ''


def compile_to_binary(instructions: list[str]) -> list:
    assign_all_labels(instructions)
    assign_all_symbols(instructions)
    compiled_instructions = []
    for instruction in instructions:
        if instruction.startswith('('):
            continue
        if is_a_instruction(instruction):
            binary = parse_a_instruction(instruction)
            compiled_instructions.append(binary)
        else:
            binary = parse_c_instruction(instruction)
            compiled_instructions.append(binary)
    return compiled_instructions


def is_a_instruction(instruction: str):
    if instruction.startswith("@"):
        return True
    return False


def parse_a_instruction(instruction: str) -> str:
    address = instruction[1:]
    if address.isnumeric():
        return format(int(instruction[1:]), '016b')
    elif PREDEFINED_SYMBOLS.get(instruction[1:]) == 0 or PREDEFINED_SYMBOLS.get(instruction[1:]):
        # format(<num>, '015b') -> to add leading zeros to the output, format(2, '08b') -> '00000010'
        return format(PREDEFINED_SYMBOLS[(instruction[1:])], '016b')
    elif get_symbol(instruction):
        return format(SYMBOLS_AND_LABELS[(instruction[1:])], '016b')


def parse_c_instruction(instruction: str):
    a = determine_a_bit(instruction)
    j1, j2, j3 = determine_jump_bits(instruction)
    d1, d2, d3 = determine_destination_bits(instruction)
    c1, c2, c3, c4, c5, c6 = determine_comp_bits(instruction, a)
    return C_INSTRUCTION.format(a=a, c1=c1, c2=c2, c3=c3, c4=c4, c5=c5, c6=c6, j1=j1,
                                j2=j2, j3=j3, d1=d1, d2=d2, d3=d3)


def determine_a_bit(instruction: str) -> str:
    eq_index = instruction.find("=")
    semicolon_index = instruction.find(";")

    instruction = instruction[eq_index+1:] if eq_index != -1 else instruction
    instruction = instruction[:semicolon_index] if semicolon_index != -1 else instruction
    if "M" in instruction:
        return '1'
    else:
        return '0'


def determine_jump_bits(instruction: str) -> tuple:
    if ';' not in instruction:
        return '0', '0', '0'
    return JUMP_BITS[instruction[instruction.find(";")+1:]]


def determine_destination_bits(instruction: str) -> tuple:
    if '=' not in instruction:
        return '0', '0', '0'
    return DESTINATION_BITS[instruction[:instruction.find('=')]]


def determine_comp_bits(instruction: str, a_bit: str) -> tuple:
    eq_sign_index = instruction.find("=")
    semicolon_sign_index = instruction.find(";")

    if eq_sign_index == -1 and semicolon_sign_index == -1:
        comp = instruction
    elif eq_sign_index != -1 and semicolon_sign_index != -1:
        comp = instruction[eq_sign_index+1:semicolon_sign_index]
    elif eq_sign_index != -1:
        comp = instruction[eq_sign_index+1:]
    elif semicolon_sign_index != -1:
        comp = instruction[:semicolon_sign_index]
    if a_bit == '0':
        return COMP_IF_NOT_A_BITS[comp]
    return COMP_IF_A_BITS[comp]


def write_binary_instructions_to_file(binary_instructions: list, file_path: str) -> None:
    with open(file_path, 'w+') as file:
        file.write('\n'.join(compile_to_binary(binary_instructions)))


if __name__ == '__main__':
    if len(argv) != 2:
        raise ValueError("Please pass just one argument for example:\n"
                         "python3 make_asm <path_to_asm_file>")
    file_path = Path(argv[1])
    hack_file_name = file_path.name.replace(".asm", ".hack")
    print(f'Compiling file {file_path} to {hack_file_name}')
    remove_all_comments_and_whitespaces_and_add_instructions(file_path)
    write_binary_instructions_to_file(all_instructions, hack_file_name)
