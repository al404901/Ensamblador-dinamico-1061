from Instruction import Instruction, InstructionType, UnitType
from Register import RegisterBank
from Station import Station


class Simulator:
    def __init__(self):
        self.rbank=RegisterBank()
        self.station=Station()
        self.instruction_queue: list[Instruction] = []
        self.cycle_counter=0
        self.wb_queue = []

    def add_instructions(self, instructions: list[Instruction]):
        for instruction in instructions:
            self.instruction_queue.append(instruction)

    def next_cycle(self)->bool:
        self.cycle_counter+=1
        print(f"Ciclo número: {self.cycle_counter}")
        self.wb_stage()
        self.ex_stage()
        self.iss_stage()
        for unit in self.station.stations:
            for entry in self.station.stations[unit]:
                if entry.busy:
                    return True
        return False


    @property
    def queue_length(self):
        return len(self.instruction_queue)

    def iss_stage(self):
        if self.queue_length!=0:
            instruction = self.instruction_queue.pop(0)
            tag=self.station.add_instruction_to_station(instruction, self.rbank)
            print(f"[{tag}] Se le ha asignado '{instruction}' y ha pasado a ISS")

    def wb_stage(self):
        if len(self.wb_queue) > 0:
            entry = self.wb_queue.pop(0)
            entry.state = 'WB'
            print(f"[{entry.tag}] Ha pasado a WB")
            temporal_result = 10101.0
            updated_entries, updated_registers=self.station.spread_result(temporal_result, entry.tag, self.cycle_counter, self.rbank)
            entry.busy = False
            entry.ready_cycle=self.cycle_counter
            if entry.operation.type is not InstructionType.SD:
                print(f"[Common Data Bus] — Se ha difundido el resultado de {entry.tag} a las siguientes fuentes: {updated_entries} y {updated_registers}")
            else:
                print(f"[STORE] — Se ha almacenado un dato en la dirección de memoria {entry.m_address} por parte de {entry.tag}")



    def ex_stage(self):
        available_step_to_ex = True
        for unit in self.station.stations:
            first=True
            for entry in self.station.stations[unit]:
                if entry.state == 'WB' and self.cycle_counter == entry.ready_cycle: #para que espere que acabe la UF EN WB
                    break
                if entry.busy:
                    if entry.state == 'EX':
                        entry.latency -= 1
                        if entry.latency == 0:
                            if entry.operation.type is InstructionType.SD:
                                entry.m_address = entry.inm + entry.vj
                            self.wb_queue.append(entry)
                        break

                    elif available_step_to_ex and entry.state == 'ISS':
                        #PARA CUANDO MEM
                        if entry.operation.type.unit is UnitType.MEM and first:
                            if entry.operation.type is InstructionType.LD:
                                if entry.qj is None:
                                    if entry.vj_cycle < self.cycle_counter:
                                        entry.state = 'EX'
                                        print(f"[{entry.tag}] Ha pasado a EX")
                                        entry.latency -= 1
                                        available_step_to_ex = False
                            else:
                                if entry.qj is None and entry.qk is None:
                                    if entry.vj_cycle < self.cycle_counter and entry.vk_cycle < self.cycle_counter:
                                        entry.state = 'EX'
                                        print(f"[{entry.tag}] Ha pasado a EX")
                                        entry.latency -= 1
                                        available_step_to_ex = False

                        # RESTO DE CASOS
                        elif entry.qj is None and entry.qk is None:
                            if entry.vj_cycle < self.cycle_counter and entry.vk_cycle < self.cycle_counter:
                                entry.state = 'EX'
                                print(f"[{entry.tag}] Ha pasado a EX")
                                entry.latency -= 1
                                available_step_to_ex = False
                    first=False #para evitar en MEM adelantamientos




def cargar_instrucciones_desde_fichero(ruta_archivo: str) -> list[Instruction]:
    instrucciones = []
    try:
        with open(ruta_archivo, 'r') as archivo:
            for linea in archivo:
                # Quitamos espacios en blanco al principio y final
                linea_limpia = linea.strip()

                # Ignoramos líneas vacías o que empiezan por comentario (opcional)
                if not linea_limpia or linea_limpia.startswith('#') or linea_limpia.startswith(';'):
                    continue

                # Usamos el método que creamos en la clase Instruction
                nueva_inst = Instruction.from_string(linea_limpia)
                if nueva_inst:
                    instrucciones.append(nueva_inst)

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en {ruta_archivo}")
    except Exception as e:
        print(f"Error al leer el fichero: {e}")

    return instrucciones


if __name__ == '__main__':
        simulador = Simulator()
        ruta = "codigo.txt"
        instrucciones = cargar_instrucciones_desde_fichero(ruta)
        simulador.add_instructions(instrucciones)
        while simulador.next_cycle():
            pass



