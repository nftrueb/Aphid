import sys 
import math 

from instruction import (
    opcode_str_to_int, hex_str_to_int, Instruction, AddInstruction, AndInstruction, NotInstruction, LdrInstruction, 
    JmpInstruction, RtiInstruction, StrInstruction, TrapInstruction, OrigInstruction, FillInstruction
)

class Assembler: 
    def __init__(self, filename): 
        self.filename = filename 
        self.lines = []
        self.symbol_table = {}
        with open(filename, 'r') as f: 
            self.contents = f.read()

        print(f'[ INFO ] Input file: {filename}')

    def parse(self): 
        self.first_pass()
        self.second_pass()

        print('[ DEBUG ] Parsed Lines: ')
        for line in self.lines: 
            print(line)
        print()

        print('[ DEBUG ] Symbol Table after first pass: ')
        for k, v in self.symbol_table.items(): 
            print(k, v)
        print()


    def first_pass(self): 
        lines = self.contents.split('\n')
        pc = 0 
        for idx, line in enumerate(lines): 
            pc_inc = 1
            processed = line.split(';')[0].lower().strip()

            # check for label
            colon_idx = processed.find(':')
            if colon_idx >= 0: 
                symbol = processed[:colon_idx]
                if symbol not in self.symbol_table: 
                    self.symbol_table[symbol] = pc
                else: 
                    print(f'[ ERROR ] Found duplicate label definition during first pass: {symbol}')
                    sys.exit(3)

                # remove symbol from start of line and strip any leading whitespace 
                processed = processed[colon_idx+1:].strip()

            # skip any lines that only have whitespace/comments
            if len(processed) == 0: 
                continue 

            if processed.startswith('.orig'): 
                pc_inc = 0 

            if processed.startswith('.end'): 
                break 

            if processed.startswith('.blkw'): 
                pc_inc = 1 # add pc with operand

            # push processed line and inc PC if line is a valid instruction
            self.lines.append(processed + ' ')
            pc += pc_inc

    def second_pass(self):
        instructions = []
        pc = 0 
        for line in self.lines:
            tokens = []
            curr_word_start_idx = 0 
            for idx in range(len(line)): 
                if line[idx] in {' ', '/t', ','}: 
                    if curr_word_start_idx == idx: 
                        curr_word_start_idx = idx + 1
                        continue 

                    tokens.append(line[curr_word_start_idx:idx])
                    curr_word_start_idx = idx + 1

                    if line[idx] == ',': 
                        tokens.append(line[idx])

            # print('[ DEBUG ] Tokens:')
            # for i, t in enumerate(tokens):
            #     print(f'{i} - {t}')
            # print()
            if tokens[0] == '.end': 
                break 

            instructions.append(parse_instruction(tokens))

            if len(instructions) == 1 and instructions[0]: 
                pass

        print('[ DEBUG ] Instructions:')
        for i, t in enumerate(instructions):
            print(f'{i} - {t.__repr__()}')
        print()

def validate_register(value):
    return isinstance(value, str) and len(value) == 2 and value[0] == 'r' and int(value[1]) < 8

def validate_decimal(value, bits): 
    if not isinstance(value, str) or len(value) > 4 or value[0] != '#': 
        return False 
    
    idx = 1
    sign = 1
    if value[idx] == '-': 
        sign = -1 
        idx += 1
    num = sign * int(value[idx:])
    return -2**(bits-1) <= num <= 2**(bits-1)-1

def validate_hex(value, bits): 
    if not isinstance(value, str) or value[0] != 'x' or len(value[1:]) > math.ceil(bits / 4): 
        return False 
    
    try: 
        _ = int(value[1:])
    except Exception as _: 
        return False 
    return True 

def parse_register(value): 
    return int(value[1])

def parse_decimal(value): 
    return int(value[1:])

def parse_hex(value): 
    return hex_str_to_int(value[1:])

