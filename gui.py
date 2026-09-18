import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

from database import conexion, cursor


# =============================================
# RUTA DE RECURSOS
# =============================================

def ruta_recurso(nombre_archivo):

    if getattr(sys, "frozen", False):
        carpeta_base = sys._MEIPASS
    else:
        carpeta_base = os.path.dirname(
            os.path.abspath(__file__)
        )

    return os.path.join(
        carpeta_base,
        nombre_archivo
    )


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
    entrada_codigo_barras.delete(0, tk.END)
    entrada_compra.delete(0, tk.END)
    entrada_venta.delete(0, tk.END)
    entrada_cantidad.delete(0, tk.END)


# =============================================
# INSERTAR PRODUCTO EN TABLA
# =============================================

def insertar_producto_en_tabla(producto):

    cantidad = int(producto[5])

    # =========================================
    # STOCK BAJO
    # =========================================

    if cantidad < 5:

        tabla.insert(
            "",
            tk.END,
            values=producto,
            tags=("stock_bajo",)
        )

    else:

        tabla.insert(
            "",
            tk.END,
            values=producto
        )


def cargar_productos():

    for item in tabla.get_children():
        tabla.delete(item)

    cursor.execute("""
        SELECT
            id,
            nombre,
            categoria,
            precio_compra,
            precio_venta,
            cantidad,
            codigo_barras
        FROM productos
        ORDER BY id
    """)

    productos = cursor.fetchall()

    for producto in productos:

        insertar_producto_en_tabla(producto)

    actualizar_inventario()


