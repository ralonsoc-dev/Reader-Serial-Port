import tkinter as tk
import customtkinter as ctk
import serial.tools.list_ports
from PIL import Image
import os

seleccionados = []

class Ventana(object):
    def __init__(self):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.app = ctk.CTk()
        self.app.title("Grabadora de Puerto Serie")

        # ** Cojo el tamaño de mi pantalla y hago el calculo para pintar la ventana en medio **
        screen_width = self.app.winfo_screenwidth()
        screen_height = self.app.winfo_screenheight()
        window_width = 1200
        window_height = 700
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)
        self.app.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")


        self.opc_menu_puerto = ctk.StringVar(value="")
        self.opc_menu_baud = ctk.StringVar(value="")
        self.generar_frame1()
        self.generar_frame2()
        self.generar_frame3()
        
        
        
        
        
        
        
    def run(self):
        self.app.mainloop()

    def generar_frame1(self):
        # **********************************************
        # ** FRAME + BOTONES DE GRABACION SERIAL PORT **
        # **********************************************
        
        self.frame = ctk.CTkFrame(master=self.app, width=600, height=400, corner_radius=10)
        self.frame.pack(padx=20, pady=30)

        # Genero el Textarea
        self.tk_textarea = tk.Text(self.frame, height=20, width=70, background='white', highlightthickness=0)
        self.tk_textarea.grid(row=0, column=0, sticky="nsew")
        ctk_scroll = ctk.CTkScrollbar(self.frame, command=self.tk_textarea.yview)
        ctk_scroll.grid(row=0, column=1, sticky="ns")
        self.tk_textarea.configure(yscrollcommand=ctk_scroll.set)

        # Genero un nuevo frame para colocar los botones
        self.button_frame = ctk.CTkFrame(master=self.frame,  fg_color="transparent")
        self.button_frame.grid(row=1, column=0, columnspan=3, pady=20)
        
        # Genero los botones
        btn_grabar = ctk.CTkButton(master=self.button_frame, text="Grabar", font=("Arial", 15, "bold"), width=120, height=45, command=self.funcion_grabar)
        btn_grabar.pack(side="left", padx=20)

        btn_parar = ctk.CTkButton(master=self.button_frame, text="Detener", font=("Arial", 15, "bold"), width=120, height=45, command=self.funcion_detener)
        btn_parar.pack(side="left", padx=20)

        btn_guardar = ctk.CTkButton(master=self.button_frame, text="Guardar", font=("Arial", 15, "bold"), width=120, height=45, command=self.funcion_guardar)
        btn_guardar.pack(side="left", padx=20)
      
    def generar_frame2(self):
        # ************************************************
        # ** CREO EL FRAME QUE VA A PERMITIR CONFIGURAR **
        # ************************************************
        
        self.frame_config = ctk.CTkFrame(master=self.app, width=100, height=50, corner_radius=10)
        self.frame_config.pack(padx=50, pady=20, expand=True, fill="both")
        
        # Genero el frame centrado
        self.frame_config_center = ctk.CTkFrame(master=self.frame_config, fg_color="transparent")
        self.frame_config_center.pack(expand=True)
        self.frame_config_center.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Genero el label del Puerto
        etiqueta_puerto = ctk.CTkLabel(master=self.frame_config_center, text="puerto", corner_radius=8, font=("Arial", 15, "bold"))
        etiqueta_puerto.pack(side="left", padx=20)
        etiqueta_puerto.configure(text="Puerto:")
        
        puertos = self.obtener_puertos_COM_activos()
        self.combobox_puerto = ctk.CTkComboBox(master=self.frame_config_center, values=puertos, variable=self.opc_menu_puerto, state="readonly")
        self.combobox_puerto.pack(side="left", padx=20)
        
        # Cargo la imagen que va a tener el boton buscar
        imagen_path = os.path.join(os.path.dirname(__file__), "./icons/buscar.png")
        imagen = ctk.CTkImage(light_image=Image.open(imagen_path), size=(20, 20) )

        # Genero boton buscar mas puertos
        btn_buscar = ctk.CTkButton(master=self.frame_config_center, image=imagen, text="", font=("Arial", 15, "bold"), width=45, height=45, command=self.buscar_puertos)
        btn_buscar.pack(side="left", padx=20)
        
        # Genero el label del Bauld
        etiqueta_baud = ctk.CTkLabel(master=self.frame_config_center, text="baud", corner_radius=8, font=("Arial", 15, "bold"))
        etiqueta_baud.pack(side="left", padx=20)
        etiqueta_baud.configure(text="Baud:")
        
        combobox_baud = ctk.CTkComboBox(master=self.frame_config_center, values=[str(value) for value in [300, 600, 750, 1200, 2400, 4800, 9600, 19200, 31250, 38400, 57600, 74880, 115200, 230400, 250000, 460800, 500000, 921600, 1000000, 2000000]], variable=self.opc_menu_baud, state="readonly")
        combobox_baud.pack(side="left", padx=20)
    
    def buscar_puertos(self):
        puertos = self.obtener_puertos_COM_activos()
        self.combobox_puerto._values = puertos
        print(self.combobox_puerto._values)
        self.combobox_puerto.update()
    
    def obtener_puertos_COM_activos(self):
        puertos_activos = []
        for puerto in serial.tools.list_ports.comports():
            puertos_activos.append(puerto.device)
        return puertos_activos
        
    def generar_frame3(self):
        # **********************************************
        # ** CREO EL FRAME QUE VA A PERMITIR EXPORTAR **
        # **********************************************
        
        self.frame_export = ctk.CTkFrame(master=self.app, width=100, height=50, corner_radius=10)
        self.frame_export.pack(padx=50, pady=20, expand=True, fill="both")
        
        # Genero el frame centrado
        self.frame_export_center = ctk.CTkFrame(master=self.frame_export, fg_color="transparent")
        self.frame_export_center.pack(expand=True)
        self.frame_export_center.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Genero el label
        etiqueta = ctk.CTkLabel(master=self.frame_export_center, text="Exportar a:", corner_radius=8, font=("Arial", 15, "bold"))
        etiqueta.pack(side="left", padx=20)
        etiqueta.configure(text="EXPORTAR A:")
        
        # Genero los checkbox
        checkbox_txt = ctk.CTkCheckBox(master=self.frame_export_center, text="TXT")
        checkbox_txt.place(relx = 0.55, rely = 0.4, anchor=tk.CENTER)
        checkbox_txt.pack(side="left", padx=20)
        
        checkbox_csv = ctk.CTkCheckBox(master=self.frame_export_center, text="CSV")
        checkbox_csv.place(relx = 0.55, rely = 0.5, anchor=tk.CENTER)
        checkbox_csv.pack(side="left", padx=20)
        
        checkbox_hex = ctk.CTkCheckBox(master=self.frame_export_center, text="HEX")
        checkbox_hex.place(relx = 0.55, rely = 0.5, anchor=tk.CENTER)
        checkbox_hex.pack(side="left", padx=20)
        
        # Genero boton exportar
        btn_export = ctk.CTkButton(master=self.frame_export_center, text="Exportar", font=("Arial", 15, "bold"), width=120, height=45, command=self.funcion_exportar)
        btn_export.pack(side="left", padx=20)
        
          
    def funcion_grabar(self):
        print("Función grabar")

    def funcion_detener(self):
        print("Función detener")

    def funcion_guardar(self):
        print("Función guardar")

    def funcion_exportar(self):
        """Obtiene los valores de los checkboxes seleccionados."""
        global seleccionados

        seleccionados = []
        
        # Recorre todos los checkboxes
        for checkbox in self.frame_export_center.winfo_children():
            if isinstance(checkbox, ctk.CTkCheckBox) and checkbox.get() == True:
                seleccionados.append(checkbox._text)

        print("Seleccionados:", seleccionados)
    
ventana = Ventana()
ventana.run()