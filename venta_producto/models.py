from datetime import date


class ModeloBase:
    """Clase base para la serialización y representación de entidades."""

    def __init__(self, id_registro):
        self.id = int(id_registro)

    @classmethod
    def desde_diccionario(cls, datos):
        datos = dict(datos)
        id_registro = datos.pop("id")
        return cls(id_registro, **datos)

    def a_diccionario(self):
        return {"id": self.id}

    def etiqueta(self):
        return f"registro {self.id}"

    def __str__(self):
        return f"[{self.id}] {self.etiqueta()}"


class Persona(ModeloBase):
    def __init__(self, id_registro, nombre, apellido, email):
        super().__init__(id_registro)
        self.nombre = str(nombre)
        self.apellido = str(apellido)
        self.email = str(email)

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update({
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email
        })
        return datos

    def etiqueta(self):
        return self.nombre_completo()


class Cliente(Persona):
    def __init__(self, id_registro, nombre, apellido, email, telefono="", ciudad=""):
        super().__init__(id_registro, nombre, apellido, email)
        self.telefono = str(telefono)
        self.ciudad = str(ciudad)

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update({
            "telefono": self.telefono,
            "ciudad": self.ciudad
        })
        return datos

    def etiqueta(self):
        return f"{super().etiqueta()} · {self.email} · {self.ciudad or 'sin ciudad'}"


class Producto(ModeloBase):
    STOCK_MINIMO = 5
    IVA = 0.15

    def __init__(self, id_registro, nombre, precio, stock=0):
        super().__init__(id_registro)
        self.nombre = str(nombre)
        self.precio = float(precio)
        self.stock = int(stock)

    @staticmethod
    def es_precio_valido(valor):
        try:
            return float(valor) > 0
        except (TypeError, ValueError):
            return False

    @staticmethod
    def con_iva(monto):
        return round(float(monto) * (1 + Producto.IVA), 2)

    def stock_bajo(self):
        return self.stock <= Producto.STOCK_MINIMO

    def hay_stock(self, cantidad):
        return 0 < cantidad <= self.stock

    def descontar_stock(self, cantidad):
        self.stock -= cantidad

    def devolver_stock(self, cantidad):
        self.stock += cantidad

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update({
            "nombre": self.nombre,
            "precio": self.precio,
            "stock": self.stock
        })
        return datos

    def etiqueta(self):
        alerta = " ⚠ stock bajo" if self.stock_bajo() else ""
        return f"{self.nombre} · ${self.precio:.2f} · stock {self.stock}{alerta}"


class Venta(ModeloBase):
    def __init__(self, id_registro, cliente_id, producto_id, cantidad, precio_unitario, fecha=""):
        super().__init__(id_registro)
        self.cliente_id = int(cliente_id)
        self.producto_id = int(producto_id)
        self.cantidad = int(cantidad)
        self.precio_unitario = float(precio_unitario)
        self.fecha = fecha or date.today().isoformat()

    def calcular_total(self):
        return round(self.cantidad * self.precio_unitario, 2)

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update({
            "cliente_id": self.cliente_id,
            "producto_id": self.producto_id,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
            "fecha": self.fecha
        })
        return datos

    def etiqueta(self):
        return (f"{self.fecha} · cliente {self.cliente_id} · "
                f"{self.cantidad} x producto {self.producto_id} "
                f"= ${self.calcular_total():.2f}")