def registrar_producto():

    nombre = entrada_nombre.get().strip()
    categoria = entrada_categoria.get().strip()
    codigo_barras = entrada_codigo_barras.get().strip()
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

    # =========================================
    # COMPROBAR NOMBRE
    # =========================================

    cursor.execute(
        """
        SELECT id
        FROM productos
        WHERE LOWER(nombre) = LOWER(?)
        """,
        (nombre,)
    )

    if cursor.fetchone():

        messagebox.showwarning(
            "Producto existente",
            "Ya existe un producto con ese nombre."
        )

        return

    # =========================================
    # COMPROBAR CÓDIGO DE BARRAS
    # =========================================

    if codigo_barras:

        cursor.execute(
            """
            SELECT id
            FROM productos
            WHERE codigo_barras = ?
            """,
            (codigo_barras,)
        )

        if cursor.fetchone():

            messagebox.showwarning(
                "Código de barras existente",
                "Ya existe un producto con ese código de barras."
            )

            return

    # =========================================
    # INSERTAR PRODUCTO
    # =========================================

    cursor.execute(
        """
        INSERT INTO productos
        (
            nombre,
            categoria,
            precio_compra,
            precio_venta,
            cantidad,
            codigo_barras
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            nombre,
            categoria,
            compra,
            venta,
            cantidad,
            codigo_barras
        )
    )

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

    valores = tabla.item(
        seleccionado[0],
        "values"
    )

    limpiar_formulario()

    entrada_nombre.insert(
        0,
        valores[1]
    )

    entrada_categoria.insert(
        0,
        valores[2]
    )

    entrada_compra.insert(
        0,
        valores[3]
    )

    entrada_venta.insert(
        0,
        valores[4]
    )

    entrada_cantidad.insert(
        0,
        valores[5]
    )

    if valores[6]:

        entrada_codigo_barras.insert(
            0,
            valores[6]
        )


def modificar_producto():

    seleccionado = tabla.selection()

    if not seleccionado:

        messagebox.showwarning(
            "Selecciona un producto",
            "Selecciona un producto de la tabla."
        )

        return

    valores = tabla.item(
        seleccionado[0],
        "values"
    )

    producto_id = valores[0]

    nombre = entrada_nombre.get().strip()
    categoria = entrada_categoria.get().strip()
    codigo_barras = entrada_codigo_barras.get().strip()
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

    # =========================================
    # COMPROBAR NOMBRE DUPLICADO
    # =========================================

    cursor.execute(
        """
        SELECT id
        FROM productos
        WHERE LOWER(nombre) = LOWER(?)
        AND id != ?
        """,
        (
            nombre,
            producto_id
        )
    )

    if cursor.fetchone():

        messagebox.showwarning(
            "Producto existente",
            "Ya existe otro producto con ese nombre."
        )

        return

    # =========================================
    # COMPROBAR CÓDIGO DUPLICADO
    # =========================================

    if codigo_barras:

        cursor.execute(
            """
            SELECT id
            FROM productos
            WHERE codigo_barras = ?
            AND id != ?
            """,
            (
                codigo_barras,
                producto_id
            )
        )

        if cursor.fetchone():

            messagebox.showwarning(
                "Código de barras existente",
                "Ese código de barras ya pertenece a otro producto."
            )

            return

    # =========================================
    # ACTUALIZAR PRODUCTO
    # =========================================

    cursor.execute(
        """
        UPDATE productos
        SET
            nombre = ?,
            categoria = ?,
            codigo_barras = ?,
            precio_compra = ?,
            precio_venta = ?,
            cantidad = ?
        WHERE id = ?
        """,
        (
            nombre,
            categoria,
            codigo_barras,
            compra,
            venta,
            cantidad,
            producto_id
        )
    )

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

    valores = tabla.item(
        seleccionado[0],
        "values"
    )

    producto_id = valores[0]
    nombre = valores[1]

    confirmar = messagebox.askyesno(
        "Confirmar eliminación",
        f"¿Deseas eliminar '{nombre}'?"
    )

    if not confirmar:
        return

    cursor.execute(
        """
        DELETE FROM productos
        WHERE id = ?
        """,
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

    cursor.execute(
        """
        SELECT
            id,
            nombre,
            categoria,
            precio_compra,
            precio_venta,
            cantidad,
            codigo_barras
        FROM productos
        WHERE LOWER(nombre) LIKE LOWER(?)
           OR LOWER(categoria) LIKE LOWER(?)
           OR codigo_barras LIKE ?
        ORDER BY id
        """,
        (
            f"%{texto}%",
            f"%{texto}%",
            f"%{texto}%"
        )
    )

    productos = cursor.fetchall()

    for producto in productos:

        insertar_producto_en_tabla(producto)


# =============================================
# NUEVA VENTA
# =============================================

def nueva_venta():

    ventana_nueva_venta = tk.Toplevel(ventana)

    ventana_nueva_venta.title("Nueva venta")
    ventana_nueva_venta.geometry("900x600")
    ventana_nueva_venta.configure(bg=COLOR_FONDO)
    ventana_nueva_venta.minsize(800, 500)

    # =============================================
    # TÍTULO
    # =============================================

    tk.Label(
        ventana_nueva_venta,
        text="Nueva venta",
        bg=COLOR_FONDO,
        fg=COLOR_ROJO,
        font=("Arial", 20, "bold")
    ).pack(
        pady=(15, 5)
    )

    tk.Label(
        ventana_nueva_venta,
        text="Escanea los productos para agregarlos a la venta",
        bg=COLOR_FONDO,
        fg="#333333",
        font=("Arial", 10)
    ).pack(
        pady=(0, 15)
    )

    # =============================================
    # CAMPO DE ESCÁNER
    # =============================================

    marco_scanner = tk.Frame(
        ventana_nueva_venta,
        bg=COLOR_FONDO
    )

    marco_scanner.pack(
        fill="x",
        padx=20,
        pady=(0, 15)
    )

    tk.Label(
        marco_scanner,
        text="Escanear código:",
        bg=COLOR_FONDO,
        fg=COLOR_ROJO,
        font=("Arial", 11, "bold")
    ).pack(
        side="left",
        padx=(0, 10)
    )

    entrada_scanner = tk.Entry(
        marco_scanner,
        width=30,
        font=("Arial", 14)
    )

    entrada_scanner.pack(
        side="left"
    )

    # =============================================
    # TABLA DE LA VENTA
    # =============================================

    marco_tabla_venta = tk.Frame(
        ventana_nueva_venta,
        bg=COLOR_FONDO
    )

    marco_tabla_venta.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=5
    )

    columnas_venta = (
        "producto",
        "cantidad",
        "precio",
        "total"
    )

    tabla_venta = ttk.Treeview(
        marco_tabla_venta,
        columns=columnas_venta,
        show="headings"
    )

    tabla_venta.heading(
        "producto",
        text="Producto"
    )

    tabla_venta.heading(
        "cantidad",
        text="Cantidad"
    )

    tabla_venta.heading(
        "precio",
        text="Precio"
    )

    tabla_venta.heading(
        "total",
        text="Total"
    )

    tabla_venta.column(
        "producto",
        width=350
    )

    tabla_venta.column(
        "cantidad",
        width=120,
        anchor="center"
    )

    tabla_venta.column(
        "precio",
        width=150,
        anchor="center"
    )

    tabla_venta.column(
        "total",
        width=150,
        anchor="center"
    )

    tabla_venta.pack(
        fill="both",
        expand=True
    )

    # =============================================
    # TOTAL
    # =============================================

    etiqueta_total_venta = tk.Label(
        ventana_nueva_venta,
        text="TOTAL: Bs 0.00",
        bg=COLOR_ROJO,
        fg="white",
        font=("Arial", 14, "bold")
    )

    etiqueta_total_venta.pack(
        fill="x",
        padx=20,
        pady=15
    )

    # =============================================
    # VARIABLES
    # =============================================

    total_venta = 0.0

    # Guarda información del último escaneo
    ultimo_escaneo = None

    # =============================================
    # PROCESAR ESCANEO
    # =============================================

    def procesar_codigo(event=None):

        nonlocal total_venta
        nonlocal ultimo_escaneo

        codigo = entrada_scanner.get().strip()

        if not codigo:
            return

        cursor.execute(
            """
            SELECT
                id,
                nombre,
                precio_compra,
                precio_venta,
                cantidad
            FROM productos
            WHERE codigo_barras = ?
            """,
            (codigo,)
        )

        producto = cursor.fetchone()

        if not producto:

            messagebox.showwarning(
                "Producto no encontrado",
                f"No existe un producto registrado con el código:\n\n{codigo}"
            )

            entrada_scanner.delete(
                0,
                tk.END
            )

            entrada_scanner.focus_set()

            return

        producto_id = producto[0]
        nombre = producto[1]
        precio_compra = float(producto[2])
        precio_venta = float(producto[3])
        stock = int(producto[4])

        # =========================================
        # COMPROBAR STOCK
        # =========================================

        if stock <= 0:

            messagebox.showwarning(
                "Sin stock",
                f"El producto '{nombre}' no tiene stock disponible."
            )

            entrada_scanner.delete(
                0,
                tk.END
            )

            entrada_scanner.focus_set()

            return

        # =========================================
        # BUSCAR SI YA ESTÁ EN LA VENTA
        # =========================================

        encontrado = False

        for item in tabla_venta.get_children():

            valores = tabla_venta.item(
                item,
                "values"
            )

            if valores[0] == nombre:

                cantidad_actual = int(
                    valores[1]
                )

                if cantidad_actual >= stock:

                    messagebox.showwarning(
                        "Stock insuficiente",
                        f"No hay más unidades disponibles de '{nombre}'."
                    )

                    entrada_scanner.delete(
                        0,
                        tk.END
                    )

                    entrada_scanner.focus_set()

                    return

                nueva_cantidad = cantidad_actual + 1

                nuevo_total = (
                    nueva_cantidad *
                    precio_venta
                )

                tabla_venta.item(
                    item,
                    values=(
                        nombre,
                        nueva_cantidad,
                        f"Bs {precio_venta:.2f}",
                        f"Bs {nuevo_total:.2f}"
                    )
                )

                # =====================================
                # GUARDAR ÚLTIMO ESCANEO
                # =====================================

                ultimo_escaneo = {
                    "item_id": item,
                    "producto_id": producto_id,
                    "nombre": nombre,
                    "precio": precio_venta,
                    "era_nuevo": False,
                    "cantidad_anterior": cantidad_actual,
                    "total_anterior": cantidad_actual * precio_venta
                }

                total_venta += precio_venta

                encontrado = True

                break

        # =========================================
        # AGREGAR NUEVO PRODUCTO
        # =========================================

        if not encontrado:

            total_producto = precio_venta

            item_id = tabla_venta.insert(
                "",
                tk.END,
                values=(
                    nombre,
                    1,
                    f"Bs {precio_venta:.2f}",
                    f"Bs {total_producto:.2f}"
                )
            )

            # =====================================
            # GUARDAR ÚLTIMO ESCANEO
            # =====================================

            ultimo_escaneo = {
                "item_id": item_id,
                "producto_id": producto_id,
                "nombre": nombre,
                "precio": precio_venta,
                "era_nuevo": True,
                "cantidad_anterior": 0,
                "total_anterior": 0.0
            }

            total_venta += precio_venta

        # =========================================
        # ACTUALIZAR TOTAL
        # =========================================

        etiqueta_total_venta.config(
            text=f"TOTAL: Bs {total_venta:.2f}"
        )

        # =========================================
        # PREPARAR SIGUIENTE ESCANEO
        # =========================================

        entrada_scanner.delete(
            0,
            tk.END
        )

        entrada_scanner.focus_set()

    # =============================================
    # DESHACER ÚLTIMO ESCANEO
    # =============================================

    def deshacer_ultimo_escaneo():

        nonlocal total_venta
        nonlocal ultimo_escaneo

        if ultimo_escaneo is None:

            messagebox.showinfo(
                "Sin operación",
                "No hay ningún escaneo reciente para deshacer."
            )

            entrada_scanner.focus_set()

            return

        item_id = ultimo_escaneo["item_id"]
        precio = ultimo_escaneo["precio"]
        era_nuevo = ultimo_escaneo["era_nuevo"]
        cantidad_anterior = ultimo_escaneo["cantidad_anterior"]
        total_anterior = ultimo_escaneo["total_anterior"]
        nombre = ultimo_escaneo["nombre"]

        # =========================================
        # SI ERA UN PRODUCTO NUEVO
        # =========================================

        if era_nuevo:

            if tabla_venta.exists(item_id):

                tabla_venta.delete(
                    item_id
                )

            total_venta -= precio

        # =========================================
        # SI YA EXISTÍA EN LA VENTA
        # =========================================

        else:

            if tabla_venta.exists(item_id):

                tabla_venta.item(
                    item_id,
                    values=(
                        nombre,
                        cantidad_anterior,
                        f"Bs {precio:.2f}",
                        f"Bs {total_anterior:.2f}"
                    )
                )

                total_venta -= precio

        # =========================================
        # EVITAR VALORES NEGATIVOS POR REDONDEO
        # =========================================

        if total_venta < 0:
            total_venta = 0.0

        # =========================================
        # ACTUALIZAR TOTAL
        # =========================================

        etiqueta_total_venta.config(
            text=f"TOTAL: Bs {total_venta:.2f}"
        )

        # =========================================
        # ELIMINAR HISTORIAL DEL ÚLTIMO ESCANEO
        # =========================================

        ultimo_escaneo = None

        entrada_scanner.delete(
            0,
            tk.END
        )

        entrada_scanner.focus_set()

    # =============================================
    # LIMPIAR VENTA
    # =============================================

    def limpiar_venta():

        nonlocal total_venta
        nonlocal ultimo_escaneo

        for item in tabla_venta.get_children():

            tabla_venta.delete(
                item
            )

        total_venta = 0.0

        ultimo_escaneo = None

        etiqueta_total_venta.config(
            text="TOTAL: Bs 0.00"
        )

        entrada_scanner.delete(
            0,
            tk.END
        )

        entrada_scanner.focus_set()

    # =============================================
    # CONFIRMAR VENTA
    # =============================================

    def confirmar_venta():

        nonlocal total_venta

        if not tabla_venta.get_children():

            messagebox.showwarning(
                "Venta vacía",
                "No hay productos agregados a la venta."
            )

            entrada_scanner.focus_set()

            return

        # =========================================
        # CONFIRMAR CON EL USUARIO
        # =========================================

        confirmar = messagebox.askyesno(
            "Confirmar venta",
            f"¿Deseas confirmar esta venta?\n\n"
            f"Total: Bs {total_venta:.2f}"
        )

        if not confirmar:

            entrada_scanner.focus_set()

            return

        # =========================================
        # VALIDAR STOCK
        # =========================================

        productos_venta = []

        for item in tabla_venta.get_children():

            valores = tabla_venta.item(
                item,
                "values"
            )

            nombre = valores[0]
            cantidad = int(
                valores[1]
            )

            cursor.execute(
                """
                SELECT
                    id,
                    nombre,
                    precio_compra,
                    precio_venta,
                    cantidad
                FROM productos
                WHERE nombre = ?
                """,
                (nombre,)
            )

            producto = cursor.fetchone()

            if not producto:

                messagebox.showerror(
                    "Error",
                    f"No se encontró el producto '{nombre}' en la base de datos."
                )

                return

            producto_id = producto[0]
            precio_compra = float(producto[2])
            precio_venta = float(producto[3])
            stock_actual = int(producto[4])

            if cantidad > stock_actual:

                messagebox.showwarning(
                    "Stock insuficiente",
                    f"El producto '{nombre}' no tiene suficiente stock.\n\n"
                    f"Stock disponible: {stock_actual}\n"
                    f"Cantidad solicitada: {cantidad}"
                )

                return

            productos_venta.append(
                (
                    producto_id,
                    nombre,
                    cantidad,
                    precio_compra,
                    precio_venta
                )
            )

        # =========================================
        # REGISTRAR TODA LA VENTA
        # =========================================

        try:

            for producto in productos_venta:

                producto_id = producto[0]
                nombre = producto[1]
                cantidad = producto[2]
                precio_compra = producto[3]
                precio_venta = producto[4]

                total_producto = (
                    cantidad *
                    precio_venta
                )

                ganancia = cantidad * (
                    precio_venta -
                    precio_compra
                )

                # Registrar venta
                cursor.execute(
                    """
                    INSERT INTO ventas(
                        producto_id,
                        producto_nombre,
                        cantidad,
                        precio_compra,
                        precio_venta,
                        total,
                        ganancia
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        producto_id,
                        nombre,
                        cantidad,
                        precio_compra,
                        precio_venta,
                        total_producto,
                        ganancia
                    )
                )

                # Descontar stock
                cursor.execute(
                    """
                    UPDATE productos
                    SET cantidad = cantidad - ?
                    WHERE id = ?
                    """,
                    (
                        cantidad,
                        producto_id
                    )
                )

            conexion.commit()

        except Exception as error:

            conexion.rollback()

            messagebox.showerror(
                "Error al registrar venta",
                f"No se pudo registrar la venta.\n\n{error}"
            )

            return

        # =========================================
        # VENTA REGISTRADA
        # =========================================

        messagebox.showinfo(
            "Venta registrada",
            f"La venta se registró correctamente.\n\n"
            f"Total: Bs {total_venta:.2f}"
        )

        # =========================================
        # ACTUALIZAR PRODUCTOS
        # =========================================

        cargar_productos()

        # =========================================
        # LIMPIAR VENTA
        # =========================================

        limpiar_venta()

        entrada_scanner.focus_set()

    # =============================================
    # ACTIVAR ESCANEO CON ENTER
    # =============================================

    entrada_scanner.bind(
        "<Return>",
        procesar_codigo
    )

    # =============================================
    # BOTONES
    # =============================================

    marco_botones = tk.Frame(
        ventana_nueva_venta,
        bg=COLOR_FONDO
    )

    marco_botones.pack(
        fill="x",
        padx=20,
        pady=(0, 15)
    )

    # =========================================
    # CONFIRMAR
    # =========================================

    tk.Button(
        marco_botones,
        text="Confirmar venta",
        bg=COLOR_VERDE,
        fg="white",
        font=("Arial", 10, "bold"),
        command=confirmar_venta
    ).pack(
        side="left",
        padx=(0, 5)
    )

    # =========================================
    # DESHACER ÚLTIMO ESCANEO
    # =========================================

    tk.Button(
        marco_botones,
        text="↶ Deshacer último escaneo",
        bg=COLOR_AMARILLO,
        fg="#333333",
        font=("Arial", 10, "bold"),
        command=deshacer_ultimo_escaneo
    ).pack(
        side="left",
        padx=5
    )

    # =========================================
    # LIMPIAR
    # =========================================

    tk.Button(
        marco_botones,
        text="Limpiar venta",
        bg=COLOR_CREMA,
        fg=COLOR_ROJO,
        font=("Arial", 10, "bold"),
        command=limpiar_venta
    ).pack(
        side="left",
        padx=5
    )

    # =========================================
    # CERRAR
    # =========================================

    tk.Button(
        marco_botones,
        text="Cerrar",
        bg=COLOR_ROJO,
        fg="white",
        font=("Arial", 10, "bold"),
        command=ventana_nueva_venta.destroy
    ).pack(
        side="right"
    )

    # =============================================
    # ENFOCAR ESCÁNER
    # =============================================

    entrada_scanner.focus_set()


