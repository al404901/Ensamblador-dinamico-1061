from Instruction import Instruction, InstructionType
from Register import RegisterBank
from Station import Station


class Simulator:
    def __init__(self):
        self.rbank=RegisterBank()
        self.station=Station()
        self.instruction_queue: list[Instruction] = []
        self.cycle_counter=0

    def add_instructions(self, instructions: list[Instruction]):
        for instruction in instructions:
            self.instruction_queue.append(instruction)

    def next_cycle(self):
        self.cycle_counter+=1
        print(f"Ciclo número: {self.cycle_counter}")
        self.wb_stage()
        self.ex_stage()
        self.iss_stage()

    @property
    def queue_length(self): #por si hace falta en un futuro
        return len(self.instruction_queue)

    def iss_stage(self):
        if self.queue_length!=0:
            instruction = self.instruction_queue.pop(0)
            tag=self.station.add_instruction_to_station(instruction, self.rbank)
            print(f"[{tag}] Se le ha asignado '{instruction}' y ha pasado a ISS")

    def wb_stage(self):
        for unit in self.station.stations:
            for entry in self.station.stations[unit]:
                if entry.busy and entry.state=='WB':
                    temporal_result= 122
                    for register in self.rbank.float_regs.values():
                        register.update(temporal_result, entry.tag)
                    for register in self.rbank.int_regs.values():
                        register.update(temporal_result, entry.tag)

                    self.station.spread_result(temporal_result, entry.tag)
                    entry.busy = False
                    print(f"[{entry.tag}] Ha difundido sus resultados a registros y estaciones con su TAG")


    def ex_stage(self):
        for unit in self.station.stations:
            for entry in self.station.stations[unit]:
                if entry.busy:
                    if entry.state == 'ISS':
                        if entry.qj is None and entry.qk is None:
                            entry.state = 'EX'
                            print(f"[{entry.tag}] Ha pasado a EX")
                    elif entry.state == 'EX':
                        entry.latency -= 1
                        if entry.latency == 0:
                            entry.state = 'WB'
                            print(f"[{entry.tag}] Ha pasado a WB")




if __name__ == '__main__':
        #IMPORTANTE: implementar txt --> lista de clase Instruccion o hacer un entorno gráfico sencillo
        simulador = Simulator()
        #EJERCICIO1
        #inst1 = Instruction(InstructionType.FADD, "f1", "f2", "f3")
        #inst2 = Instruction(InstructionType.FMULT, "f4", "f5", "f6")
        #inst3 = Instruction(InstructionType.LD, "r1", "r2", "4")
        #inst4 = Instruction(InstructionType.SD, "r3", "r1", "44")
        #EJERCICIO2
        instrucciones=[Instruction(InstructionType.LD, "f2", "r2", 0),Instruction(InstructionType.FADD, "f4", "f5", "f6"),Instruction(InstructionType.FMULT, "f5", "f6", "f7")]
        simulador.add_instructions(instrucciones)
        for i in range(100):
            simulador.next_cycle()

