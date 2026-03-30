from Instruction import InstructionType, Instruction, UnitType
from Register import RegisterBank



class Entry:
    def __init__(self, operation: Instruction, tag: str):
        self.tag= tag
        self.busy = True
        self.operation= operation
        self.state = 'ISS'
        self.latency= operation.type.unit.value
        self.vj=None
        self.vk=None
        self.qj=None
        self.qk=None
        self.inm=None
        self.vj_cycle= 0
        self.vk_cycle= 0
        self.result=None
        self.ready_cycle=0

    def update(self, operation: Instruction):
        self.busy = True
        self.operation = operation
        self.state = 'ISS'
        self.latency = operation.type.unit.value
        self.vj = None
        self.vk = None
        self.qj = None
        self.qk = None
        self.inm = None
        self.vj_cycle = 0
        self.vk_cycle = 0
        self.result=None
        self.ready_cycle=0

class Station:
    def __init__(self):
        self.stations = {}
        self.unit_counters = {}
        for unit in UnitType:
            new_list=[]
            self.stations[unit] = new_list
            self.unit_counters[unit] = 0

    def add_instruction_to_station(self, instruction: Instruction, rbank: RegisterBank):
        utype = instruction.type.unit
        entry=None
        is_new=False
        if instruction.type.unit is not UnitType.MEM:
            for e in self.stations[utype]:
                if not e.busy:
                    e.update(instruction)
                    entry=e
        if entry is None:
            tag = f"{utype.name}_{self.unit_counters[utype]}"
            self.unit_counters[utype] += 1
            entry = Entry(instruction, tag)
            is_new= True
        #rs: TODOS
        rs = rbank.getRegister(instruction.src1)
        if not rs.busy:
            entry.vj = rs.value
        else:
            entry.qj = rs.tag
        #rt: ES MEM
        if instruction.type.unit is UnitType.MEM:
            entry.inm = instruction.src2
            rt = rbank.getRegister(instruction.dest)
            if instruction.type is InstructionType.SD:
                if not rt.busy:
                    entry.vk = rt.value
                else:
                    entry.qk = rt.tag
            else:
                rt.busy = True
                rt.tag = entry.tag
        #rt y rd: ES ALU O MULT
        else:
            rt = rbank.getRegister(instruction.src2)
            if not rt.busy:
                entry.vk = rt.value
            else:
                entry.qk = rt.tag
        if instruction.type.unit is not UnitType.MEM:
            rd= rbank.getRegister(instruction.dest)
            rd.busy= True
            rd.tag=entry.tag
        #Se añade la entrada a la estación
        if is_new: self.stations[utype].append(entry)
        return entry.tag

    def spread_result(self, value, tag, cycle, rbank: RegisterBank)->tuple[list, list]:
        updated_entries: list[str]=[]
        updated_registers: list[str]=[]
        for unit in self.stations:
            for entry in self.stations[unit]:
                if entry.busy:
                    if entry.qj == tag:
                        entry.vj = value
                        entry.qj = None
                        entry.vj_cycle = cycle
                        updated_entries.append(entry.tag)
                    if entry.qk == tag:
                        entry.vk = value
                        entry.qk = None
                        entry.vk_cycle = cycle
                        updated_entries.append(entry.tag)
        for register in rbank.float_regs.values():
            if register.update(value, tag):
                updated_registers.append(register.name)
        for register in rbank.int_regs.values():
            if register.update(value, tag):
                updated_registers.append(register.name)
        return updated_entries, updated_registers