# =============================================
# REGISTRAR VENTA MANUAL
# =============================================

def registrar_venta():

    seleccionado = tabla.selection()

    if not seleccionado:

        messagebox.showwarning(
            "Selecciona un producto",
            "Selecciona el producto que deseas vender."
        )

        return

    valores = tabla.item(
        seleccionado[0],
        "values"
    )

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
    ).pack(
        pady=15
    )

    tk.Label(
        ventana_venta,
        text=f"Stock disponible: {stock}",
        bg=COLOR_FONDO
    ).pack()

    tk.Label(
        ventana_venta,
        text=f"Precio de venta: Bs {precio_venta:.2f}",
        bg=COLOR_FONDO
    ).pack(
        pady=(5, 0)
    )

    tk.Label(
        ventana_venta,
        text="Cantidad a vender:",
        bg=COLOR_FONDO
    ).pack(
        pady=(15, 5)
    )

    entrada_venta_cantidad = tk.Entry(
        ventana_venta,
        width=15
    )

    entrada_venta_cantidad.pack()

    def confirmar_venta_manual():

        try:

            cantidad = int(
                entrada_venta_cantidad.get()
            )

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

        # =========================================
        # CÁLCULOS
        # =========================================

        nuevo_stock = stock - cantidad

        total = cantidad * precio_venta

        ganancia = (
            precio_venta -
            precio_compra
        ) * cantidad

        # =========================================
        # GUARDAR VENTA
        # =========================================

        try:

            cursor.execute(
                """
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
                """,
                (
                    producto_id,
                    nombre,
                    cantidad,
                    precio_compra,
                    precio_venta,
                    total,
                    ganancia
                )
            )

            # =====================================
            # ACTUALIZAR STOCK
            # =====================================

            cursor.execute(
                """
                UPDATE productos
                SET cantidad = ?
                WHERE id = ?
                """,
                (
                    nuevo_stock,
                    producto_id
                )
            )

            conexion.commit()

        except Exception as error:

            conexion.rollback()

            messagebox.showerror(
                "Error",
                f"No se pudo registrar la venta.\n\n{error}"
            )

            return

        # =========================================
        # ACTUALIZAR INTERFAZ
        # =========================================

        cargar_productos()

        ventana_venta.destroy()

        # =========================================
        # CONFIRMACIÓN
        # =========================================

        messagebox.showinfo(
            "Venta registrada",
            f"Venta registrada correctamente.\n\n"
            f"Producto: {nombre}\n"
            f"Cantidad: {cantidad}\n"
            f"Total: Bs {total:.2f}\n"
            f"Ganancia: Bs {ganancia:.2f}"
        )

    # =============================================
    # BOTÓN CONFIRMAR
    # =============================================

    tk.Button(
        ventana_venta,
        text="Confirmar venta",
        bg=COLOR_VERDE,
        fg="white",
        font=("Arial", 10, "bold"),
        command=confirmar_venta_manual
    ).pack(
        pady=15
    )


