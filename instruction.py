from dataclasses import dataclass
from enum import Enum

opcode_int_to_str = {
    1:  'add',
    5:  'and', 
    0:  'br', 
    12: 'jmp', 
    4:  'jsr', 
    4:  'jsrr', 
    2:  'ld', 
    10: 'ldi', 
    14: 'lea', 
    6:  'ldr', 
    9:  'not', 
    8:  'rti', 
    3: 'st',
    11: 'sti',
    7:  'str', 
    15: 'trap', 
    13: 'directive'
}

opcode_str_to_int = {
    'add': 1, 
    'and': 5, 
    'br' : 0,
    'jmp': 12, 
    'jsr': 4, 
    'jsrr': 4, 
    'ld' : 2, 
    'ldi': 10, 
    'lea': 14, 
    'ldr': 6, 
    'not': 9, 
    'rti': 8, 
    'st': 3, 
    'sti': 11, 
    'str': 7, 
    'trap': 15, 
    'directive': 13
}

def int_to_16_bit(value: int): 
    return bytearray([(value >> 8) & 0xFF, value & 0xFF])

HEX = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
def int_to_hex_str(value, bits=4): 
    if value <= 15: 
        return HEX[value]
    return int_to_hex_str(value // 16) + HEX[value & 0xF]

def hex_str_to_int(value: str): 
    result = 0
    for i in range(len(value)): 
        digit = 0 
        if '0' <= value[i] <= '9': 
            digit = ord(value[i]) - ord('0')
        
        elif 'a' <= value[i] <= 'f': 
            digit = ord(value[i]) - ord('a') + 10

        else: 
            print(f'[ ERROR ] Failed to parse hex ... encounted invalid digit: {value[i]}')
        
        result *= 16
        result += digit
    return result

def twos_complement(value, bits): 
    if value >= 0: 
        return value 
    value *= -1
    mask = (1 << bits) - 1 
    return mask - value + 1

@dataclass
class Instruction: 
    opcode: int 

    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]}'
    
    def encode(self): 
        raise NotImplementedError
    
@dataclass
class OrigInstruction(Instruction): 
    opcode: int 
    addr: int

    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]}'
    
    def __repr__(self): 
        return f'OrigInstruction(opcode={opcode_int_to_str[self.opcode]}, addr={self.addr:#06x})'

    def encode(self): 
        return int_to_16_bit(self.addr)

@dataclass
class FillInstruction(Instruction): 
    opcode: int 
    value: int

    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]}'
    
    def __repr__(self): 
        return f'FillInstruction(opcode={opcode_int_to_str[self.opcode]}, value={self.value:#06x})'
    
    def encode(self): 
        return int_to_16_bit(self.value)
    
@dataclass
class RtiInstruction(Instruction): 
    opcode: int 

    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]}'
    
    def encode(self): 
        return bytearray([self.opcode << 4, 0x00])
    
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
    
    def encode(self): 
        first = self.opcode << 4
        first += self.dr << 1 
        first += (self.sr1 >> 2) & 0x1
        if self.sr2 is not None: 
            second = ((self.sr1 & 0x3) << 6) + self.sr2
        else: 
            imm = twos_complement(self.imm, 5) if self.imm < 0 else self.imm
            second = ((self.sr1 & 0x3) << 6) + (1 << 5) + imm

        return bytearray([first , second]) 
    
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
    
    def encode(self): 
        first = self.opcode << 4
        first += self.dr << 1 
        first += (self.sr1 >> 2) & 0x1
        if self.sr2 is not None: 
            second = ((self.sr1 & 0x3) << 6) + self.sr2
        else: 
            imm = twos_complement(self.imm, 5) if self.imm < 0 else self.imm
            second = ((self.sr1 & 0x3) << 6) + (1 << 5) + imm

        return bytearray([first , second]) 

@dataclass
class JmpInstruction(Instruction): 
    base_reg: int 
    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]} R{self.base_reg}'
    
    def encode(self): 
        first, second = 0, 0
        first = self.opcode << 4
        first += (self.base_reg >> 2) & 0x1
        second += (self.base_reg & 0x3) << 6
        return bytearray([first , second])
    
