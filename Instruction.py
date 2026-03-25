from enum import Enum

class UnitType(Enum):
    MEM=3
    ALU=2
    MULT=5

class InstructionType(Enum):
    FADD=(1, UnitType.ALU)
    FSUB=(2, UnitType.ALU)
    FMULT=(3, UnitType.MULT)
    LD=(4, UnitType.MEM)
    SD=(5, UnitType.MEM)

    def __init__(self, op_code, unit):
        self.op_code = op_code
        self.unit = unit


class Instruction:
    def __init__(self, type: InstructionType, dest:str, src1:str, src2):
        self.type = type
        self.dest = dest
        self.src1 = src1
        self.src2 = src2

    def __str__(self):
        if self.type.unit!=UnitType.MEM:
            return  f"{self.type.name.lower()} {self.dest}, {self.src1} , {self.src2}"
        else:
            return f"{self.type.name.lower()} {self.dest}, {self.src2}({self.src1})"

    @staticmethod
    def from_string(line: str):
        line = line.lower().replace(',', ' ').replace('(', ' ').replace(')', ' ').strip()
        parts= line.split()
        if not parts:
            return None
        inst_name = parts[0].upper()
        try:
            type_enum = InstructionType[inst_name]
        except KeyError:
            raise ValueError(f"Instrucción desconocida: {inst_name}")
        dest = parts[1]
        if type_enum.unit == UnitType.MEM:
            offset = int(parts[2])
            base_reg = parts[3]
            return Instruction(type_enum, dest, base_reg, offset)
        else:
            src1 = parts[2]
            src2 = parts[3]
            return Instruction(type_enum, dest, src1, src2)
