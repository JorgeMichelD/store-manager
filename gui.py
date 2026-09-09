import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

def ruta_recurso(nombre_archivo):
    if getattr(sys, "frozen", False):
        carpeta_base = sys._MEIPASS
    else:
        carpeta_base = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(carpeta_base, nombre_archivo)

from database import conexion, cursor


# =============================================
# PALETA DE COLORES
# =============================================

COLOR_FONDO = "#F1CE8A"
COLOR_ROJO = "#83311F"
COLOR_VERDE = "#356B45"
COLOR_AMARILLO = "#E8A027"
COLOR_CREMA = "#F4DDAA"
COLOR_BLANCO = "#FFF8E7"


# =============================================
# VENTANA PRINCIPAL
# =============================================

ventana = tk.Tk()

ventana.title("Market al Paso")
ventana.geometry("1100x700")
ventana.minsize(900, 600)
ventana.configure(bg=COLOR_FONDO)


# =============================================
# ESTILOS
# =============================================

estilo = ttk.Style()

estilo.theme_use("clam")

estilo.configure(
    "Treeview",
    background=COLOR_BLANCO,
    fieldbackground=COLOR_BLANCO,
    foreground="#333333",
    rowheight=30,
    font=("Arial", 10)
)

estilo.configure(
    "Treeview.Heading",
    background=COLOR_ROJO,
    foreground="white",
    font=("Arial", 10, "bold")
)


# =============================================
# FUNCIONES
# =============================================

def limpiar_formulario():
    entrada_nombre.delete(0, tk.END)
    entrada_categoria.delete(0, tk.END)
    entrada_compra.delete(0, tk.END)
    entrada_venta.delete(0, tk.END)
    entrada_cantidad.delete(0, tk.END)


def cargar_productos():
    for item in tabla.get_children():
        tabla.delete(item)

    cursor.execute("""
        SELECT id, nombre, categoria, precio_compra,
               precio_venta, cantidad
        FROM productos
        ORDER BY id
    """)

    productos = cursor.fetchall()

    for producto in productos:
        tabla.insert("", tk.END, values=producto)

    actualizar_inventario()


def registrar_producto():
    nombre = entrada_nombre.get().strip()
    categoria = entrada_categoria.get().strip()
    compra = entrada_compra.get().strip()
    venta = entrada_venta.get().strip()
    cantidad = entrada_cantidad.get().strip()

    if not nombre or not categoria or not compra or not venta or not cantidad:
        messagebox.showwarning(
            "Datos incompletos",
            "Debes completar todos los campos."
        )
        return

    try:
        compra = float(compra)
        venta = float(venta)
        cantidad = int(cantidad)
    except ValueError:
        messagebox.showerror(
            "Error",
            "Precio debe ser número y cantidad debe ser entero."
        )
        return

    if compra < 0 or venta < 0 or cantidad < 0:
        messagebox.showerror(
            "Error",
            "Los valores no pueden ser negativos."
        )
        return

    if venta < compra:
        messagebox.showerror(
            "Error",
            "El precio de venta no puede ser menor al precio de compra."
        )
        return

    cursor.execute(
        "SELECT id FROM productos WHERE LOWER(nombre) = LOWER(?)",
        (nombre,)
    )

    if cursor.fetchone():
        messagebox.showwarning(
            "Producto existente",
            "Ya existe un producto con ese nombre."
        )
        return

    cursor.execute("""
        INSERT INTO productos
        (nombre, categoria, precio_compra, precio_venta, cantidad)
        VALUES (?, ?, ?, ?, ?)
    """, (nombre, categoria, compra, venta, cantidad))

    conexion.commit()

    limpiar_formulario()
    cargar_productos()

    messagebox.showinfo(
        "Producto registrado",
        "El producto fue registrado correctamente."
    )


