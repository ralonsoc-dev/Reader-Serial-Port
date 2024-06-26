import tkinter as tk
from tkinter import ttk

import customtkinter as ctk
import serial.tools.list_ports
from PIL import Image, ImageTk
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import Fourier
import serial
import threading
import time
seleccionados = []

class Ventana(object):
    def __init__(self):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        self.app = ctk.CTk()
        self.configuracion_principal()
        
        self.grafica_fourier = Fourier.grafica_fourier()
        
        self.frame_principal = ctk.CTkFrame(master=self.app, width=600, height=400, corner_radius=10, fg_color="transparent")
        self.frame_principal.pack(side="top", padx=20, pady=30)

        self.frame_footer = ctk.CTkFrame(master=self.app, width=1200, height=700, corner_radius=10, fg_color="transparent")
        self.frame_footer.pack(side="bottom", padx=10, pady=0)

        self.generar_frame_izquierda()
        self.generar_frame_derecha()
        self.generar_frame3()
        self.generar_frame4()
        
        #self.app.after(2000, self.agrandar())
        # Inicialización del atributo hilo_lectura
        self.serial_reader = None
        self.hilo_lectura = None
        self.detener_lectura = False

        # Inicializo listas
        self.mediaDedos = []
        self.accelerometro = []
        self.letra = ""
          
    def run(self):
        self.app.mainloop()
    
    def agrandar(self):
        self.app.state('zoomed')

    def configuracion_principal(self):
        self.app.title("Grabadora de Puerto Serie")
        # self.app.attributes('-fullscreen', True)  # ESTO PONE VENTANA MAXIMIZADA

        # ** Cojo el tamaño de mi pantalla y hago el calculo para pintar la ventana en medio **
        screen_width = self.app.winfo_screenwidth()
        screen_height = self.app.winfo_screenheight()
        
        # Para que este a pantalla completa 
        #self.app.geometry("%dx%d" % (screen_width, screen_height))
        
        # Esto de abajo para si la quiero de X tamaño y centrada
        window_width = screen_width - 10
        window_height = screen_height - 100
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2) - 35
        self.app.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        
    def toggleFullScreen(self, event):
        self.fullScreenState = not self.fullScreenState
        self.app.attributes("-fullscreen", self.fullScreenState)

    def quitFullScreen(self, event):
        self.fullScreenState = False
        self.app.attributes("-fullscreen", self.fullScreenState)
        
    def generar_frame_izquierda(self):
        # **********************************************
        # ** FRAME + BOTONES DE GRABACION SERIAL PORT **
        # **********************************************
        
        self.frame_izquierda = ctk.CTkFrame(master=self.frame_principal, width=600, height=400, corner_radius=10)
        self.frame_izquierda.pack(side="left", padx=20, pady=30)

        # Pinto los paneles superior e inferior
        self.generar_frame_izq_sup()
        self.generar_frame_izq_inf()

    def generar_frame_izq_sup(self):
        # Frame superior
        self.frame_superior = ctk.CTkFrame(master=self.frame_izquierda, width=600, height=200, corner_radius=10)
        self.frame_superior.pack(side="top", padx=20, pady=10, fill="both", expand=True)

        # Crear un frame para las barras de progreso
        self.frame_barras = ctk.CTkFrame(master=self.frame_superior, fg_color="transparent")
        self.frame_barras.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Crear y configurar las barras de progreso
        self.barras = []
        self.valores = []
        for i in range(5):
            # Label para mostrar el valor numérico
            valor = tk.Label(self.frame_barras, text="000", font=("Arial", 12, "bold"), width=3, anchor="center")
            valor.grid(row=0, column=i, padx=18, pady=5, sticky="ew")
            self.valores.append(valor)

            # Barra de progreso vertical
            barra = ttk.Progressbar(self.frame_barras, orient="vertical", length=200, mode="determinate", maximum=400)
            barra.grid(row=1, column=i, padx=20, pady=5, sticky="nsew")
            self.barras.append(barra)

        # Crear el Textarea
        self.tk_textarea = tk.Text(self.frame_superior, height=10, width=45, background='white',
                                   highlightthickness=0)
        self.tk_textarea.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        ctk_scroll = ctk.CTkScrollbar(self.frame_superior, command=self.tk_textarea.yview)
        ctk_scroll.grid(row=0, column=2, sticky="ns")
        self.tk_textarea.configure(yscrollcommand=ctk_scroll.set)

    def generar_frame_izq_inf(self):
        # Frame inferior
        self.frame_inferior = ctk.CTkFrame(master=self.frame_izquierda, width=600, height=200, corner_radius=10)
        self.frame_inferior.pack(side="top", padx=20, pady=10, fill="both", expand=True)

        # Genero un nuevo frame para colocar los botones
        self.button_frame = ctk.CTkFrame(master=self.frame_inferior, fg_color="transparent")
        self.button_frame.grid(row=0, column=0, columnspan=3, pady=20)

        # Genero los botones / Grabar - Parar - Generar
        self.btn_grabar = ctk.CTkButton(master=self.button_frame, text="Grabar", font=("Arial", 15, "bold"), width=120,
                                        height=45, command=self.funcion_grabar)
        self.btn_grabar.pack(side="left", padx=20)

        self.btn_parar = ctk.CTkButton(master=self.button_frame, text="Detener", font=("Arial", 15, "bold"), width=120, height=45, command=self.funcion_detener)
        self.btn_parar.pack(side="left", padx=20)

        self.btn_generar = ctk.CTkButton(master=self.button_frame, text="Generar", font=("Arial", 15, "bold"),
                                         width=120, height=45, command=self.funcion_generar)
        self.btn_generar.pack(side="left", padx=20)



    def generar_frame_derecha(self):
         # ***************************************
        # ** FRAME TRANSFORMACION DE ABECEDARIO **
        # ****************************************
        self.frame_derecha = ctk.CTkFrame(master=self.frame_principal, width=600, height=400, corner_radius=10)
        self.frame_derecha.pack(side="right", padx=25, pady=30)

        # Ruta de imagenes y total de botones
        images_path = "./images"
        num_botones = 27

        # Crear botones en rejilla
        for i in range(num_botones):
            # Calcular posición en la rejilla
            fila = i // 5
            columna = i % 5

            # Nombre del archivo de imagen
            image_filename = f"{i}.png"
            image_path = os.path.join(images_path, image_filename)

            # Cargar la imagen y crear un objeto ImageTk para Tkinter
            img = Image.open(image_path)
            img = img.resize((120, 70), Image.LANCZOS)  # Cambio a Image.LANCZOS para el escalado
            img_tk = ImageTk.PhotoImage(img)
            # img_tk = ctk.CTkImage(light_image=img) # Se hace pequeña con este en vez lo de arriba

            # Crear el botón con la imagen
            btn = ctk.CTkButton(master=self.frame_derecha, image=img_tk, text="", width=120, height=60, bg_color="transparent", command=lambda index=i: self.on_button_click(index))
            btn.image = img_tk  # Guardar una referencia a la imagen para evitar que sea eliminada por el recolector de basura
            btn.grid(row=fila, column=columna, padx=5, pady=5)

            # Configurar la imagen en el botón
            btn.configure(image=img_tk)
            btn.image = img_tk

    def on_button_click(self, index):
        abecedario = "abcdefghijklmnñopqrstuvwxyz"
        print(f"Letra asignada: {abecedario[index]}")
        self.letra = abecedario[index]

    def generar_frame3(self):
        # ************************************************
        # ** CREO EL FRAME QUE VA A CONTENER LA LECTURA **
        # ************************************************
        self.frame_config = ctk.CTkFrame(master=self.frame_footer, width=self.app.winfo_screenwidth()/2, height=80, corner_radius=30)
        self.frame_config.pack(padx=50, pady=0, expand=True, fill="both")

        # Genero el frame centrado
        self.frame_config_center = ctk.CTkFrame(master=self.frame_config, fg_color="transparent", corner_radius=30)
        self.frame_config_center.pack(fill="both", expand=True)

        # Crear el Textarea centrado dentro de self.frame_config_center
        self.tk_textarea2 = tk.Text(self.frame_config_center, background='white', highlightthickness=0, height=5, width=50)
        self.tk_textarea2.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Configurar el peso de la fila y columna para que el Textarea se expanda correctamente
        self.frame_config_center.grid_rowconfigure(0, weight=1)
        self.frame_config_center.grid_columnconfigure(0, weight=1)

    def buscar_puertos(self):
        # Metodo par repintar el combo con los nuevos puertos activos
        puertos = self.obtener_puertos_COM_activos()
        self.combobox_puerto['values'] = ()
        self.combobox_puerto.configure(values=puertos)

    def obtener_puertos_COM_activos(self):
        # Metodo para buscar los los puertos activos
        puertos_activos = []
        for puerto in serial.tools.list_ports.comports():
            puertos_activos.append(puerto.device)
        return puertos_activos
        
    def generar_frame4(self):
        # **********************************************
        # ** CREO EL FRAME QUE VA A PERMITIR EXPORTAR **
        # **********************************************
        
        self.frame_export = ctk.CTkFrame(master=self.frame_footer, width=self.app.winfo_screenwidth()/2, height=80,
                                         corner_radius=10)
        self.frame_export.pack(padx=50, pady=20, expand=True, fill="both")
        
        # Genero el frame centrado
        self.frame_export_center = ctk.CTkFrame(master=self.frame_export, fg_color="transparent")
        self.frame_export_center.pack(expand=True)
        self.frame_export_center.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Label  Puerto
        etiqueta_puerto = ctk.CTkLabel(master=self.frame_export_center, text="puerto", corner_radius=8,
                                       font=("Arial", 15, "bold"))
        etiqueta_puerto.pack(side="left", padx=20)
        etiqueta_puerto.configure(text="PUERTO:")

        # Genero el combo de los puertos activos
        puertos = self.obtener_puertos_COM_activos()
        self.combobox_puerto = ctk.CTkComboBox(master=self.frame_export_center, values=puertos, state="readonly")
        self.combobox_puerto.pack(side="left", padx=20)

        # Cargo la imagen que va a tener el boton buscar
        imagen_path = os.path.join(os.path.dirname(__file__), "./icons/buscar.png")
        imagen = ctk.CTkImage(light_image=Image.open(imagen_path), size=(20, 20))

        # Boton para recargar puertos activos
        btn_buscar = ctk.CTkButton(master=self.frame_export_center, image=imagen, text="", font=("Arial", 15, "bold"),
                                   width=45, height=45, command=self.buscar_puertos)
        btn_buscar.pack(side="left", padx=20)

        # Label Baudios
        etiqueta_baud = ctk.CTkLabel(master=self.frame_export_center, text="baud", corner_radius=8,
                                     font=("Arial", 15, "bold"))
        etiqueta_baud.pack(side="left", padx=20)
        etiqueta_baud.configure(text="BAUDIOS:")

        # Genero el combo de los baudios
        self.combobox_baud = ctk.CTkComboBox(master=self.frame_export_center, values=[str(value) for value in
                                                                                      [300, 600, 750, 1200, 2400, 4800,
                                                                                       9600, 19200, 31250, 38400, 57600,
                                                                                       74880, 115200, 230400, 250000,
                                                                                       460800, 500000, 921600, 1000000,
                                                                                       2000000]], state="readonly")
        self.combobox_baud.pack(side="left", padx=20)

        # Genero boton exportar
        self.btn_export = ctk.CTkButton(master=self.frame_export_center, text="Exportar", font=("Arial", 15, "bold"),
                                        width=120, height=45, command=self.funcion_exportar)
        self.btn_export.pack(side="left", padx=20)
        self.btn_export.configure(state="disabled")
        
              
    def funcion_grabar(self):
        print("Función grabar")
        self.tk_textarea.delete('1.0', tk.END)
        puerto = self.combobox_puerto.get()
        baud = self.combobox_baud.get()
        err = ""
        if puerto == "":
            err = err + "El Puerto "
        if baud == "":
            if err != "":
                err = err + "y los Baudios"
            else:
                err = err + "Los Baudios"
        if err != "":
            print("Error: "+err)
            self.mostrar_mensaje("Error", "Seleccione: "+err)
        else:
            print("Valor seleccionado:", puerto)
            print("Valor seleccionado:", baud)

            self.btn_grabar.configure(state="disabled")
            self.btn_parar.configure(state="normal")
            self.btn_generar.configure(state="disabled")

            ## Comienzo a leer puerto serie
            try:
                self.serial_reader = serial.Serial(port=puerto, baudrate=baud)
                self.leer_puerto_serie(self.serial_reader)
                self.btn_grabar.configure(state="disabled")
                self.btn_generar.configure(state="normal")
            except serial.SerialException as e:
                print(f"Error al abrir el puerto serie: {e}")


    def leer_puerto_serie(self, serial_reader = None):
        datos = [[] for _ in range(5)]
        acelera = []
        for _ in range(6):
            try:
                texto_recibido = serial_reader.readline().decode('utf-8', errors='ignore').strip()
                valores = texto_recibido.split(';')
                for i in range(5):
                    datos[i].append(float(valores[i]))
                acelera.append(valores[5])
            except Exception as e:
                print(f"Error leyendo el puerto serie: {e}")
        print(datos)
        print(acelera)
        self.funcion_detener()
        self.mediaDedos = [sum(d) / len(d) if d else 0 for d in datos]
        data_matrix = [list(map(float, row.split(','))) for row in acelera]
        transposed_data = list(zip(*data_matrix))
        self.accelerometro = [sum(column) for column in transposed_data]
        self.actualizar_barras_progreso()
        self.actualizar_textarea()
        print("Lecturas dedos: ")
        print(self.mediaDedos)
        print("Lecturas accelerometro: ")
        print(self.accelerometro)

    def actualizar_barras_progreso(self):
        print("Actualizando barras de progreso con los datos leidos...")
        for i, media in enumerate(self.mediaDedos):
            self.barras[i].config(value=media)
            self.valores[i].config(text=str(media))

    def actualizar_textarea(self):
        for dato in self.accelerometro:
            self.tk_textarea.insert(tk.END, f"{dato}\n")

    def funcion_detener(self):
        print("Función detener")
        if self.serial_reader.is_open:
            self.serial_reader.close()

        self.btn_grabar.configure(state="normal")
        if self.tk_textarea.get("1.0", "end-1c"):
            self.btn_generar.configure(state="normal")


    def funcion_generar(self):
        print("Función generar")
        if len(self.mediaDedos) > 0 and len(self.accelerometro) > 0 and self.letra != "":
            self.tk_textarea2.delete('1.0', tk.END)
            dedos = ""
            for i, dato in enumerate(self.mediaDedos):
                print(str(round(dato, 2)))
                dedos = dedos + str(round(dato, 2))+","
            accelerometro = ""
            for i, dato in enumerate(self.accelerometro):
                print(str(round(dato, 2)))
                accelerometro = accelerometro + str(round(dato, 2))+";"
            self.tk_textarea2.insert(tk.END, f"{self.letra},{dedos}{accelerometro[:-1]}\n")
        else:
            err = ""
            if self.letra == "":
                err = err + "La letra"
            if len(self.mediaDedos) == 0:
                if err != "":
                    err = err + ", las lecturas de los dedos"
                else:
                    err = err + "Las lecturas de los dedos"
            if len(self.accelerometro) == 0:
                if err != "":
                    err = err + " y las lecturas del accelerometro"
                else:
                    err = err + "Las lecturas del accelerometro"
            self.mostrar_mensaje("Error", "Faltan los datos: " + err)

        self.btn_export.configure(state="normal")

        # contenido = self.tk_textarea.get("1.0", tk.END)
        # filas = contenido.strip().split('\n')
        # datos = [list(map(float, fila.split(';'))) for fila in filas]
        # Convertir los datos a un arreglo de NumPy
        # datos_np = np.array(datos)
        # self.grafica_fourier.datos_procesados = datos_np
        # self.grafica_fourier.pintar_grafica(self.frame_derecha)

    """Obtiene los valores de los checkboxes seleccionados."""
    def funcion_exportar(self):
        print("Exportando datos")
        with open(f"{self.letra}.csv", 'w') as f:
            f.write(f"{self.tk_textarea2.get("1.0", "end-1c")}\n")

    
    def mostrar_mensaje(self, msgTipe, msgContent):
        tk.messagebox.showinfo(msgTipe, msgContent)


ventana = Ventana()
ventana.run()