@dataclass
class JsrInstruction(Instruction): 
    offset: int 
    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]} x{self.offset:#x}'
    
    def encode(self): 
        offset = twos_complement(self.offset, 11)
        first = self.opcode << 4
        first += 1 << 3
        first += (offset >> 8) & 0x7
        second = offset & 0xff
        return bytearray([first , second]) 
    
@dataclass
class JsrrInstruction(Instruction): 
    base_reg: int 
    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]} R{self.base_reg}'
    
    def encode(self):
        first, second = 0, 0
        first = self.opcode << 4
        first += (self.base_reg >> 2) & 0x1
        second += (self.base_reg & 0x3) << 6
        return bytearray([first , second])
    
@dataclass
class LdInstruction(Instruction): 
    dr: int
    offset: int 
    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]} R{self.dr}, x{self.offset:#x}'
    
    def encode(self): 
        first, second = 0, 0
        offset = twos_complement(self.offset, 9)
        first = self.opcode << 4
        first += self.dr << 1
        first += (offset >> 8) & 0x1
        second += offset & 0xff
        return bytearray([first , second]) 
    
@dataclass
class LdiInstruction(Instruction): 
    dr: int
    offset: int 
    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]} R{self.dr}, x{self.offset:#x}'
    
    def encode(self): 
        first, second = 0, 0
        offset = twos_complement(self.offset, 9)
        first = self.opcode << 4
        first += self.dr << 1
        first += (offset >> 8) & 0x1
        second += offset & 0xff
        return bytearray([first , second]) 
    
@dataclass
class LeaInstruction(Instruction): 
    dr: int
    offset: int 
    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]} R{self.dr}, x{self.offset:#x}'
    
    def encode(self): 
        first, second = 0, 0
        offset = twos_complement(self.offset, 9)
        first = self.opcode << 4
        first += self.dr << 1
        first += (offset >> 8) & 0x1
        second += offset & 0xff
        return bytearray([first , second]) 
   
@dataclass
class LdrInstruction(Instruction): 
    dr: int 
    base_reg: int 
    offset: int

    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]} R{self.dr}, R{self.base_reg}, #{self.offset}'
    
    def encode(self): 
        first, second = 0, 0 
        offset = twos_complement(self.offset, 6)
        first += self.opcode << 4 
        first += self.dr << 1 
        first += (self.base_reg >> 2) & 0x1
        second += (self.base_reg & 0x3) << 6 
        second += offset & 0x3F
        return bytearray([first, second])
    
@dataclass
class NotInstruction(Instruction): 
    dr: int 
    sr: int 

    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]} R{self.dr}, R{self.base_reg}'
    
    def encode(self): 
        first, second = 0, 0
        first += self.opcode << 4 
        first += self.dr << 1
        first += (self.sr >> 2) & 0x1
        second += (self.sr & 0x3) << 6
        second += 0x3f
        return bytearray([first, second])
  
@dataclass
class StInstruction(Instruction): 
    dr: int
    offset: int 
    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]} R{self.dr}, x{self.offset:#x}'
    
    def encode(self): 
        first, second = 0, 0
        offset = twos_complement(self.offset, 9)
        first = self.opcode << 4
        first += self.dr << 1
        first += (offset >> 8) & 0x1
        second += offset & 0xff
        return bytearray([first , second]) 

@dataclass
class StiInstruction(Instruction): 
    dr: int
    offset: int 
    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]} R{self.dr}, x{self.offset:#x}'
    
    def encode(self): 
        first, second = 0, 0
        offset = twos_complement(self.offset, 9)
        first = self.opcode << 4
        first += self.dr << 1
        first += (offset >> 8) & 0x1
        second += offset & 0xff
        return bytearray([first , second]) 
  
@dataclass
class StrInstruction(Instruction): 
    dr: int 
    base_reg: int 
    offset: int

    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]} R{self.dr}, R{self.base_reg}, #{self.offset}'
    
    def encode(self): 
        first, second = 0, 0 
        offset = twos_complement(self.offset, 6)
        first += self.opcode << 4 
        first += self.dr << 1 
        first += (self.base_reg >> 2) & 0x1
        second += (self.base_reg & 0x3) << 6 
        second += offset & 0x3F
        return bytearray([first, second])
    
@dataclass
class TrapInstruction(Instruction): 
    vector: int

    def __repr__(self): 
        return f'TrapInstruction(opcode={opcode_int_to_str[self.opcode]}, vector={self.vector:#x})'

    def __str__(self): 
        return f'{opcode_int_to_str[self.opcode]} {self.vector:#x}'
    
    def encode(self): 
        first, second = 0, 0 
        vector = twos_complement(self.vector, 8)
        first += self.opcode << 4 
        second += vector & 0xFF
        return bytearray([first, second])