def seleccionar_producto(event):
    seleccionado = tabla.selection()

    if not seleccionado:
        return

    valores = tabla.item(seleccionado[0], "values")

    limpiar_formulario()

    entrada_nombre.insert(0, valores[1])
    entrada_categoria.insert(0, valores[2])
    entrada_compra.insert(0, valores[3])
    entrada_venta.insert(0, valores[4])
    entrada_cantidad.insert(0, valores[5])


def modificar_producto():
    seleccionado = tabla.selection()

    if not seleccionado:
        messagebox.showwarning(
            "Selecciona un producto",
            "Selecciona un producto de la tabla."
        )
        return

    valores = tabla.item(seleccionado[0], "values")
    producto_id = valores[0]

    nombre = entrada_nombre.get().strip()
    categoria = entrada_categoria.get().strip()
    compra = entrada_compra.get().strip()
    venta = entrada_venta.get().strip()
    cantidad = entrada_cantidad.get().strip()

    if not nombre or not categoria or not compra or not venta or not cantidad:
        messagebox.showwarning(
            "Datos incompletos",
            "Completa todos los campos."
        )
        return

    try:
        compra = float(compra)
        venta = float(venta)
        cantidad = int(cantidad)
    except ValueError:
        messagebox.showerror(
            "Error",
            "Revisa los precios y la cantidad."
        )
        return

    if compra < 0 or venta < 0 or cantidad < 0:
        messagebox.showerror(
            "Error",
            "Los valores no pueden ser negativos."
        )
        return

    if venta < compra:
        messagebox.showerror(
            "Error",
            "El precio de venta no puede ser menor al precio de compra."
        )
        return

    cursor.execute("""
        UPDATE productos
        SET nombre = ?,
            categoria = ?,
            precio_compra = ?,
            precio_venta = ?,
            cantidad = ?
        WHERE id = ?
    """, (
        nombre,
        categoria,
        compra,
        venta,
        cantidad,
        producto_id
    ))

    conexion.commit()

    limpiar_formulario()
    cargar_productos()

    messagebox.showinfo(
        "Producto actualizado",
        "Los datos fueron actualizados correctamente."
    )


def eliminar_producto():
    seleccionado = tabla.selection()

    if not seleccionado:
        messagebox.showwarning(
            "Selecciona un producto",
            "Selecciona un producto de la tabla."
        )
        return

    valores = tabla.item(seleccionado[0], "values")

    producto_id = valores[0]
    nombre = valores[1]

    confirmar = messagebox.askyesno(
        "Confirmar eliminación",
        f"¿Deseas eliminar '{nombre}'?"
    )

    if not confirmar:
        return

    cursor.execute(
        "DELETE FROM productos WHERE id = ?",
        (producto_id,)
    )

    conexion.commit()

    limpiar_formulario()
    cargar_productos()

    messagebox.showinfo(
        "Producto eliminado",
        "El producto fue eliminado correctamente."
    )


def buscar_producto():
    texto = entrada_busqueda.get().strip()

    for item in tabla.get_children():
        tabla.delete(item)

    cursor.execute("""
        SELECT id, nombre, categoria, precio_compra,
               precio_venta, cantidad
        FROM productos
        WHERE LOWER(nombre) LIKE LOWER(?)
           OR LOWER(categoria) LIKE LOWER(?)
        ORDER BY id
    """, (f"%{texto}%", f"%{texto}%"))

    productos = cursor.fetchall()

    for producto in productos:
        tabla.insert("", tk.END, values=producto)



