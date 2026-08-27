import sqlite3


# =============================================
# CONEXIÓN CON SQLITE
# =============================================

conexion = sqlite3.connect("store_manager.db")

cursor = conexion.cursor()


# =============================================
# CREAR TABLA
# =============================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS productos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL,
    precio_compra REAL NOT NULL,
    precio_venta REAL NOT NULL,
    cantidad INTEGER NOT NULL
)
""")

conexion.commit()


# =============================================
# ENCABEZADO
# =============================================

print("====================")
print("     STORE MANAGER")
print("====================")

print("Sistema de gestión de tienda")
print("Versión 0.3")

print()


# =============================================
# PEDIR FLOAT
# =============================================

def pedir_float(mensaje):

    while True:

        try:

            valor = float(input(mensaje))

            if valor < 0:
                print("Introduzca un número positivo.")

            else:
                return valor

        except ValueError:
            print("Introduzca un valor válido.")


# =============================================
# PEDIR ENTERO
# =============================================

def pedir_entero(mensaje):

    while True:

        try:

            valor = int(input(mensaje))

            if valor < 0:
                print("Introduzca un número positivo.")

            else:
                return valor

        except ValueError:
            print("Introduzca un valor válido.")


# =============================================
# REGISTRAR PRODUCTO
# =============================================

def registrar_producto():

    print()
    print("----- REGISTRAR PRODUCTO -----")

    nombre = input("Nombre: ").strip()

    cursor.execute(
        "SELECT * FROM productos WHERE LOWER(nombre) = LOWER(?)",
        (nombre,)
    )

    producto_existente = cursor.fetchone()

    if producto_existente:
        print("Error: el producto ya existe.")
        return

    categoria = input("Categoría: ").strip()

    precio_compra = pedir_float("Precio de compra: ")


    while True:

        precio_venta = pedir_float("Precio de venta: ")

        if precio_venta < precio_compra:
            print(
                "Error: el precio de venta no puede ser "
                "menor al precio de compra."
            )

        else:
            break


    cantidad = pedir_entero("Cantidad: ")


    cursor.execute("""
        INSERT INTO productos(
            nombre,
            categoria,
            precio_compra,
            precio_venta,
            cantidad
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        nombre,
        categoria,
        precio_compra,
        precio_venta,
        cantidad
    ))

    conexion.commit()

    print()
    print("Producto registrado correctamente.")


# =============================================
# VER PRODUCTOS
# =============================================

def ver_productos():

    print()
    print("----- PRODUCTOS -----")

    cursor.execute("SELECT * FROM productos")

    productos = cursor.fetchall()

    if len(productos) == 0:
        print("No hay productos registrados.")
        return


    for producto in productos:

        print()
        print("ID:", producto[0])
        print("Nombre:", producto[1])
        print("Categoría:", producto[2])
        print("Precio de compra:", producto[3])
        print("Precio de venta:", producto[4])
        print("Cantidad:", producto[5])


# =============================================
# BUSCAR PRODUCTO
# =============================================

def buscar_producto():

    print()
    print("----- BUSCAR PRODUCTO -----")

    nombre_busqueda = input("Nombre del producto: ").strip()


    cursor.execute(
        "SELECT * FROM productos WHERE LOWER(nombre) = LOWER(?)",
        (nombre_busqueda,)
    )


    producto = cursor.fetchone()


    if producto:

        print()
        print("Producto encontrado.")
        print("ID:", producto[0])
        print("Nombre:", producto[1])
        print("Categoría:", producto[2])
        print("Precio de compra:", producto[3])
        print("Precio de venta:", producto[4])
        print("Cantidad:", producto[5])

    else:

        print()
        print("Producto no encontrado.")


# =============================================
# MODIFICAR PRODUCTO
# =============================================

