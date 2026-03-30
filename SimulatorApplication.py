

#TODO ESTE CODIGO LO HA GENERADO GEMINI PARA PODER DEPURAR E INTERACTUAR EL SIMULADOR EN TIEMPO REAL

import tkinter as tk
from tkinter import scrolledtext, ttk
from Instruction import Instruction
from Simulator import Simulator

# Variables globales para control de estado
simulador_actual = None
total_instrucciones = 0


def actualizar_tablas(simulador, tabla_er, tabla_regs):
    # 1. ACTUALIZAR ESTACIONES DE RESERVA
    for item in tabla_er.get_children():
        tabla_er.delete(item)

    for unit in simulador.station.stations:
        for entry in simulador.station.stations[unit]:
            # Extracción de datos de la entrada
            vj_val = entry.vj if entry.vj is not None else "-"
            vk_val = entry.vk if entry.vk is not None else "-"
            qj_val = entry.qj if entry.qj else "-"
            qk_val = entry.qk if entry.qk else "-"
            ready_val = entry.ready_cycle if entry.ready_cycle > 0 else "-"
            result_val = entry.result if entry.result is not None else "-"

            tipo_inst = entry.operation.type.name if entry.operation else "-"

            # Lógica de estado visual: Si ya no está ocupada pero terminó, es WB
            if not entry.busy and entry.ready_cycle > 0:
                estado_visual = "WB (Finalizado)"
            else:
                estado_visual = entry.state

            tabla_er.insert("", tk.END, values=(
                entry.tag,
                tipo_inst,
                estado_visual,
                vj_val,
                vk_val,
                qj_val,
                qk_val,
                entry.latency,
                result_val,
                ready_val
            ))

    # 2. ACTUALIZAR BANCO DE REGISTROS
    for item in tabla_regs.get_children():
        tabla_regs.delete(item)

    # Combinamos registros flotantes e internos
    todos_regs = {**simulador.rbank.float_regs, **simulador.rbank.int_regs}
    for name, reg in todos_regs.items():
        # Mostramos registros que están en uso o tienen valores iniciales distintos de 0
        if reg.busy or reg.value != 0:
            tabla_regs.insert("", tk.END, values=(
                reg.name,
                f"{reg.value:.2f}" if isinstance(reg.value, float) else reg.value,
                "SÍ" if reg.busy else "No",
                reg.tag if reg.tag else "-"
            ))

    label_ciclos.config(text=f"Ciclo actual: {simulador.cycle_counter}")


def iniciar_simulacion():
    global simulador_actual, total_instrucciones
    contenido = caja_texto.get("1.0", tk.END)
    lineas = contenido.splitlines()

    simulador_actual = Simulator()
    instrucciones = []

    for linea in lineas:
        linea_limpia = linea.strip()
        if not linea_limpia or linea_limpia.startswith(('#', ';')): continue
        try:
            nueva_inst = Instruction.from_string(linea_limpia)
            if nueva_inst: instrucciones.append(nueva_inst)
        except Exception as e:
            print(f"Error parseando: {e}")

    if instrucciones:
        total_instrucciones = len(instrucciones)
        simulador_actual.add_instructions(instrucciones)
        actualizar_tablas(simulador_actual, tabla_er, tabla_regs)

        # Resetear estado de la UI
        boton_paso.config(state=tk.NORMAL)
        boton_todo.config(state=tk.NORMAL)
        label_resumen.config(text="")
        print(f"--- Simulación Cargada: {total_instrucciones} instrucciones ---")


def finalizar_simulacion():
    resumen = f"SIMULACIÓN FINALIZADA\nCiclos Totales: {simulador_actual.cycle_counter}\nInstrucciones: {total_instrucciones}"
    label_resumen.config(text=resumen, fg="#0056b3")
    boton_paso.config(state=tk.DISABLED)
    boton_todo.config(state=tk.DISABLED)