def registrar_venta():

    seleccionado = tabla.selection()
    if not seleccionado:
        messagebox.showwarning(
            "Selecciona un producto",
            "Selecciona el producto que deseas vender."
        )
        return

    valores = tabla.item(seleccionado[0], "values")

    producto_id = valores[0]
    nombre = valores[1]
    stock = int(valores[5])
    precio_compra = float(valores[3])
    precio_venta = float(valores[4])

    ventana_venta = tk.Toplevel(ventana)

    ventana_venta.title("Registrar venta")
    ventana_venta.geometry("350x300")
    ventana_venta.configure(bg=COLOR_FONDO)
    ventana_venta.resizable(False, False)

    tk.Label(
        ventana_venta,
        text=f"Producto: {nombre}",
        bg=COLOR_FONDO,
        fg=COLOR_ROJO,
        font=("Arial", 14, "bold")
    ).pack(pady=15)

    tk.Label(
        ventana_venta,
        text=f"Stock disponible: {stock}",
        bg=COLOR_FONDO
    ).pack()

    tk.Label(
        ventana_venta,
        text=f"Precio de venta: Bs {precio_venta:.2f}",
        bg=COLOR_FONDO
    ).pack(pady=(5, 0))

    tk.Label(
        ventana_venta,
        text="Cantidad a vender:",
        bg=COLOR_FONDO
    ).pack(pady=(15, 5))

    entrada_venta_cantidad = tk.Entry(
        ventana_venta,
        width=15
    )

    entrada_venta_cantidad.pack()


    def confirmar_venta():

        try:
            cantidad = int(entrada_venta_cantidad.get())

        except ValueError:
            messagebox.showerror(
                "Error",
                "La cantidad debe ser un número entero."
            )
            return


        if cantidad <= 0:
            messagebox.showerror(
                "Error",
                "La cantidad debe ser mayor que cero."
            )
            return


        if cantidad > stock:
            messagebox.showerror(
                "Stock insuficiente",
                "No hay suficiente stock disponible."
            )
            return


        # =============================================
        # CÁLCULOS DE LA VENTA
        # =============================================

        nuevo_stock = stock - cantidad

        total = cantidad * precio_venta

        ganancia = (precio_venta - precio_compra) * cantidad


        # =============================================
        # GUARDAR VENTA EN LA BASE DE DATOS
        # =============================================

        cursor.execute("""
            INSERT INTO ventas (
                producto_id,
                producto_nombre,
                cantidad,
                precio_compra,
                precio_venta,
                total,
                ganancia
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            producto_id,
            nombre,
            cantidad,
            precio_compra,
            precio_venta,
            total,
            ganancia
        ))


        # =============================================
        # ACTUALIZAR STOCK
        # =============================================

        cursor.execute("""
            UPDATE productos
            SET cantidad = ?
            WHERE id = ?
        """, (
            nuevo_stock,
            producto_id
        ))


        # =============================================
        # GUARDAR CAMBIOS
        # =============================================

        conexion.commit()


        # =============================================
        # ACTUALIZAR INTERFAZ
        # =============================================

        cargar_productos()

        ventana_venta.destroy()


        # =============================================
        # CONFIRMACIÓN
        # =============================================

        messagebox.showinfo(
            "Venta registrada",
            f"Venta registrada correctamente.\n\n"
            f"Producto: {nombre}\n"
            f"Cantidad: {cantidad}\n"
            f"Total: Bs {total:.2f}\n"
            f"Ganancia: Bs {ganancia:.2f}"
        )

    # =============================================
    # BOTÓN CONFIRMAR VENTA
    # =============================================

    tk.Button(
        ventana_venta,
        text="Confirmar venta",
        bg=COLOR_VERDE,
        fg="white",
        font=("Arial", 10, "bold"),
        command=confirmar_venta
    ).pack(pady=15)


def ver_historial_ventas():

    # =============================================
    # VENTANA DEL HISTORIAL
    # =============================================

    ventana_historial = tk.Toplevel(ventana)

    ventana_historial.title("Historial de ventas")
    ventana_historial.geometry("1000x600")
    ventana_historial.configure(bg=COLOR_FONDO)
    ventana_historial.minsize(900, 500)

    # =============================================
    # TÍTULO
    # =============================================

    tk.Label(
        ventana_historial,
        text="Historial de ventas",
        bg=COLOR_FONDO,
        fg=COLOR_ROJO,
        font=("Arial", 18, "bold")
    ).pack(pady=(15, 5))

    tk.Label(
        ventana_historial,
        text="Consulta y resumen de ventas",
        bg=COLOR_FONDO,
        fg="#333333",
        font=("Arial", 10)
    ).pack(pady=(0, 10))

    # =============================================
    # FILTROS
    # =============================================

    marco_filtros = tk.Frame(
        ventana_historial,
        bg=COLOR_FONDO
    )

    marco_filtros.pack(
        fill="x",
        padx=15,
        pady=(0, 10)
    )

    tk.Label(
        marco_filtros,
        text="Mostrar:",
        bg=COLOR_FONDO,
        fg=COLOR_ROJO,
        font=("Arial", 10, "bold")
    ).pack(side="left", padx=(0, 10))

    filtro_periodo = tk.StringVar(
        value="Todas"
    )

    opciones_periodo = [
        "Todas",
        "Hoy",
        "Esta semana",
        "Este mes"
    ]

    selector_periodo = ttk.Combobox(
        marco_filtros,
        textvariable=filtro_periodo,
        values=opciones_periodo,
        state="readonly",
        width=18
    )

    selector_periodo.pack(side="left")

    # =============================================
    # CONTENEDOR DE LA TABLA
    # =============================================

    marco_tabla = tk.Frame(
        ventana_historial,
        bg=COLOR_FONDO
    )

    marco_tabla.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=5
    )

    # =============================================
    # COLUMNAS
    # =============================================

    columnas_historial = (
        "fecha",
        "producto",
        "cantidad",
        "compra",
        "venta",
        "total",
        "ganancia"
    )

    tabla_historial = ttk.Treeview(
        marco_tabla,
        columns=columnas_historial,
        show="headings"
    )

    tabla_historial.heading("fecha", text="Fecha")
    tabla_historial.heading("producto", text="Producto")
    tabla_historial.heading("cantidad", text="Cantidad")
    tabla_historial.heading("compra", text="Precio compra")
    tabla_historial.heading("venta", text="Precio venta")
    tabla_historial.heading("total", text="Total vendido")
    tabla_historial.heading("ganancia", text="Ganancia")

    tabla_historial.column(
        "fecha",
        width=150,
        anchor="center"
    )

    tabla_historial.column(
        "producto",
        width=220
    )

    tabla_historial.column(
        "cantidad",
        width=80,
        anchor="center"
    )

    tabla_historial.column(
        "compra",
        width=120,
        anchor="center"
    )

    tabla_historial.column(
        "venta",
        width=120,
        anchor="center"
    )

    tabla_historial.column(
        "total",
        width=120,
        anchor="center"
    )

    tabla_historial.column(
        "ganancia",
        width=120,
        anchor="center"
    )

    # =============================================
    # SCROLLBAR
    # =============================================

    scrollbar = ttk.Scrollbar(
        marco_tabla,
        orient="vertical",
        command=tabla_historial.yview
    )

    tabla_historial.configure(
        yscrollcommand=scrollbar.set
    )

    tabla_historial.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    # =============================================
    # RESUMEN
    # =============================================

    marco_resumen = tk.Frame(
        ventana_historial,
        bg=COLOR_ROJO,
        height=55
    )

    marco_resumen.pack(
        fill="x",
        padx=15,
        pady=(10, 15)
    )

    marco_resumen.pack_propagate(False)

    etiqueta_resumen_ventas = tk.Label(
        marco_resumen,
        text="",
        bg=COLOR_ROJO,
        fg="white",
        font=("Arial", 10, "bold")
    )

    etiqueta_resumen_ventas.pack(
        side="left",
        padx=15,
        pady=15
    )

    # =============================================
    # FUNCIÓN PARA CARGAR LAS VENTAS
    # =============================================

    def cargar_historial():

        # Limpiar tabla antes de cargar nuevos datos
        for item in tabla_historial.get_children():
            tabla_historial.delete(item)

        periodo = filtro_periodo.get()

        # =========================================
        # CONSULTA SEGÚN EL PERÍODO
        # =========================================

        if periodo == "Hoy":

            consulta = """
                SELECT
                    fecha,
                    producto_nombre,
                    cantidad,
                    precio_compra,
                    precio_venta,
                    total,
                    ganancia
                FROM ventas
                WHERE DATE(fecha) = DATE('now', 'localtime')
                ORDER BY id DESC
            """

            cursor.execute(consulta)

        elif periodo == "Esta semana":

            consulta = """
                SELECT
                    fecha,
                    producto_nombre,
                    cantidad,
                    precio_compra,
                    precio_venta,
                    total,
                    ganancia
                FROM ventas
                WHERE DATE(fecha) >= DATE(
                    'now',
                    'localtime',
                    'weekday 0',
                    '-6 days'
                )
                AND DATE(fecha) <= DATE(
                    'now',
                    'localtime'
                )
                ORDER BY id DESC
            """

            cursor.execute(consulta)

        elif periodo == "Este mes":

            consulta = """
                SELECT
                    fecha,
                    producto_nombre,
                    cantidad,
                    precio_compra,
                    precio_venta,
                    total,
                    ganancia
                FROM ventas
                WHERE strftime(
                    '%Y-%m',
                    fecha,
                    'localtime'
                ) = strftime(
                    '%Y-%m',
                    'now',
                    'localtime'
                )
                ORDER BY id DESC
            """

            cursor.execute(consulta)

        else:

            consulta = """
                SELECT
                    fecha,
                    producto_nombre,
                    cantidad,
                    precio_compra,
                    precio_venta,
                    total,
                    ganancia
                FROM ventas
                ORDER BY id DESC
            """

            cursor.execute(consulta)

        ventas = cursor.fetchall()

        # =========================================
        # MOSTRAR VENTAS
        # =========================================

        for venta in ventas:

            fecha = venta[0]
            producto = venta[1]
            cantidad = venta[2]
            precio_compra = venta[3]
            precio_venta = venta[4]
            total = venta[5]
            ganancia = venta[6]

            tabla_historial.insert(
                "",
                tk.END,
                values=(
                    fecha,
                    producto,
                    cantidad,
                    f"Bs {precio_compra:.2f}",
                    f"Bs {precio_venta:.2f}",
                    f"Bs {total:.2f}",
                    f"Bs {ganancia:.2f}"
                )
            )

        # =========================================
        # CALCULAR RESUMEN
        # =========================================

        numero_ventas = len(ventas)

        unidades_vendidas = sum(
            venta[2]
            for venta in ventas
        )

        total_vendido = sum(
            venta[5]
            for venta in ventas
        )

        ganancia_total = sum(
            venta[6]
            for venta in ventas
        )

        etiqueta_resumen_ventas.config(
            text=(
                f"Ventas: {numero_ventas}    "
                f"Unidades vendidas: {unidades_vendidas}    "
                f"Total vendido: Bs {total_vendido:.2f}    "
                f"Ganancia: Bs {ganancia_total:.2f}"
            )
        )

    # =============================================
    # ACTUALIZAR AL CAMBIAR EL FILTRO
    # =============================================

    selector_periodo.bind(
        "<<ComboboxSelected>>",
        lambda event: cargar_historial()
    )

    # =============================================
    # BOTÓN CERRAR
    # =============================================

    tk.Button(
        marco_resumen,
        text="Cerrar",
        bg=COLOR_CREMA,
        fg=COLOR_ROJO,
        font=("Arial", 10, "bold"),
        command=ventana_historial.destroy
    ).pack(
        side="right",
        padx=10,
        pady=8
    )

    # =============================================
    # CARGAR HISTORIAL INICIAL
    # =============================================

    cargar_historial()



def actualizar_inventario():
    cursor.execute("""
        SELECT
            COUNT(*),
            COALESCE(SUM(cantidad), 0),
            COALESCE(SUM(precio_compra * cantidad), 0),
            COALESCE(SUM(precio_venta * cantidad), 0)
        FROM productos
    """)

    productos, unidades, valor_compra, valor_venta = cursor.fetchone()

    etiqueta_resumen.config(
        text=(
            f"Productos: {productos}    "
            f"Unidades: {unidades}    "
            f"Valor compra: Bs {valor_compra:.2f}    "
            f"Valor venta: Bs {valor_venta:.2f}"
        )
    )


def cerrar_aplicacion():
    conexion.close()
    ventana.destroy()


# =============================================
# ENCABEZADO
# =============================================

encabezado = tk.Frame(
    ventana,
    bg=COLOR_ROJO,
    height=110
)

encabezado.pack(fill="x")
encabezado.pack_propagate(False)

# ==============================================
# LOGO
# ==============================================

imagen_original = tk.PhotoImage(
    file=ruta_recurso("market_al_paso.png")
)

imagen_logo = imagen_original.subsample(6, 6)

logo = tk.Label(
    encabezado,
    image = imagen_logo,
    bg = COLOR_ROJO
)

logo.pack(
    side = "left",
    padx = 15,
    pady = 5
)


tk.Label(
    encabezado,
    text="MARKET al PASO",
    bg=COLOR_ROJO,
    fg="white",
    font=("Arial", 26, "bold")
).pack(pady=(15, 0))


tk.Label(
    encabezado,
    text="Gestión de inventario y ventas",
    bg=COLOR_ROJO,
    fg=COLOR_CREMA,
    font=("Arial", 11)
).pack()


# =============================================
# PANEL PRINCIPAL
# =============================================

panel = tk.Frame(
    ventana,
    bg=COLOR_FONDO
)

panel.pack(fill="both", expand=True, padx=20, pady=20)


# =============================================
# FORMULARIO
# =============================================

formulario = tk.LabelFrame(
    panel,
    text=" Gestión de productos ",
    bg=COLOR_FONDO,
    fg=COLOR_ROJO,
    font=("Arial", 11, "bold")
)

formulario.pack(fill="x", pady=(0, 15))


tk.Label(
    formulario,
    text="Nombre:",
    bg=COLOR_FONDO
).grid(row=0, column=0, padx=10, pady=10)

entrada_nombre = tk.Entry(formulario, width=20)
entrada_nombre.grid(row=0, column=1, padx=5)


tk.Label(
    formulario,
    text="Categoría:",
    bg=COLOR_FONDO
).grid(row=0, column=2, padx=10)

entrada_categoria = tk.Entry(formulario, width=20)
entrada_categoria.grid(row=0, column=3, padx=5)


tk.Label(
    formulario,
    text="Compra:",
    bg=COLOR_FONDO
).grid(row=1, column=0, padx=10, pady=10)

entrada_compra = tk.Entry(formulario, width=20)
entrada_compra.grid(row=1, column=1, padx=5)


tk.Label(
    formulario,
    text="Venta:",
    bg=COLOR_FONDO
).grid(row=1, column=2, padx=10)

entrada_venta = tk.Entry(formulario, width=20)
entrada_venta.grid(row=1, column=3, padx=5)


tk.Label(
    formulario,
    text="Cantidad:",
    bg=COLOR_FONDO
).grid(row=2, column=0, padx=10, pady=10)

entrada_cantidad = tk.Entry(formulario, width=20)
entrada_cantidad.grid(row=2, column=1, padx=5)


# =============================================
# BOTONES
# =============================================

tk.Button(
    formulario,
    text="Registrar",
    bg=COLOR_VERDE,
    fg="white",
    font=("Arial", 10, "bold"),
    command=registrar_producto
).grid(row=2, column=2, padx=5)


tk.Button(
    formulario,
    text="Modificar",
    bg=COLOR_AMARILLO,
    fg="#333333",
    font=("Arial", 10, "bold"),
    command=modificar_producto
).grid(row=2, column=3, padx=5)


tk.Button(
    formulario,
    text="Eliminar",
    bg=COLOR_ROJO,
    fg="white",
    font=("Arial", 10, "bold"),
    command=eliminar_producto
).grid(row=2, column=4, padx=5)


tk.Button(
    formulario,
    text="Limpiar",
    bg=COLOR_CREMA,
    fg=COLOR_ROJO,
    font=("Arial", 10, "bold"),
    command=limpiar_formulario
).grid(row=2, column=5, padx=5)


# =============================================
# BÚSQUEDA
# =============================================

barra_busqueda = tk.Frame(
    panel,
    bg=COLOR_FONDO
)

barra_busqueda.pack(fill="x", pady=(0, 10))


tk.Label(
    barra_busqueda,
    text="Buscar:",
    bg=COLOR_FONDO,
    fg=COLOR_ROJO,
    font=("Arial", 10, "bold")
).pack(side="left")


entrada_busqueda = tk.Entry(
    barra_busqueda,
    width=30
)

entrada_busqueda.pack(side="left", padx=10)


tk.Button(
    barra_busqueda,
    text="Buscar",
    bg=COLOR_VERDE,
    fg="white",
    command=buscar_producto
).pack(side="left")


tk.Button(
    barra_busqueda,
    text="Mostrar todos",
    bg=COLOR_CREMA,
    fg=COLOR_ROJO,
    command=cargar_productos
).pack(side="left", padx=5)


# =============================================
# TABLA
# =============================================

columnas = (
    "id",
    "nombre",
    "categoria",
    "compra",
    "venta",
    "cantidad"
)

tabla = ttk.Treeview(
    panel,
    columns = columnas,
    show = "headings"
)

tabla.heading("id", text = "id")
tabla.heading("nombre", text = "Producto")
tabla.heading("categoria", text = "Categoria")
tabla.heading("compra", text = "Precio compra")
tabla.heading("venta", text = "Precio venta")
tabla.heading("cantidad", text = "Stock")

tabla.column("id", width=50, anchor="center")
tabla.column("nombre", width=200)
tabla.column("categoria", width=150)
tabla.column("compra", width=120, anchor="center")
tabla.column("venta", width=120, anchor="center")
tabla.column("cantidad", width=100, anchor="center")

tabla.bind(
    "<Double-1>",
    seleccionar_producto
)

#=============================================
# BARRA INFERIOR
#=============================================

barra_inferior = tk.Frame(
    panel,
    bg=COLOR_ROJO,
    height=50
)

barra_inferior.pack(
    side="bottom",
    fill="x",
    pady=(15,0)
)

barra_inferior.pack_propagate(False)


etiqueta_resumen = tk.Label(
    barra_inferior,
    text="",
    bg=COLOR_ROJO,
    fg="white",
    font=("Arial", 10, "bold")
)

etiqueta_resumen.pack(
    side="left",
    padx=15,
    pady=10
)

tk.Button(
    barra_inferior,
    text="Historial de ventas",
    bg=COLOR_VERDE,
    fg="white",
    font=("Arial", 10, "bold"),
    command=ver_historial_ventas
).pack(
    side="right",
    padx=5,
    pady=5
)

tk.Button(
    barra_inferior,
    text="Registrar venta",
    bg=COLOR_AMARILLO,
    fg="#333333",
    font=("Arial", 10, "bold"),
    command=registrar_venta
).pack(
    side="right",
    padx=10,
    pady=5
)

tk.Button(
    barra_inferior,
    text="Salir",
    bg=COLOR_CREMA,
    fg=COLOR_ROJO,
    font=("Arial", 10, "bold"),
    command=cerrar_aplicacion
).pack(
    side="right",
    padx=5,
    pady=5
)

#==============================================
# TABLA
#==============================================

tabla.pack(
    fill="both",
    expand=True
)


# =============================================
# CARGAR DATOS INICIALES
# =============================================

cargar_productos()


# =============================================
# INICIAR APLICACIÓN
# =============================================

ventana.mainloop()