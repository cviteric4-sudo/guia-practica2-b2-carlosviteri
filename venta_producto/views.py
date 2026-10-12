from abc import ABC, abstractmethod
from models import Cliente, Producto, Venta
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


class CrudBase(ABC):
    @abstractmethod
    def leer(self): pass

    @abstractmethod
    def obtener(self, id_registro): pass

    @abstractmethod
    def buscar(self, texto): pass

    @abstractmethod
    def siguiente(self): pass

    @abstractmethod
    def crear(self, datos): pass

    @abstractmethod
    def actualizar(self, id_registro, datos): pass

    @abstractmethod
    def eliminar(self, id_registro): pass


class ClienteController(CrudBase):
    def __init__(self, archivo="data/clientes.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = [Cliente.desde_diccionario(d) for d in self.gestor.leer()]

    def guardar(self):
        self.gestor.guardar([c.a_diccionario() for c in self.lista])

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "apellido", "email"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email inválido: '{email}'"
            usados = {c.email for c in self.lista if c.id != id_actual}
            if email in usados:
                return "Ese email ya está registrado"

        telefono = str(datos.get("telefono", "")).strip()
        if telefono != "" and not telefono.isdigit():
            return "El teléfono solo puede tener números"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_cliente):
        return next((c for c in self.lista if c.id == id_cliente), None)

    def buscar(self, texto):
        texto = texto.strip().lower()
        if not texto:
            return []
        return [
            c for c in self.lista
            if texto in c.nombre.lower() or texto in c.apellido.lower()
            or texto in c.email or texto in c.telefono or texto in c.ciudad.lower()
        ]

    def siguiente(self):
        return max([c.id for c in self.lista], default=0) + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        cliente = Cliente(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["apellido"]).strip().title(),
            str(datos["email"]).strip().lower(),
            str(datos.get("telefono", "")).strip(),
            str(datos.get("ciudad", "")).strip().title()
        )
        self.lista.append(cliente)
        self.guardar()
        return True, f"Cliente creado: {cliente.etiqueta()}"

    def actualizar(self, id_cliente, datos):
        cliente = self.obtener(id_cliente)
        if cliente is None:
            return False, f"No existe un cliente con id {id_cliente}"
        if not datos:
            return False, "No se indicó ningún cambio"

        descon = set(datos) - {"nombre", "apellido", "email", "telefono", "ciudad"}
        if descon:
            return False, f"Campos no válidos: {', '.join(sorted(descon))}"

        error = self.validar(datos, id_cliente)
        if error:
            return False, error

        for campo, valor in datos.items():
            valor = str(valor).strip()
            if campo in ("nombre", "apellido", "ciudad"):
                valor = valor.title()
            elif campo == "email":
                valor = valor.lower()
            setattr(cliente, campo, valor)

        self.guardar()
        return True, f"Cliente {id_cliente} actualizado"

    def eliminar(self, id_cliente):
        cliente = self.obtener(id_cliente)
        if cliente is None:
            return False, f"No existe un cliente con id {id_cliente}"

        self.lista.remove(cliente)
        self.guardar()
        return True, f"Cliente {id_cliente} eliminado"

    def ciudades(self):
        return sorted({c.ciudad for c in self.lista if c.ciudad})


class ProductoController(CrudBase):
    def __init__(self, archivo="data/productos.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = [Producto.desde_diccionario(d) for d in self.gestor.leer()]

    def guardar(self):
        self.gestor.guardar([p.a_diccionario() for p in self.lista])

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "precio"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "precio" in datos:
            if not Producto.es_precio_valido(datos["precio"]):
                return f"Precio inválido: '{datos['precio']}' (debe ser mayor a 0)"

        if "stock" in datos:
            stock_str = str(datos["stock"]).strip()
            if stock_str != "":
                try:
                    val = int(stock_str)
                    if val < 0:
                        return "El stock no puede ser negativo"
                except ValueError:
                    return "El stock debe ser un número entero"

        if "nombre" in datos:
            nombre = str(datos["nombre"]).strip().title()
            for otro in self.lista:
                if otro.nombre == nombre and otro.id != id_actual:
                    return f"Ya existe un producto llamado '{nombre}'"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_producto):
        return next((p for p in self.lista if p.id == id_producto), None)

    def buscar(self, texto):
        texto = texto.strip().lower()
        if not texto:
            return []
        return [p for p in self.lista if texto in p.nombre.lower()]

    def siguiente(self):
        return max([p.id for p in self.lista], default=0) + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        stock_str = str(datos.get("stock", "")).strip()
        producto = Producto(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            float(datos["precio"]),
            int(stock_str) if stock_str != "" else 0
        )
        self.lista.append(producto)
        self.guardar()
        return True, f"Producto creado: {producto.etiqueta()}"

    def actualizar(self, id_producto, datos):
        producto = self.obtener(id_producto)
        if producto is None:
            return False, f"No existe un producto con id {id_producto}"
        if not datos:
            return False, "No se indicó ningún cambio"

        descon = set(datos) - {"nombre", "precio", "stock"}
        if descon:
            return False, f"Campos no válidos: {', '.join(sorted(descon))}"

        error = self.validar(datos, id_producto)
        if error:
            return False, error

        if "nombre" in datos:
            producto.nombre = str(datos["nombre"]).strip().title()
        if "precio" in datos:
            producto.precio = float(datos["precio"])
        if "stock" in datos:
            producto.stock = int(datos["stock"])

        self.guardar()
        return True, f"Producto {id_producto} actualizado"

    def eliminar(self, id_producto):
        producto = self.obtener(id_producto)
        if producto is None:
            return False, f"No existe un producto con id {id_producto}"

        self.lista.remove(producto)
        self.guardar()
        return True, f"Producto {id_producto} eliminado"

    def con_stock_bajo(self):
        return [p for p in self.lista if p.stock_bajo()]