def modificar_producto():

    print()
    print("----- MODIFICAR PRODUCTO -----")

    nombre_busqueda = input("Nombre del producto: ").strip()

    cursor.execute(
        "SELECT * FROM productos WHERE LOWER(nombre) = LOWER(?)",
        (nombre_busqueda,)
    )
    producto = cursor.fetchone()

    if producto: 

        print()
        print("Producto encontrado.")
        print("Deja vacio un campo si no quieres modificarlo.")

        print()
        print("Nombre actual:", producto[1])
        print("Categoría actual:", producto[2])
        print("Precio de compra actual:", producto[3])
        print("Precio de venta actual:", producto[4])
        print("Cantidad actual:", producto[5])

        print()

        # ---------------------------------------------
        # NUEVO NOMBRE
        # ---------------------------------------------

        nuevo_nombre = input("Nuevo nombre: ").strip()

        if nuevo_nombre == "":
            nuevo_nombre = producto[1]

        # ---------------------------------------------
        # NUEVA CATEGORÍA
        # ---------------------------------------------

        nueva_categoria = input("Nueva categoría: ").strip()

        if nueva_categoria == "":
            nueva_categoria = producto[2]
        
        # ---------------------------------------------
        # NUEVO PRECIO DE COMPRA
        # ---------------------------------------------

        while True:
            nuevo_precio_compra = input("Nuevo precio de compra: ").strip()

            if nuevo_precio_compra == "":
                nuevo_precio_compra = producto[3]
                break
            try:
                nuevo_precio_compra = float(nuevo_precio_compra)

                if nuevo_precio_compra < 0:
                    print("Introduzca un número positivo.")
                else:
                    break

            except ValueError:
                print("Introduzca un valor válido.")

        # ---------------------------------------------
        # NUEVO PRECIO DE VENTA
        # ---------------------------------------------
         
        while True:
            nuevo_precio_venta = input("Nuevo precio de venta: ").strip()

            if nuevo_precio_venta == "":
                nuevo_precio_venta = producto[4]
                break

            try:

                nuevo_precio_venta = float(nuevo_precio_venta)

                if nuevo_precio_venta < 0:

                    print("Introduzca un número positivo.")

                elif nuevo_precio_venta < nuevo_precio_compra:
                    print()
                    print("Error: el precio de venta no puede ser menor al precio de compra")
                    return

                else:
                    break

            except ValueError:

                print("Introduzca un valor válido.")

        # ---------------------------------------------
        # NUEVA CANTIDAD
        # ---------------------------------------------  

        while True:

            nueva_cantidad = input("Nueva cantidad: ").strip()

            if nueva_cantidad == "":
                nueva_cantidad = producto [5]
                break

            try:

                nueva_cantidad = int(nueva_cantidad)

                if nueva_cantidad < 0:
                    print("Introduzca un número positivo.")
                else:
                    break

            except ValueError:
                print("Introduzca un valor válido.")  

        # ---------------------------------------------
        # ACTUALIZAR PRODUCTO
        # ---------------------------------------------

        cursor.execute("""
            UPDATE productos
            SET nombre = ?,
                categoria = ?,
                precio_compra = ?,
                precio_venta = ?,
                cantidad = ?
            WHERE id = ?""",(
                nuevo_nombre,
                nueva_categoria,
                nuevo_precio_compra,
                nuevo_precio_venta,
                nueva_cantidad,
                producto[0]
            ))

        conexion.commit()

        print()
        print("Producto modificado correctamente.")

    else:

        print()
        print("Producto no encontrado.")


# =============================================
# ELIMINAR PRODUCTO
# =============================================

def eliminar_producto():

    print()
    print("----- ELIMINAR PRODUCTO -----")

    nombre_eliminar = input("Nombre del producto: ").strip()


    cursor.execute(
        "SELECT * FROM productos WHERE LOWER(nombre) = LOWER(?)",
        (nombre_eliminar,)
    )


    producto = cursor.fetchone()


    if producto:

        cursor.execute(
            "DELETE FROM productos WHERE id = ?",
            (producto[0],)
        )

        conexion.commit()

        print()
        print("Producto eliminado correctamente.")

    else:

        print()
        print("Producto no encontrado.")


# =============================================
# REGISTRAR VENTA
# =============================================

def registrar_venta():

    print()
    print("----- REGISTRAR VENTA -----")

    nombre_venta = input("Nombre del producto vendido: ").strip()


    while True:

        cantidad_venta = pedir_entero("Cantidad vendida: ")

        if cantidad_venta == 0:
            print(
                "Error: la cantidad vendida debe ser "
                "mayor que cero."
            )

        else:
            break


    cursor.execute(
        "SELECT * FROM productos WHERE LOWER(nombre) = LOWER(?)",
        (nombre_venta,)
    )


    producto = cursor.fetchone()


    if producto:

        if cantidad_venta <= producto[5]:

            nueva_cantidad = producto[5] - cantidad_venta

            total_venta = producto[4] * cantidad_venta


            cursor.execute(
                "UPDATE productos SET cantidad = ? WHERE id = ?",
                (nueva_cantidad, producto[0])
            )


            conexion.commit()


            print()
            print("Venta registrada correctamente.")
            print("Producto:", producto[1])
            print("Cantidad vendida:", cantidad_venta)
            print("Total de venta:", total_venta)
            print("Stock restante:", nueva_cantidad)

        else:

            print()
            print("No hay suficiente stock.")

    else:

        print()
        print("Producto no encontrado.")


# =============================================
# VER INVENTARIO
# =============================================

def ver_inventario():

    print()
    print("----- INVENTARIO -----")


    cursor.execute("SELECT * FROM productos")

    productos = cursor.fetchall()


    if len(productos) == 0:
        print("No hay productos registrados.")
        return


    for producto in productos:

        valor_inventario = producto[3] * producto[5]

        print()
        print("Producto:", producto[1])
        print("Stock:", producto[5])
        print("Valor de inventario:", valor_inventario)


# =============================================
# MENÚ PRINCIPAL
# =============================================

option = ""


while option != "8":

    print()
    print("====================")
    print("        MENU")
    print("====================")

    print("1. Registrar producto")
    print("2. Ver productos")
    print("3. Buscar producto")
    print("4. Modificar producto")
    print("5. Eliminar producto")
    print("6. Registrar venta")
    print("7. Ver inventario")
    print("8. Salir")


    option = input("Selecciona una opción: ")


    if option == "1":

        registrar_producto()

    elif option == "2":

        ver_productos()

    elif option == "3":

        buscar_producto()

    elif option == "4":

        modificar_producto()

    elif option == "5":

        eliminar_producto()

    elif option == "6":

        registrar_venta()

    elif option == "7":

        ver_inventario()

    elif option == "8":

        print()
        print("Hasta luego.")

    else:

        print()
        print("Opción no válida.")


conexion.close()