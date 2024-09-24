import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
import socket
import time

# URL base de la API externa
API_URL = 'https://66eb01db55ad32cda47b4ea1.mockapi.io/IoTCarStatus'


# Función para obtener la IP del dispositivo
def get_device_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address


# Función para obtener la fecha actual en formato de timestamp
def get_current_timestamp():
    return int(time.time())


# Función para crear un nuevo registro en la API
def create_car_status():
    name = entry_name.get()

    if not name:
        messagebox.showerror("Error", "El campo de nombre es obligatorio.")
        return

    ip_client = get_device_ip()
    date = get_current_timestamp()

    data = {
        "name": name,
        "date": date,
        "ipClient": ip_client
    }

    response = requests.post(API_URL, json=data)

    if response.status_code == 201:
        created_record = response.json()
        new_id = created_record["id"]
        status = f"status {new_id}"
        update_data = {"status": status}
        update_response = requests.put(f"{API_URL}/{new_id}", json=update_data)

        if update_response.status_code == 200:
            messagebox.showinfo("Éxito", "Estado del auto creado y actualizado exitosamente.")
            entry_name.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "No se pudo actualizar el estado del auto.")
    else:
        messagebox.showerror("Error", "No se pudo crear el estado del auto.")


# Función para mostrar los últimos 10 registros secuenciales según el ID
def show_last_10_records():
    # Obtener los registros ordenados por ID en orden descendente y limitar a 10
    response = requests.get(f"{API_URL}?sortBy=id&order=desc&limit=10")

    if response.status_code == 200:
        records = response.json()

        # Revertimos la lista para mostrar los IDs en orden descendente (de mayor a menor)
        records_text = "\n\n".join(
            [
                f"ID: {r['id']}\n"
                f"Status: {r['status']}\n"
                f"Date: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(r['date']))}\n"
                f"IP: {r['ipClient']}\n"
                f"Name: {r['name']}"
                for r in sorted(records, key=lambda x: int(x['id']), reverse=True)
            ]
        )

        # Mostrar los registros en una ventana emergente con un campo de texto desplazable
        records_window = tk.Toplevel(root)
        records_window.title("Últimos 10 Registros")

        text_area = scrolledtext.ScrolledText(records_window, wrap=tk.WORD, width=50, height=20)
        text_area.pack(padx=10, pady=10)
        text_area.insert(tk.END, records_text)
        text_area.configure(state='disabled')  # Hacer que el campo sea de solo lectura
    else:
        messagebox.showerror("Error", "No se pudieron obtener los registros.")


# Configuración de la ventana principal de Tkinter
root = tk.Tk()
root.title("Inyección de datos - IoTCarStatus")

label_name = tk.Label(root, text="Ingresa el Nombre:")
label_name.grid(row=0, column=0, padx=10, pady=10)
entry_name = tk.Entry(root)
entry_name.grid(row=0, column=1, padx=10, pady=10)

btn_submit = tk.Button(root, text="Crear Estado", command=create_car_status)
btn_submit.grid(row=1, columnspan=2, pady=10)

btn_show_records = tk.Button(root, text="Ver Últimos 10 Registros", command=show_last_10_records)
btn_show_records.grid(row=2, columnspan=2, pady=10)

root.mainloop()