# =============================================
# HISTORIAL DE VENTAS
# =============================================

def ver_historial_ventas():

    ventana_historial = tk.Toplevel(ventana)

    ventana_historial.title(
        "Historial de ventas"
    )

    ventana_historial.geometry(
        "1000x600"
    )

    ventana_historial.configure(
        bg=COLOR_FONDO
    )

    ventana_historial.minsize(
        900,
        500
    )

    # =============================================
    # TÍTULO
    # =============================================

    tk.Label(
        ventana_historial,
        text="Historial de ventas",
        bg=COLOR_FONDO,
        fg=COLOR_ROJO,
        font=("Arial", 18, "bold")
    ).pack(
        pady=(15, 5)
    )

    tk.Label(
        ventana_historial,
        text="Consulta y resumen de ventas",
        bg=COLOR_FONDO,
        fg="#333333",
        font=("Arial", 10)
    ).pack(
        pady=(0, 10)
    )

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
    ).pack(
        side="left",
        padx=(0, 10)
    )

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

    selector_periodo.pack(
        side="left"
    )

    # =============================================
    # BÚSQUEDA
    # =============================================

    tk.Label(
        marco_filtros,
        text="Producto:",
        bg=COLOR_FONDO,
        fg=COLOR_ROJO,
        font=("Arial", 10, "bold")
    ).pack(
        side="left",
        padx=(25, 10)
    )

    entrada_busqueda_historial = tk.Entry(
        marco_filtros,
        width=25,
        font=("Arial", 10)
    )

    entrada_busqueda_historial.pack(
        side="left"
    )

    # =============================================
    # TABLA
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

    tabla_historial.heading(
        "fecha",
        text="Fecha"
    )

    tabla_historial.heading(
        "producto",
        text="Producto"
    )

    tabla_historial.heading(
        "cantidad",
        text="Cantidad"
    )

    tabla_historial.heading(
        "compra",
        text="Precio compra"
    )

    tabla_historial.heading(
        "venta",
        text="Precio venta"
    )

    tabla_historial.heading(
        "total",
        text="Total vendido"
    )

    tabla_historial.heading(
        "ganancia",
        text="Ganancia"
    )

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
    # CARGAR HISTORIAL
    # =============================================

    def cargar_historial():

        for item in tabla_historial.get_children():

            tabla_historial.delete(
                item
            )

        periodo = filtro_periodo.get()

        producto_buscado = (
            entrada_busqueda_historial
            .get()
            .strip()
        )

        consulta = """
            SELECT
                datetime(fecha, 'localtime'),
                producto_nombre,
                cantidad,
                precio_compra,
                precio_venta,
                total,
                ganancia
            FROM ventas
            WHERE 1 = 1
        """

        parametros = []

        # =========================================
        # FILTRO PERÍODO
        # =========================================

        if periodo == "Hoy":

            consulta += """
                AND DATE(fecha, 'localtime') =
                    DATE('now', 'localtime')
            """

        elif periodo == "Esta semana":

            consulta += """
                AND DATE(fecha, 'localtime') >=
                    DATE(
                        'now',
                        'localtime',
                        'weekday 0',
                        '-6 days'
                    )
                AND DATE(fecha, 'localtime') <=
                    DATE(
                        'now',
                        'localtime'
                    )
            """

        elif periodo == "Este mes":

            consulta += """
                AND strftime(
                    '%Y-%m',
                    fecha,
                    'localtime'
                ) = strftime(
                    '%Y-%m',
                    'now',
                    'localtime'
                )
            """

        # =========================================
        # FILTRO PRODUCTO
        # =========================================

        if producto_buscado:

            consulta += """
                AND producto_nombre LIKE ?
            """

            parametros.append(
                f"%{producto_buscado}%"
            )

        # =========================================
        # ORDENAR
        # =========================================

        consulta += """
            ORDER BY id DESC
        """

        cursor.execute(
            consulta,
            parametros
        )

        ventas = cursor.fetchall()

        # =========================================
        # MOSTRAR
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
        # RESUMEN
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
    # EVENTOS
    # =============================================

    selector_periodo.bind(
        "<<ComboboxSelected>>",
        lambda event: cargar_historial()
    )

    entrada_busqueda_historial.bind(
        "<Return>",
        lambda event: cargar_historial()
    )

    # =============================================
    # BOTÓN BUSCAR
    # =============================================

    tk.Button(
        marco_filtros,
        text="Buscar",
        bg=COLOR_VERDE,
        fg="white",
        font=("Arial", 10, "bold"),
        command=cargar_historial
    ).pack(
        side="left",
        padx=(10, 0)
    )

    # =============================================
    # BOTÓN LIMPIAR
    # =============================================

    def limpiar_filtros_historial():

        entrada_busqueda_historial.delete(
            0,
            tk.END
        )

        filtro_periodo.set(
            "Todas"
        )

        cargar_historial()

    tk.Button(
        marco_filtros,
        text="Limpiar",
        bg=COLOR_CREMA,
        fg=COLOR_ROJO,
        font=("Arial", 10, "bold"),
        command=limpiar_filtros_historial
    ).pack(
        side="left",
        padx=(5, 0)
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


# =============================================
# REPORTE DIARIO
# =============================================

def ver_reporte_diario():

    ventana_reporte = tk.Toplevel(ventana)

    ventana_reporte.title(
        "Reporte diario"
    )

    ventana_reporte.geometry(
        "900x600"
    )

    ventana_reporte.configure(
        bg=COLOR_FONDO
    )

    ventana_reporte.minsize(
        800,
        500
    )

    # =============================================
    # TÍTULO
    # =============================================

    tk.Label(
        ventana_reporte,
        text="Reporte diario",
        bg=COLOR_FONDO,
        fg=COLOR_ROJO,
        font=("Arial", 18, "bold")
    ).pack(
        pady=(15, 5)
    )

    tk.Label(
        ventana_reporte,
        text="Resumen de ventas del día",
        bg=COLOR_FONDO,
        fg="#333333",
        font=("Arial", 10)
    ).pack(
        pady=(0, 15)
    )

    # =============================================
    # DATOS DEL DÍA
    # =============================================

    cursor.execute(
        """
        SELECT
            COUNT(*),
            COALESCE(SUM(cantidad), 0),
            COALESCE(SUM(total), 0),
            COALESCE(SUM(precio_compra * cantidad), 0),
            COALESCE(SUM(ganancia), 0)
        FROM ventas
        WHERE DATE(fecha, 'localtime') =
            DATE('now', 'localtime')
        """
    )

    resultado = cursor.fetchone()

    numero_ventas = resultado[0]
    unidades_vendidas = resultado[1]
    total_vendido = resultado[2]
    costo_productos = resultado[3]
    ganancia_bruta = resultado[4]

    # =============================================
    # FECHA
    # =============================================

    cursor.execute(
        """
        SELECT DATE(
            'now',
            'localtime'
        )
        """
    )

    fecha_hoy = cursor.fetchone()[0]

    tk.Label(
        ventana_reporte,
        text=f"Fecha: {fecha_hoy}",
        bg=COLOR_FONDO,
        fg=COLOR_ROJO,
        font=("Arial", 12, "bold")
    ).pack(
        pady=(0, 15)
    )

    # =============================================
    # RESUMEN
    # =============================================

    marco_resumen = tk.Frame(
        ventana_reporte,
        bg=COLOR_ROJO
    )

    marco_resumen.pack(
        fill="x",
        padx=20,
        pady=(0, 15)
    )

    texto_resumen = (
        f"Ventas realizadas: {numero_ventas}    |    "
        f"Unidades vendidas: {unidades_vendidas}    |    "
        f"Total vendido: Bs {total_vendido:.2f}    |    "
        f"Costo: Bs {costo_productos:.2f}    |    "
        f"Ganancia bruta: Bs {ganancia_bruta:.2f}"
    )

    tk.Label(
        marco_resumen,
        text=texto_resumen,
        bg=COLOR_ROJO,
        fg="white",
        font=("Arial", 10, "bold"),
        wraplength=820,
        justify="center"
    ).pack(
        padx=15,
        pady=15
    )

    # =============================================
    # TÍTULO DETALLE
    # =============================================

    tk.Label(
        ventana_reporte,
        text="Productos vendidos hoy",
        bg=COLOR_FONDO,
        fg=COLOR_ROJO,
        font=("Arial", 13, "bold")
    ).pack(
        pady=(0, 8)
    )

    # =============================================
    # TABLA
    # =============================================

    marco_tabla = tk.Frame(
        ventana_reporte,
        bg=COLOR_FONDO
    )

    marco_tabla.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=5
    )

    columnas_reporte = (
        "producto",
        "unidades",
        "total",
        "ganancia"
    )

    tabla_reporte = ttk.Treeview(
        marco_tabla,
        columns=columnas_reporte,
        show="headings"
    )

    tabla_reporte.heading(
        "producto",
        text="Producto"
    )

    tabla_reporte.heading(
        "unidades",
        text="Unidades"
    )

    tabla_reporte.heading(
        "total",
        text="Total vendido"
    )

    tabla_reporte.heading(
        "ganancia",
        text="Ganancia bruta"
    )

    tabla_reporte.column(
        "producto",
        width=350
    )

    tabla_reporte.column(
        "unidades",
        width=120,
        anchor="center"
    )

    tabla_reporte.column(
        "total",
        width=160,
        anchor="center"
    )

    tabla_reporte.column(
        "ganancia",
        width=160,
        anchor="center"
    )

    # =============================================
    # SCROLLBAR
    # =============================================

    scrollbar = ttk.Scrollbar(
        marco_tabla,
        orient="vertical",
        command=tabla_reporte.yview
    )

    tabla_reporte.configure(
        yscrollcommand=scrollbar.set
    )

    tabla_reporte.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    # =============================================
    # PRODUCTOS VENDIDOS
    # =============================================

    cursor.execute(
        """
        SELECT
            producto_nombre,
            SUM(cantidad),
            SUM(total),
            SUM(ganancia)
        FROM ventas
        WHERE DATE(fecha, 'localtime') =
            DATE('now', 'localtime')
        GROUP BY producto_nombre
        ORDER BY SUM(cantidad) DESC
        """
    )

    productos_vendidos = cursor.fetchall()

    for producto in productos_vendidos:

        nombre = producto[0]
        unidades = producto[1]
        total = producto[2]
        ganancia = producto[3]

        tabla_reporte.insert(
            "",
            tk.END,
            values=(
                nombre,
                unidades,
                f"Bs {total:.2f}",
                f"Bs {ganancia:.2f}"
            )
        )

    # =============================================
    # BOTÓN CERRAR
    # =============================================

    tk.Button(
        ventana_reporte,
        text="Cerrar",
        bg=COLOR_CREMA,
        fg=COLOR_ROJO,
        font=("Arial", 10, "bold"),
        command=ventana_reporte.destroy
    ).pack(
        pady=12
    )


