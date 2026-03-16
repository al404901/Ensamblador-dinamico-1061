from enum import Enum

class UnitType(Enum):
    MEM=3
    ALU=2
    MULT=5

class InstructionType(Enum):
    FADD=UnitType.ALU
    FSUB=UnitType.ALU
    FMULT=UnitType.MULT
    LD=UnitType.MEM
    SD=UnitType.MEM


class Instruction:
    def __init__(self, type: InstructionType, dest:str, src1:str, src2):
        self.type = type
        self.dest = dest
        self.src1 = src1
        self.src2 = src2

    def __str__(self):
        if self.type.value!=UnitType.MEM:
            return  f"{self.type.name.lower()} {self.dest}, {self.src1} , {self.src2}"
        else:
            return f"{self.type.name.lower()} {self.dest}, {self.src2}({self.src1})"