def siguiente_paso():
    if simulador_actual:
        hay_actividad = simulador_actual.next_cycle()
        # Actualizamos siempre para ver el resultado del ciclo, incluso el último
        actualizar_tablas(simulador_actual, tabla_er, tabla_regs)
        if not hay_actividad:
            finalizar_simulacion()


def ejecutar_todo():
    if simulador_actual:
        boton_todo.config(state=tk.DISABLED)
        boton_paso.config(state=tk.DISABLED)

        # Bucle de ejecución rápida
        while simulador_actual.next_cycle():
            actualizar_tablas(simulador_actual, tabla_er, tabla_regs)
            ventana.update()

        # Actualización final post-bucle para capturar el último WB
        actualizar_tablas(simulador_actual, tabla_er, tabla_regs)
        finalizar_simulacion()


if __name__ == '__main__':
    ventana = tk.Tk()
    ventana.title("Tomasulo Simulator - Monitor de Hardware")
    ventana.geometry("1100x900")

    # 1. Entrada de Código
    tk.Label(ventana, text="Código:", font=('Arial', 10, 'bold')).pack(pady=5)
    caja_texto = scrolledtext.ScrolledText(ventana, width=100, height=8)
    caja_texto.pack(pady=5)
    # Código por defecto basado en tu fichero enviado
    caja_texto.insert(tk.INSERT, "ld f2,0(r1)\nfmult f3,f2,f5\nfadd f2,f4,f6\nfadd f2,f2,f3\nsd f2,0(r1)")

    # 2. Panel de Control
    frame_btn = tk.Frame(ventana)
    frame_btn.pack(pady=10)
    tk.Button(frame_btn, text="1. Cargar Código", command=iniciar_simulacion, bg="#007bff", fg="white", width=18).grid(
        row=0, column=0, padx=5)
    boton_paso = tk.Button(frame_btn, text="2. Paso Ciclo >", command=siguiente_paso, bg="#28a745", fg="white",
                           state=tk.DISABLED, width=18)
    boton_paso.grid(row=0, column=1, padx=5)
    boton_todo = tk.Button(frame_btn, text="3. Ejecutar Todo >>", command=ejecutar_todo, bg="#dc3545", fg="white",
                           state=tk.DISABLED, width=18)
    boton_todo.grid(row=0, column=2, padx=5)

    label_ciclos = tk.Label(ventana, text="Ciclo: 0", font=('Consolas', 12, 'bold'))
    label_ciclos.pack()

    # 3. Estaciones de Reserva
    tk.Label(ventana, text="Estaciones de Reserva:", font=('Arial', 10, 'bold')).pack(pady=(10, 0))
    cols_er = ("Tag", "Inst", "Estado", "Vj", "Vk", "Qj", "Qk", "Lat", "Result", "Ready")
    tabla_er = ttk.Treeview(ventana, columns=cols_er, show='headings', height=10)
    anchos = {"Tag": 70, "Inst": 70, "Estado": 120, "Vj": 70, "Vk": 70, "Qj": 70, "Qk": 70, "Lat": 50, "Result": 80,
              "Ready": 60}
    for col in cols_er:
        tabla_er.heading(col, text=col)
        tabla_er.column(col, width=anchos.get(col, 100), anchor=tk.CENTER)
    tabla_er.pack(padx=10, pady=5, fill=tk.X)

    # 4. Banco de Registros
    tk.Label(ventana, text="Banco de Registros:", font=('Arial', 10, 'bold')).pack(pady=(10, 0))
    cols_reg = ("Registro", "Valor", "Busy", "Tag (Pendiente)")
    tabla_regs = ttk.Treeview(ventana, columns=cols_reg, show='headings', height=8)
    for col in cols_reg:
        tabla_regs.heading(col, text=col)
        tabla_regs.column(col, width=150, anchor=tk.CENTER)
    tabla_regs.pack(padx=10, pady=5)

    # Resumen final
    label_resumen = tk.Label(ventana, text="", font=('Arial', 12, 'bold'), pady=10)
    label_resumen.pack()

    ventana.mainloop()