def parse_instruction(tokens) -> Instruction:  
    # directives 
    if tokens[0] == '.orig': 
        return parse_orig(tokens)
    elif tokens[0] == '.fill': 
        return parse_fill(tokens)
    elif tokens[0] == '.blkw': 
        pass 
    elif tokens[0] == '.external': 
        pass

    # instruction
    elif tokens[0] == 'add': 
        return parse_add(tokens)
    elif tokens[0] == 'and': 
        return parse_and(tokens) 
    elif tokens[0] == 'br': 
        pass 
    elif tokens[0] in { 'jmp', 'ret' }: 
        return parse_jmp_ret(tokens) 
    elif tokens[0] == 'jsr': 
        pass 
    elif tokens[0] == 'jsrr': 
        pass 
    elif tokens[0] == 'ld': 
        pass 
    elif tokens[0] == 'ldi': 
        pass 
    elif tokens[0] == 'ldr': 
        return parse_ldr(tokens) 
    elif tokens[0] == 'lea': 
        pass 
    elif tokens[0] == 'not': 
        return parse_not(tokens) 
    elif tokens[0] == 'rti': 
        return RtiInstruction(opcode_str_to_int['rti']) 
    elif tokens[0] == 'st': 
        pass 
    elif tokens[0] == 'sti': 
        pass 
    elif tokens[0] == 'str': 
        return parse_str(tokens) 
    elif tokens[0] == 'trap': 
        return parse_trap(tokens) 

    print(f'[ ERROR ] Unknown opcode encountered when parsing tokens: {tokens}')
    sys.exit(2)

def parse_orig(tokens) -> Instruction: 
    is_decimal = validate_decimal(tokens[1], 16)
    if not is_decimal and not validate_hex(tokens[1], 16): 
        print(f'[ ERROR ] OrigInstruction: failed to parse addr operand: {tokens[1]}')

    return OrigInstruction(
        opcode_str_to_int['directive'], 
        addr = parse_decimal(tokens[1]) if is_decimal else parse_hex(tokens[1])
    )

def parse_fill(tokens) -> Instruction: 
    if not validate_hex(tokens[1], 16): 
        print(f'[ ERROR ] FillInstruction: failed to parse operand: {tokens[1]}')

    return FillInstruction(
        opcode_str_to_int['directive'], 
        value = parse_hex(tokens[1])
    )

def parse_add(tokens) -> Instruction: 
    if not validate_register(tokens[1]) or not validate_register(tokens[3]):
        print(f'[ ERROR ] AddInstruction: failed to parse dr or sr1: {tokens[1], tokens[3]}')
        sys.exit(2)
    
    if tokens[2] != ',' or tokens[4] != ',': 
        print(f'[ ERROR ] AddInstruction: failed to parse commas: {tokens[2], tokens[4]}')
        sys.exit(2) 

    is_sr2 = validate_register(tokens[5]) 
    if not is_sr2 and not validate_decimal(tokens[5], 5): 
        print(f'[ ERROR ] AddInstruction: failed to parse sr2 or imm5: {tokens[5]}')
        sys.exit(2)

    return AddInstruction(
        opcode_str_to_int['add'], 
        dr = parse_register(tokens[1]), 
        sr1 = parse_register(tokens[3]), 
        sr2 = parse_register(tokens[5]) if is_sr2 else None, 
        imm = parse_decimal(tokens[5]) if not is_sr2 else None
    )

def parse_and(tokens) -> Instruction: 
    if not validate_register(tokens[1]) or not validate_register(tokens[3]):
        print(f'[ ERROR ] AndInstruction: failed to parse dr or sr1: {tokens[1], tokens[3]}')
        sys.exit(2)
    
    if tokens[2] != ',' or tokens[4] != ',': 
        print(f'[ ERROR ] AndInstruction: failed to parse commas: {tokens[2], tokens[4]}')
        sys.exit(2) 

    is_sr2 = validate_register(tokens[5]) 
    if not is_sr2 and not validate_decimal(tokens[5], 5): 
        print(f'[ ERROR ] AndInstruction: failed to parse sr2 or imm5: {tokens[5]}')
        sys.exit(2)

    return AndInstruction(
        opcode_str_to_int['and'], 
        dr = parse_register(tokens[1]), 
        sr1 = parse_register(tokens[3]), 
        sr2 = parse_register(tokens[5]) if is_sr2 else None, 
        imm = parse_decimal(tokens[5]) if not is_sr2 else None
    )