# =============================================
# REPORTE MENSUAL
# =============================================

def ver_reporte_mensual():

    ventana_reporte = tk.Toplevel(ventana)

    ventana_reporte.title(
        "Reporte mensual"
    )

    ventana_reporte.geometry(
        "950x700"
    )

    ventana_reporte.configure(
        bg=COLOR_FONDO
    )

    ventana_reporte.minsize(
        850,
        600
    )

    # =============================================
    # TÍTULO
    # =============================================

    tk.Label(
        ventana_reporte,
        text="Reporte mensual",
        bg=COLOR_FONDO,
        fg=COLOR_ROJO,
        font=("Arial", 18, "bold")
    ).pack(
        pady=(15, 5)
    )

    tk.Label(
        ventana_reporte,
        text="Resumen de ventas del mes actual",
        bg=COLOR_FONDO,
        fg="#333333",
        font=("Arial", 10)
    ).pack(
        pady=(0, 10)
    )

    # =============================================
    # MES ACTUAL
    # =============================================

    cursor.execute(
        """
        SELECT strftime(
            '%Y-%m',
            'now',
            'localtime'
        )
        """
    )

    mes_actual = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT strftime(
            '%m',
            'now',
            'localtime'
        )
        """
    )

    numero_mes = cursor.fetchone()[0]

    nombres_meses = {
        "01": "enero",
        "02": "febrero",
        "03": "marzo",
        "04": "abril",
        "05": "mayo",
        "06": "junio",
        "07": "julio",
        "08": "agosto",
        "09": "septiembre",
        "10": "octubre",
        "11": "noviembre",
        "12": "diciembre"
    }

    nombre_mes = nombres_meses.get(
        numero_mes,
        numero_mes
    )

    tk.Label(
        ventana_reporte,
        text=(
            f"Mes: "
            f"{nombre_mes.capitalize()} "
            f"{mes_actual[:4]}"
        ),
        bg=COLOR_FONDO,
        fg=COLOR_ROJO,
        font=("Arial", 12, "bold")
    ).pack(
        pady=(0, 15)
    )

    # =============================================
    # RESUMEN MENSUAL
    # =============================================

    cursor.execute(
        """
        SELECT
            COUNT(*),
            COALESCE(SUM(cantidad), 0),
            COALESCE(SUM(total), 0),
            COALESCE(SUM(precio_compra * cantidad), 0),
            COALESCE(SUM(ganancia), 0)
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
        """
    )

    resultado = cursor.fetchone()

    numero_ventas = resultado[0]
    unidades_vendidas = resultado[1]
    total_vendido = resultado[2]
    costo_productos = resultado[3]
    ganancia_bruta = resultado[4]

    marco_resumen = tk.Frame(
        ventana_reporte,
        bg=COLOR_ROJO
    )

    marco_resumen.pack(
        fill="x",
        padx=20,
        pady=(0, 15)
    )

    texto_resumen = (
        f"Ventas realizadas: {numero_ventas}    |    "
        f"Unidades vendidas: {unidades_vendidas}    |    "
        f"Total vendido: Bs {total_vendido:.2f}    |    "
        f"Costo: Bs {costo_productos:.2f}    |    "
        f"Ganancia bruta: Bs {ganancia_bruta:.2f}"
    )

    tk.Label(
        marco_resumen,
        text=texto_resumen,
        bg=COLOR_ROJO,
        fg="white",
        font=("Arial", 10, "bold"),
        wraplength=870,
        justify="center"
    ).pack(
        padx=15,
        pady=15
    )

    # =============================================
    # VENTAS POR DÍA
    # =============================================

    tk.Label(
        ventana_reporte,
        text="Ventas por día",
        bg=COLOR_FONDO,
        fg=COLOR_ROJO,
        font=("Arial", 13, "bold")
    ).pack(
        pady=(0, 8)
    )

    marco_dias = tk.Frame(
        ventana_reporte,
        bg=COLOR_FONDO
    )

    marco_dias.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=5
    )

    columnas_dias = (
        "fecha",
        "ventas",
        "unidades",
        "total",
        "ganancia"
    )

    tabla_dias = ttk.Treeview(
        marco_dias,
        columns=columnas_dias,
        show="headings"
    )

    tabla_dias.heading(
        "fecha",
        text="Fecha"
    )

    tabla_dias.heading(
        "ventas",
        text="Ventas"
    )

    tabla_dias.heading(
        "unidades",
        text="Unidades"
    )

    tabla_dias.heading(
        "total",
        text="Total vendido"
    )

    tabla_dias.heading(
        "ganancia",
        text="Ganancia bruta"
    )

    tabla_dias.column(
        "fecha",
        width=180,
        anchor="center"
    )

    tabla_dias.column(
        "ventas",
        width=120,
        anchor="center"
    )

    tabla_dias.column(
        "unidades",
        width=120,
        anchor="center"
    )

    tabla_dias.column(
        "total",
        width=180,
        anchor="center"
    )

    tabla_dias.column(
        "ganancia",
        width=180,
        anchor="center"
    )

    scrollbar_dias = ttk.Scrollbar(
        marco_dias,
        orient="vertical",
        command=tabla_dias.yview
    )

    tabla_dias.configure(
        yscrollcommand=scrollbar_dias.set
    )

    tabla_dias.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar_dias.pack(
        side="right",
        fill="y"
    )

    cursor.execute(
        """
        SELECT
            DATE(fecha, 'localtime'),
            COUNT(*),
            SUM(cantidad),
            SUM(total),
            SUM(ganancia)
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
        GROUP BY DATE(fecha, 'localtime')
        ORDER BY DATE(fecha, 'localtime') DESC
        """
    )

    ventas_por_dia = cursor.fetchall()

    for venta_dia in ventas_por_dia:

        fecha = venta_dia[0]
        ventas = venta_dia[1]
        unidades = venta_dia[2]
        total = venta_dia[3]
        ganancia = venta_dia[4]

        tabla_dias.insert(
            "",
            tk.END,
            values=(
                fecha,
                ventas,
                unidades,
                f"Bs {total:.2f}",
                f"Bs {ganancia:.2f}"
            )
        )

    # =============================================
    # DETALLE POR PRODUCTO
    # =============================================

    tk.Label(
        ventana_reporte,
        text="Productos más vendidos del mes",
        bg=COLOR_FONDO,
        fg=COLOR_ROJO,
        font=("Arial", 13, "bold")
    ).pack(
        pady=(12, 8)
    )

    marco_productos = tk.Frame(
        ventana_reporte,
        bg=COLOR_FONDO
    )

    marco_productos.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=5
    )

    columnas_productos = (
        "producto",
        "unidades",
        "total",
        "ganancia"
    )

    tabla_productos = ttk.Treeview(
        marco_productos,
        columns=columnas_productos,
        show="headings",
        height=6
    )

    tabla_productos.heading(
        "producto",
        text="Producto"
    )

    tabla_productos.heading(
        "unidades",
        text="Unidades"
    )

    tabla_productos.heading(
        "total",
        text="Total vendido"
    )

    tabla_productos.heading(
        "ganancia",
        text="Ganancia bruta"
    )

    tabla_productos.column(
        "producto",
        width=350
    )

    tabla_productos.column(
        "unidades",
        width=120,
        anchor="center"
    )

    tabla_productos.column(
        "total",
        width=180,
        anchor="center"
    )

    tabla_productos.column(
        "ganancia",
        width=180,
        anchor="center"
    )

    scrollbar_productos = ttk.Scrollbar(
        marco_productos,
        orient="vertical",
        command=tabla_productos.yview
    )

    tabla_productos.configure(
        yscrollcommand=scrollbar_productos.set
    )

    tabla_productos.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar_productos.pack(
        side="right",
        fill="y"
    )

    cursor.execute(
        """
        SELECT
            producto_nombre,
            SUM(cantidad),
            SUM(total),
            SUM(ganancia)
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
        GROUP BY producto_nombre
        ORDER BY SUM(cantidad) DESC
        """
    )

    productos_vendidos = cursor.fetchall()

    for producto in productos_vendidos:

        nombre = producto[0]
        unidades = producto[1]
        total = producto[2]
        ganancia = producto[3]

        tabla_productos.insert(
            "",
            tk.END,
            values=(
                nombre,
                unidades,
                f"Bs {total:.2f}",
                f"Bs {ganancia:.2f}"
            )
        )

    # =============================================
    # BOTÓN CERRAR
    # =============================================

    tk.Button(
        ventana_reporte,
        text="Cerrar",
        bg=COLOR_CREMA,
        fg=COLOR_ROJO,
        font=("Arial", 10, "bold"),
        command=ventana_reporte.destroy
    ).pack(
        pady=12
    )


# =============================================
# ACTUALIZAR INVENTARIO
# =============================================

def actualizar_inventario():

    cursor.execute(
        """
        SELECT
            COUNT(*),
            COALESCE(SUM(cantidad), 0),
            COALESCE(
                SUM(precio_compra * cantidad),
                0
            ),
            COALESCE(
                SUM(precio_venta * cantidad),
                0
            )
        FROM productos
        """
    )

    productos, unidades, valor_compra, valor_venta = (
        cursor.fetchone()
    )

    etiqueta_resumen.config(
        text=(
            f"Productos: {productos}    "
            f"Unidades: {unidades}    "
            f"Valor compra: Bs {valor_compra:.2f}    "
            f"Valor venta: Bs {valor_venta:.2f}"
        )
    )


# =============================================
# CERRAR APLICACIÓN
# =============================================

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

encabezado.pack(
    fill="x"
)

encabezado.pack_propagate(False)


# =============================================
# LOGO
# =============================================

imagen_original = tk.PhotoImage(
    file=ruta_recurso(
        "market_al_paso.png"
    )
)

imagen_logo = imagen_original.subsample(
    6,
    6
)

logo = tk.Label(
    encabezado,
    image=imagen_logo,
    bg=COLOR_ROJO
)

logo.pack(
    side="left",
    padx=15,
    pady=5
)


tk.Label(
    encabezado,
    text="MARKET al PASO",
    bg=COLOR_ROJO,
    fg="white",
    font=("Arial", 26, "bold")
).pack(
    pady=(15, 0)
)


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

panel.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=20
)


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

formulario.pack(
    fill="x",
    pady=(0, 15)
)


tk.Label(
    formulario,
    text="Nombre:",
    bg=COLOR_FONDO
).grid(
    row=0,
    column=0,
    padx=10,
    pady=10
)

entrada_nombre = tk.Entry(
    formulario,
    width=20
)

entrada_nombre.grid(
    row=0,
    column=1,
    padx=5
)


tk.Label(
    formulario,
    text="Categoría:",
    bg=COLOR_FONDO
).grid(
    row=0,
    column=2,
    padx=10
)

entrada_categoria = tk.Entry(
    formulario,
    width=20
)

entrada_categoria.grid(
    row=0,
    column=3,
    padx=5
)


tk.Label(
    formulario,
    text="Compra:",
    bg=COLOR_FONDO
).grid(
    row=1,
    column=0,
    padx=10,
    pady=10
)

entrada_compra = tk.Entry(
    formulario,
    width=20
)

entrada_compra.grid(
    row=1,
    column=1,
    padx=5
)


tk.Label(
    formulario,
    text="Venta:",
    bg=COLOR_FONDO
).grid(
    row=1,
    column=2,
    padx=10
)

entrada_venta = tk.Entry(
    formulario,
    width=20
)

entrada_venta.grid(
    row=1,
    column=3,
    padx=5
)


tk.Label(
    formulario,
    text="Código de barras:",
    bg=COLOR_FONDO
).grid(
    row=0,
    column=4,
    padx=10
)

entrada_codigo_barras = tk.Entry(
    formulario,
    width=20
)

entrada_codigo_barras.grid(
    row=0,
    column=5,
    padx=5
)


tk.Label(
    formulario,
    text="Cantidad:",
    bg=COLOR_FONDO
).grid(
    row=2,
    column=0,
    padx=10,
    pady=10
)

entrada_cantidad = tk.Entry(
    formulario,
    width=20
)

entrada_cantidad.grid(
    row=2,
    column=1,
    padx=5
)


# =============================================
# BOTONES DEL FORMULARIO
# =============================================

tk.Button(
    formulario,
    text="Registrar",
    bg=COLOR_VERDE,
    fg="white",
    font=("Arial", 10, "bold"),
    command=registrar_producto
).grid(
    row=2,
    column=2,
    padx=5
)


tk.Button(
    formulario,
    text="Modificar",
    bg=COLOR_AMARILLO,
    fg="#333333",
    font=("Arial", 10, "bold"),
    command=modificar_producto
).grid(
    row=2,
    column=3,
    padx=5
)


tk.Button(
    formulario,
    text="Eliminar",
    bg=COLOR_ROJO,
    fg="white",
    font=("Arial", 10, "bold"),
    command=eliminar_producto
).grid(
    row=2,
    column=4,
    padx=5
)


tk.Button(
    formulario,
    text="Limpiar",
    bg=COLOR_CREMA,
    fg=COLOR_ROJO,
    font=("Arial", 10, "bold"),
    command=limpiar_formulario
).grid(
    row=2,
    column=5,
    padx=5
)


# =============================================
# BÚSQUEDA
# =============================================

barra_busqueda = tk.Frame(
    panel,
    bg=COLOR_FONDO
)

barra_busqueda.pack(
    fill="x",
    pady=(0, 10)
)


tk.Label(
    barra_busqueda,
    text="Buscar:",
    bg=COLOR_FONDO,
    fg=COLOR_ROJO,
    font=("Arial", 10, "bold")
).pack(
    side="left"
)


entrada_busqueda = tk.Entry(
    barra_busqueda,
    width=30
)

entrada_busqueda.pack(
    side="left",
    padx=10
)


tk.Button(
    barra_busqueda,
    text="Buscar",
    bg=COLOR_VERDE,
    fg="white",
    command=buscar_producto
).pack(
    side="left"
)


tk.Button(
    barra_busqueda,
    text="Mostrar todos",
    bg=COLOR_CREMA,
    fg=COLOR_ROJO,
    command=cargar_productos
).pack(
    side="left",
    padx=5
)


# =============================================
# TABLA PRINCIPAL
# =============================================

columnas = (
    "id",
    "nombre",
    "categoria",
    "compra",
    "venta",
    "cantidad",
    "codigo_barras"
)

tabla = ttk.Treeview(
    panel,
    columns=columnas,
    show="headings"
)

tabla.heading(
    "id",
    text="id"
)

tabla.heading(
    "nombre",
    text="Producto"
)

tabla.heading(
    "categoria",
    text="Categoria"
)

tabla.heading(
    "compra",
    text="Precio compra"
)

tabla.heading(
    "venta",
    text="Precio venta"
)

tabla.heading(
    "cantidad",
    text="Stock"
)

tabla.heading(
    "codigo_barras",
    text="Código de barras"
)

tabla.column(
    "id",
    width=50,
    anchor="center"
)

tabla.column(
    "nombre",
    width=200
)

tabla.column(
    "categoria",
    width=150
)

tabla.column(
    "compra",
    width=120,
    anchor="center"
)

tabla.column(
    "venta",
    width=120,
    anchor="center"
)

tabla.column(
    "cantidad",
    width=100,
    anchor="center"
)

tabla.column(
    "codigo_barras",
    width=160
)

# =============================================
# COLOR STOCK BAJO
# =============================================

tabla.tag_configure(
    "stock_bajo",
    foreground=COLOR_ROJO
)

tabla.bind(
    "<Double-1>",
    seleccionar_producto
)


# =============================================
# BARRA INFERIOR
# =============================================

barra_inferior = tk.Frame(
    panel,
    bg=COLOR_ROJO,
    height=50
)

barra_inferior.pack(
    side="bottom",
    fill="x",
    pady=(15, 0)
)

barra_inferior.pack_propagate(
    False
)


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


# =============================================
# BOTÓN REPORTE MENSUAL
# =============================================

tk.Button(
    barra_inferior,
    text="Reporte mensual",
    bg=COLOR_VERDE,
    fg="white",
    font=("Arial", 10, "bold"),
    command=ver_reporte_mensual
).pack(
    side="right",
    padx=5,
    pady=5
)


# =============================================
# BOTÓN REPORTE DIARIO
# =============================================

tk.Button(
    barra_inferior,
    text="Reporte diario",
    bg=COLOR_AMARILLO,
    fg="#333333",
    font=("Arial", 10, "bold"),
    command=ver_reporte_diario
).pack(
    side="right",
    padx=5,
    pady=5
)


# =============================================
# BOTÓN HISTORIAL
# =============================================

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


# =============================================
# BOTÓN NUEVA VENTA
# =============================================

tk.Button(
    barra_inferior,
    text="Nueva venta",
    bg=COLOR_VERDE,
    fg="white",
    font=("Arial", 10, "bold"),
    command=nueva_venta
).pack(
    side="right",
    padx=5,
    pady=5
)


# =============================================
# BOTÓN REGISTRAR VENTA MANUAL
# =============================================

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


# =============================================
# BOTÓN SALIR
# =============================================

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


# =============================================
# TABLA
# =============================================

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