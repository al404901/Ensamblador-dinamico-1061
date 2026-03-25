import tkinter as tk
from tkinter import scrolledtext, ttk
from Instruction import Instruction
from Simulator import Simulator

#TODO ESTE CODIGO LO HA GENERADO GEMINI PARA PODER DEPURAR E INTERACTUAR EL SIMULADOR EN TIEMPO REAL

# Variables globales para control de estado
simulador_actual = None
total_instrucciones = 0


def actualizar_tabla(simulador, tabla_er):
    for item in tabla_er.get_children():
        tabla_er.delete(item)

    for unit in simulador.station.stations:
        for entry in simulador.station.stations[unit]:
            # Extraemos los datos de la entrada
            vj_val = entry.vj if entry.vj is not None else "-"
            vk_val = entry.vk if entry.vk is not None else "-"
            qj_val = entry.qj if entry.qj else "-"
            qk_val = entry.qk if entry.qk else "-"
            ready_val = entry.ready_cycle if entry.ready_cycle > 0 else "-"

            # OBTENER EL TIPO DE INSTRUCCIÓN (ej: fadd, ld, etc.)
            tipo_inst = entry.operation.type.name if entry.operation else "-"

            estado_visual = entry.state if entry.busy else "LIBRE (Terminada)"

            # Insertar en la tabla incluyendo la nueva columna 'Inst'
            tabla_er.insert("", tk.END, values=(
                entry.tag,
                tipo_inst,  # <--- Nueva columna
                estado_visual,
                vj_val,
                vk_val,
                qj_val,
                qk_val,
                entry.latency,
                ready_val
            ))

    # Actualizar contador de ciclos en la interfaz
    label_ciclos.config(
        text=f"Ciclo actual: {simulador.cycle_counter}  |  Instrucciones en cola: {len(simulador.instruction_queue)}")


def iniciar_simulacion():
    global simulador_actual, total_instrucciones
    contenido = caja_texto.get("1.0", tk.END)
    lineas = contenido.splitlines()

    simulador_actual = Simulator()
    instrucciones = []

    for linea in lineas:
        linea_limpia = linea.strip()
        if not linea_limpia or linea_limpia.startswith(('#', ';')):
            continue
        try:
            nueva_inst = Instruction.from_string(linea_limpia)
            if nueva_inst:
                instrucciones.append(nueva_inst)
        except Exception as e:
            print(f"Error parseando: {e}")

    if instrucciones:
        total_instrucciones = len(instrucciones)
        simulador_actual.add_instructions(instrucciones)
        actualizar_tabla(simulador_actual, tabla_er)

        # Resetear UI
        boton_paso.config(state=tk.NORMAL)
        boton_todo.config(state=tk.NORMAL)
        label_resumen.config(text="")
        print(f"--- Sistema Cargado: {total_instrucciones} instrucciones ---")


def finalizar_simulacion():
    # Mostrar el total de ciclos y de instrucciones al terminar
    resumen = f"🏁 SIMULACIÓN FINALIZADA\nCiclos Totales: {simulador_actual.cycle_counter}\nInstrucciones Procesadas: {total_instrucciones}"
    label_resumen.config(text=resumen, fg="#0056b3")
    boton_paso.config(state=tk.DISABLED)
    boton_todo.config(state=tk.DISABLED)


def siguiente_paso():
    if simulador_actual:
        hay_actividad = simulador_actual.next_cycle()
        actualizar_tabla(simulador_actual, tabla_er)
        if not hay_actividad:
            finalizar_simulacion()


def ejecutar_todo():
    if simulador_actual:
        boton_todo.config(state=tk.DISABLED)
        boton_paso.config(state=tk.DISABLED)

        # Bucle de ejecución rápida con refresco visual
        while simulador_actual.next_cycle():
            actualizar_tabla(simulador_actual, tabla_er)
            ventana.update()

        actualizar_tabla(simulador_actual, tabla_er)
        finalizar_simulacion()


if __name__ == '__main__':
    ventana = tk.Tk()
    ventana.title("Tomasulo Simulator - Visual Debugger")
    ventana.geometry("1000x850")

    # 1. Área de texto para el código
    tk.Label(ventana, text="Ensamblador MIPS:", font=('Arial', 10, 'bold')).pack(pady=5)
    caja_texto = scrolledtext.ScrolledText(ventana, width=100, height=10)
    caja_texto.pack(padx=10, pady=5)
    caja_texto.insert(tk.INSERT, "ld f2, 0(r1)\nfadd f4, f2, f3\nfmult f6, f4, f2\nsd f6, 8(r1)")

    # 2. Botonera
    frame_ctrl = tk.Frame(ventana)
    frame_ctrl.pack(pady=10)

    tk.Button(frame_ctrl, text="1. Cargar Código", command=iniciar_simulacion,
              bg="#007bff", fg="white", width=18).grid(row=0, column=0, padx=5)

    boton_paso = tk.Button(frame_ctrl, text="2. Paso a Paso >", command=siguiente_paso,
                           bg="#28a745", fg="white", state=tk.DISABLED, width=18)
    boton_paso.grid(row=0, column=1, padx=5)

    boton_todo = tk.Button(frame_ctrl, text="3. Ejecutar Todo >>", command=ejecutar_todo,
                           bg="#dc3545", fg="white", state=tk.DISABLED, width=18)
    boton_todo.grid(row=0, column=2, padx=5)

    # Contador de ciclos en vivo
    label_ciclos = tk.Label(ventana, text="Ciclo: 0", font=('Consolas', 11, 'bold'), fg="#555")
    label_ciclos.pack()

    # 3. Tabla de Estaciones de Reserva (Monitor)
    tk.Label(ventana, text="Monitor de Estaciones de Reserva:", font=('Arial', 10, 'bold')).pack(pady=(15, 5))

    # Añadida columna 'Inst'
    columnas = ("Tag", "Inst", "Estado", "Vj", "Vk", "Qj", "Qk", "Lat", "Ready")
    tabla_er = ttk.Treeview(ventana, columns=columnas, show='headings', height=15)

    anchos = {"Tag": 70, "Inst": 80, "Estado": 130, "Vj": 80, "Vk": 80, "Qj": 70, "Qk": 70, "Lat": 50, "Ready": 70}
    for col in columnas:
        tabla_er.heading(col, text=col)
        tabla_er.column(col, width=anchos.get(col, 100), anchor=tk.CENTER)

    tabla_er.pack(padx=10, pady=10, fill=tk.X)

    # 4. Resumen de resultados (Ciclos totales)
    label_resumen = tk.Label(ventana, text="", font=('Arial', 12, 'bold'), pady=20)
    label_resumen.pack()

    ventana.mainloop()