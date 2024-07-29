import os
from tkinter import Tk, messagebox
from tkinter.filedialog import askopenfilenames, asksaveasfilename

def merge_txt_files(file_paths, output_file):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for file_path in file_paths:
            with open(file_path, 'r', encoding='utf-8') as infile:
                outfile.write(infile.read())
                outfile.write('\n')
            print(f'Archivo combinado: {file_path}')
    print(f'Contenido combinado en {output_file}')

def main():
    root = Tk()
    root.withdraw()

    messagebox.showinfo("Instrucciones", "Por favor, selecciona los archivos .txt que deseas combinar.")
    file_paths = askopenfilenames(
        title="Selecciona los archivos .txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if not file_paths:
        messagebox.showerror("Error", "No se seleccionaron archivos.")
        return

    messagebox.showinfo("Instrucciones", "Por favor, selecciona el archivo de salida donde se guardará el contenido combinado.")
    output_file = asksaveasfilename(
        title="Guardar archivo como",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if not output_file:
        messagebox.showerror("Error", "No se seleccionó ningún archivo de salida.")
        return

    merge_txt_files(file_paths, output_file)
    messagebox.showinfo("Éxito", f'Contenido combinado en {output_file}')

if __name__ == "__main__":
    main()
