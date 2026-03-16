from Instruction import InstructionType, Instruction, UnitType
from Register import RegisterBank



class Entry:
    def __init__(self, operation: Instruction, tag: str):
        self.tag= tag
        self.busy = True
        self.operation= operation
        self.state = 'ISS'
        self.latency= operation.type.value.value
        self.vj=None
        self.vk=None
        self.qj=None
        self.qk=None


class Station:
    def __init__(self):
        self.stations = {}
        self.unit_counters = {}
        for unit in UnitType:
            new_list=[]
            self.stations[unit] = new_list
            self.unit_counters[unit] = 0

    def add_instruction_to_station(self, instruction: Instruction, rbank: RegisterBank):
        utype = instruction.type.value
        tag = f"{utype.name}_{self.unit_counters[utype]}"
        self.unit_counters[utype]+=1
        entry = Entry(instruction, tag)
        rs = rbank.getRegister(instruction.src1)
        if not rs.busy:
            entry.vj = rs.value
        else:
            entry.qj = rs.tag
        if instruction.type.value is UnitType.MEM:
            entry.vk = instruction.src2
        else:
            rt = rbank.getRegister(instruction.src2)
            if not rt.busy:
                entry.vk = rt.value
            else:
                entry.qk = rt.tag
        self.stations[utype].append(entry)
        rd= rbank.getRegister(instruction.dest)
        rd.busy= True
        rd.tag=tag
        return tag

    def spread_result(self, value, tag):
        for unit in self.stations:
            for entry in self.stations[unit]:
                if entry.busy:
                    if entry.qj == tag:
                        entry.vj = value
                        entry.qj = None
                    if entry.qk == tag:
                        entry.vk = value
                        entry.qk = None
