import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class grafica_fourier(object):
    def __init__(self):
        self.datos_procesados = []
        self.datos_procesados1 = [[1, 2, 3, 4, 5, 4, 3, 2, 1], [1, 2, 3, 4, 5, 4, 3, 2, 1]]
        self.transformada = None
        
    
    def pintar_grafica1(self, frame_derecha):
        if len(self.datos_procesados) > 0:
            self.transformada = np.fft.fft(self.datos_procesados)
        
        # Creo la figura
        fig = Figure(figsize=(7, 5), dpi=100)
        ax = fig.add_subplot(111)
        if self.transformada is not None:
            ax.plot(np.abs(self.transformada))
        ax.set_xlabel('Frecuencia')
        ax.set_ylabel('Amplitud')
        ax.set_title('Transformada de Fourier')

        # Creo un canvas para mostrar la transformada
        canvas = FigureCanvasTkAgg(fig, master=frame_derecha)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def pintar_grafica(self, frame_derecha):
        if len(self.datos_procesados) > 0:
            suma_datos = np.sum(self.datos_procesados, axis=0)
            self.transformada = np.fft.fft(suma_datos)
        
        # Creo la figura
        fig = Figure(figsize=(7, 5), dpi=100)
        ax = fig.add_subplot(111)
        if self.transformada is not None:
            ax.plot(np.abs(self.transformada))
        ax.set_xlabel('Frecuencia')
        ax.set_ylabel('Amplitud')
        ax.set_title('Transformada de Fourier')

        for widget in frame_derecha.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=frame_derecha)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def exportar_txt(self, extension):
        with open("datos."+extension, 'w') as f:
            for dato in self.transformada:
                f.write(f"{dato}\n")
    
    def exportar_hex(self):
        with open("hexadecimal.txt", 'w') as f:
            for dato in self.transformada:
                parte_real_hex = int(dato.real).to_bytes(8, byteorder='big').hex()
                parte_imaginaria_hex = int(dato.imag).to_bytes(8, byteorder='big').hex()
                f.write(f"{parte_real_hex},{parte_imaginaria_hex}\n")