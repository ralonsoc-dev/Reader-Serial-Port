import tkinter as tk
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

        # Genero el Textarea
        self.tk_textarea = tk.Text(self.frame_izquierda, height=26, width=70, background='white', highlightthickness=0)
        self.tk_textarea.grid(row=0, column=0, sticky="nsew")
        ctk_scroll = ctk.CTkScrollbar(self.frame_izquierda, command=self.tk_textarea.yview)
        ctk_scroll.grid(row=0, column=1, sticky="ns")
        self.tk_textarea.configure(yscrollcommand=ctk_scroll.set)

        # Genero un nuevo frame para colocar los botones
        self.button_frame = ctk.CTkFrame(master=self.frame_izquierda,  fg_color="transparent")
        self.button_frame.grid(row=1, column=0, columnspan=3, pady=20)
        
        # Genero los botones / Grabar - Parar - Generar
        self.btn_grabar = ctk.CTkButton(master=self.button_frame, text="Grabar", font=("Arial", 15, "bold"), width=120, height=45, command=self.funcion_grabar)
        self.btn_grabar.pack(side="left", padx=20)

        # self.btn_parar = ctk.CTkButton(master=self.button_frame, text="Detener", font=("Arial", 15, "bold"), width=120, height=45, command=self.funcion_detener)
        # self.btn_parar.pack(side="left", padx=20)

        self.btn_generar = ctk.CTkButton(master=self.button_frame, text="Generar", font=("Arial", 15, "bold"), width=120, height=45, command=self.funcion_generar)
        self.btn_generar.pack(side="left", padx=20)

        # self.btn_parar.configure(state="disabled")
        # self.btn_generar.configure(state="disabled")

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

    def generar_frame3(self):
        # ************************************************
        # ** CREO EL FRAME QUE VA A PERMITIR CONFIGURAR **
        # ************************************************
        self.frame_config = ctk.CTkFrame(master=self.frame_footer, width=self.app.winfo_screenwidth()/2, height=80, corner_radius=10)
        self.frame_config.pack(padx=50, pady=0, expand=True, fill="both")

        # Genero el frame centrado
        self.frame_config_center = ctk.CTkFrame(master=self.frame_config, fg_color="transparent")
        self.frame_config_center.pack(expand=True)
        self.frame_config_center.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Label  Puerto
        etiqueta_puerto = ctk.CTkLabel(master=self.frame_config_center, text="puerto", corner_radius=8, font=("Arial", 15, "bold"))
        etiqueta_puerto.pack(side="left", padx=20)
        etiqueta_puerto.configure(text="PUERTO:")

        # Genero el combo de los puertos activos
        puertos = self.obtener_puertos_COM_activos()
        self.combobox_puerto = ctk.CTkComboBox(master=self.frame_config_center, values=puertos, state="readonly")
        self.combobox_puerto.pack(side="left", padx=20)

        # Cargo la imagen que va a tener el boton buscar
        imagen_path = os.path.join(os.path.dirname(__file__), "./icons/buscar.png")
        imagen = ctk.CTkImage(light_image=Image.open(imagen_path), size=(20, 20) )

        # Boton para recargar puertos activos
        btn_buscar = ctk.CTkButton(master=self.frame_config_center, image=imagen, text="", font=("Arial", 15, "bold"), width=45, height=45, command=self.buscar_puertos)
        btn_buscar.pack(side="left", padx=20)

        # Label Baudios
        etiqueta_baud = ctk.CTkLabel(master=self.frame_config_center, text="baud", corner_radius=8, font=("Arial", 15, "bold"))
        etiqueta_baud.pack(side="left", padx=20)
        etiqueta_baud.configure(text="BAUDIOS:")

        # Genero el combo de los baudios
        self.combobox_baud = ctk.CTkComboBox(master=self.frame_config_center, values=[str(value) for value in [300, 600, 750, 1200, 2400, 4800, 9600, 19200, 31250, 38400, 57600, 74880, 115200, 230400, 250000, 460800, 500000, 921600, 1000000, 2000000]], state="readonly")
        self.combobox_baud.pack(side="left", padx=20)

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
        
        self.frame_export = ctk.CTkFrame(master=self.frame_footer, width=self.app.winfo_screenwidth()/2, height=80, corner_radius=10)
        self.frame_export.pack(padx=50, pady=20, expand=True, fill="both")
        
        # Genero el frame centrado
        self.frame_export_center = ctk.CTkFrame(master=self.frame_export, fg_color="transparent")
        self.frame_export_center.pack(expand=True)
        self.frame_export_center.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Genero el label
        etiqueta = ctk.CTkLabel(master=self.frame_export_center, text="Exportar a:", corner_radius=8, font=("Arial", 15, "bold"))
        etiqueta.pack(side="left", padx=20)
        etiqueta.configure(text="EXPORTAR A:")

        # Variable para el radio button
        self.radio_var = tk.StringVar(value="CSV")

        # Genero el RadioButton
        self.radio_csv = ctk.CTkRadioButton(
            master=self.frame_export_center,
            text="CSV",
            variable=self.radio_var,
            value="CSV"
        )
        self.radio_csv.place(relx = 0.55, rely = 0.4, anchor=tk.CENTER)
        self.radio_csv.pack(side="left", padx=20)

        # Genero boton exportar
        self.btn_export = ctk.CTkButton(master=self.frame_export_center, text="Exportar", font=("Arial", 15, "bold"), width=120, height=45, command=self.funcion_exportar)
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
            # self.btn_parar.configure(state="normal")
            self.btn_generar.configure(state="disabled")
        
            ## Comienzo a leer puerto serie
            self.detener_lectura = False
            self.serial_reader = serial.Serial(port=puerto, baudrate=baud)
            self.hilo_lectura = threading.Thread(target=self.leer_puerto_serie, args=(self.serial_reader,))
            self.hilo_lectura.start()

    def leer_puerto_serie(self, serial_reader = None):
        while not self.detener_lectura:
            if serial_reader.in_waiting > 0:
                texto_recibido = serial_reader.readline().decode('utf-8', errors='ignore').strip()
                print(texto_recibido)
                self.tk_textarea.insert(tk.END, texto_recibido + '\n')
                self.tk_textarea.see(tk.END)     

    def funcion_detener(self):
        self.detener_lectura = True
        if self.hilo_lectura and self.hilo_lectura.is_alive():
            self.hilo_lectura.join() 
        self.serial_reader.close()
        print("Función detener")
        self.btn_grabar.configure(state="normal")
        if self.tk_textarea.get("1.0", "end-1c"):
            self.btn_generar.configure(state="normal")
        

    def funcion_generar(self):
        print("Función guardar")
        contenido = self.tk_textarea.get("1.0", tk.END)  
        filas = contenido.strip().split('\n')
        datos = [list(map(float, fila.split(';'))) for fila in filas]
        self.btn_export.configure(state="normal")

        # Convertir los datos a un arreglo de NumPy
        datos_np = np.array(datos)
        self.grafica_fourier.datos_procesados = datos_np
        self.grafica_fourier.pintar_grafica(self.frame_derecha)

    """Obtiene los valores de los checkboxes seleccionados."""
    def funcion_exportar(self):
        print("Exportando datos")
        if self.radio_var.get() == "CSV":
            self.grafica_fourier.exportar_txt("CSV")

    
    def mostrar_mensaje(self, msgTipe, msgContent):
        tk.messagebox.showinfo(msgTipe, msgContent)


ventana = Ventana()
ventana.run()