def parse_jmp_ret(tokens) -> Instruction: 
    if tokens[0] == 'ret': 
        tokens.append('r7')

    if not validate_register(tokens[1]):
        print(f'[ ERROR ] JmpInstruction: failed to parse base register: {tokens[1]}')
        sys.exit(2)

    return JmpInstruction(
        opcode_str_to_int['jmp'], 
        base_reg = parse_register(tokens[1])
    )

# LDR R4, R2, #-5
def parse_ldr(tokens) -> Instruction: 
    if not validate_register(tokens[1]) or not validate_register(tokens[3]) or not validate_decimal(tokens[5], 6):
        print(f'[ ERROR ] LdrInstruction: failed to parse dr, base_reg, or offset6: {tokens[1], tokens[3]}')
        sys.exit(2)
    
    if tokens[2] != ',' or tokens[4] != ',': 
        print(f'[ ERROR ] LdrInstruction: failed to parse commas: {tokens[2], tokens[4]}')
        sys.exit(2) 

    return LdrInstruction(
        opcode_str_to_int['ldr'], 
        dr = parse_register(tokens[1]), 
        base_reg = parse_register(tokens[3]), 
        offset = parse_decimal(tokens[5])
    )

# NOT R4, R2
def parse_not(tokens) -> Instruction: 
    if not validate_register(tokens[1]) or not validate_register(tokens[3]):
        print(f'[ ERROR ] NotInstruction: failed to parse dr, sr: {tokens[1], tokens[3]}')
        sys.exit(2)
    
    if tokens[2] != ',': 
        print(f'[ ERROR ] NotInstruction: failed to parse commas: {tokens[2]}')
        sys.exit(2) 

    return NotInstruction(
        opcode_str_to_int['not'], 
        dr = parse_register(tokens[1]), 
        sr = parse_register(tokens[3])
    )

# STR R4, R2, #-5
def parse_str(tokens) -> Instruction: 
    if not validate_register(tokens[1]) or not validate_register(tokens[3]) or not validate_decimal(tokens[5], 6):
        print(f'[ ERROR ] StrInstruction: failed to parse dr, base_reg, or offset6: {tokens[1], tokens[3]}')
        sys.exit(2)
    
    if tokens[2] != ',' or tokens[4] != ',': 
        print(f'[ ERROR ] StrInstruction: failed to parse commas: {tokens[2], tokens[4]}')
        sys.exit(2) 

    return StrInstruction(
        opcode_str_to_int['str'], 
        dr = parse_register(tokens[1]), 
        base_reg = parse_register(tokens[3]), 
        offset = parse_decimal(tokens[5])
    )

# TRAP x23
def parse_trap(tokens) -> Instruction: 
    if not validate_hex(tokens[1], 8):
        print(f'[ ERROR ] TrapInstruction: failed to vector: {tokens[1]}')
        sys.exit(2)

    return TrapInstruction(
        opcode_str_to_int['trap'], 
        vector = parse_hex(tokens[1])
    )

def usage(): 
    print('$ python assembler.py {filename}')
    print('  -o | --output [filename]')
    print('  -h | --help')

def main(): 
    if '-h' in sys.argv or '--help' in sys.argv or len(sys.argv) < 2: 
        usage()
        sys.exit(1)

    Assembler(sys.argv[1]).parse()

    print('Successfully exited Aphid Assember ... ')

if __name__ == '__main__':  
    main()