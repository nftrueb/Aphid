from dataclasses import dataclass
import sys

opcode_int_to_str = {
    1:  'add',
    5:  'and', 
    0:  'br', 
    12: 'jmp', 
    6:  'ldr', 
    9:  'not', 
    8:  'rti', 
    7:  'str', 
    15: 'trap', 
}

opcode_str_to_int = {
    'add': 1, 
    'and': 5, 
    'br' : 0,
    'jmp': 12, 
    'ldr': 6, 
    'not': 9, 
    'rti': 8, 
    'str': 7, 
    'trap': 15
}

HEX = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
def int_to_hex_str(value, bits=4): 
    if value <= 15: 
        return HEX[value]
    return int_to_hex_str(value // 16) + HEX[value & 0xF]

def hex_str_to_int(value): 
    if len(value) == 1: 
        if '0' <= value <= '9': 
            return int(value)
        
        if 'A' <= value <= 'F': 
            return ord(value) - ord('A')
    
    return hex_str_to_int(value[0]) * 16 + hex_str_to_int(value[1:])


@dataclass
class Instruction: 
    opcode: int 

    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]}'
    
@dataclass
class RtiInstruction: 
    opcode: int 

    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]}'
    
    def encode(self): 
        return f'{int_to_hex_str(self.opcode)}000'
    
@dataclass
class AddInstruction(Instruction): 
    dr: int 
    sr1: int 
    sr2: int | None = None
    imm: int | None = None

    def __str__(self): 
        s = f'{opcode_int_to_str[self.opcode]} R{self.dr}, R{self.sr1},'
        if self.sr2 is not None: 
            s += f' R{self.sr2}'
        else: 
            s += f' #{self.imm}'
        return s 
    
@dataclass
class AndInstruction(Instruction): 
    dr: int 
    sr1: int 
    sr2: int | None = None
    imm: int | None = None

    def __str__(self): 
        s = f'{opcode_int_to_str[self.opcode]} R{self.dr}, R{self.sr1},'
        if self.sr2 is not None: 
            s += f' R{self.sr2}'
        else: 
            s += f' #{self.imm}'
        return s 
    
@dataclass
class JmpInstruction(Instruction): 
    base_reg: int 
    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]} R{self.base_reg}'
    
@dataclass
class LdrInstruction(Instruction): 
    dr: int 
    base_reg: int 
    offset: int

    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]} R{self.dr}, R{self.base_reg}, #{self.offset}'
    
@dataclass
class NotInstruction(Instruction): 
    dr: int 
    sr: int 

    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]} R{self.dr}, R{self.base_reg}'
    
@dataclass
class StrInstruction(Instruction): 
    dr: int 
    base_reg: int 
    offset: int

    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]} R{self.dr}, R{self.base_reg}, #{self.offset}'
    
@dataclass
class TrapInstruction(Instruction): 
    vector: int

    def __repr__(self): 
        return f'TrapInstruction(opcode={opcode_int_to_str[self.opcode]}, vector={self.vector:#x})'

    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]} {self.vector:#x}'