class VentaController(CrudBase):
    def __init__(self, clientes, productos, archivo="data/ventas.json"):
        self.clientes = clientes
        self.productos = productos
        self.gestor = GestorJSON(archivo)
        self.lista = [Venta.desde_diccionario(d) for d in self.gestor.leer()]

    def guardar(self):
        self.gestor.guardar([v.a_diccionario() for v in self.lista])

    def validar(self, datos):
        try:
            cliente_id = int(datos.get("cliente_id", 0))
            producto_id = int(datos.get("producto_id", 0))
            cantidad = int(datos.get("cantidad", 0))
        except (TypeError, ValueError):
            return "cliente_id, producto_id y cantidad deben ser enteros"

        if cantidad <= 0:
            return "La cantidad debe ser mayor a 0"

        if self.clientes.obtener(cliente_id) is None:
            return f"No existe un cliente con id {cliente_id}"

        producto = self.productos.obtener(producto_id)
        if producto is None:
            return f"No existe un producto con id {producto_id}"

        if not producto.hay_stock(cantidad):
            return f"Stock insuficiente de {producto.nombre}: hay {producto.stock}, piden {cantidad}"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_venta):
        return next((v for v in self.lista if v.id == id_venta), None)

    def buscar(self, texto):
        texto = texto.strip()
        if not texto:
            return []
        return [v for v in self.lista if texto in v.fecha]

    def siguiente(self):
        return max([v.id for v in self.lista], default=0) + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        producto = self.productos.obtener(int(datos["producto_id"]))
        venta = Venta(
            self.siguiente(),
            int(datos["cliente_id"]),
            producto.id,
            int(datos["cantidad"]),
            producto.precio
        )

        producto.descontar_stock(venta.cantidad)
        self.productos.guardar()
        self.lista.append(venta)
        self.guardar()
        return True, f"Venta {venta.id} registrada por ${venta.calcular_total():.2f}"

    def actualizar(self, id_venta, datos):
        return False, "Las ventas no se pueden modificar: anúlela y registre otra"

    @abstractmethod
    def eliminar(self, id_venta):
        venta = self.obtener(id_venta)
        if venta is None:
            return False, f"No existe la venta {id_venta}"

        producto = self.productos.obtener(venta.producto_id)
        if producto is not None:
            producto.devolver_stock(venta.cantidad)
            self.productos.guardar()

        self.lista.remove(venta)
        self.guardar()
        return True, f"Venta {id_venta} anulada y stock devuelto"

    def comprobante(self, id_venta):
        venta = self.obtener(id_venta)
        if venta is None:
            return None

        cliente = self.clientes.obtener(venta.cliente_id)
        producto = self.productos.obtener(venta.producto_id)
        total = venta.calcular_total()

        texto = f"COMPROBANTE #{venta.id}   fecha: {venta.fecha}\n"
        texto += f"Cliente : {cliente.nombre_completo() if cliente else 'eliminado'}\n"
        texto += f"Producto: {producto.nombre if producto else 'eliminado'}\n"
        texto += f"Cantidad: {venta.cantidad} x ${venta.precio_unitario:.2f}\n"
        texto += "-" * 42 + "\n"
        texto += f"SUBTOTAL: ${total:.2f}\n"
        texto += f"TOTAL con IVA: ${Producto.con_iva(total):.2f}"
        return texto

    def total_vendido(self):
        return round(sum(v.calcular_total() for v in self.lista), 2)