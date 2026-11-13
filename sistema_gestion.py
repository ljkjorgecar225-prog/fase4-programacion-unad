import logging
from abc import ABC, abstractmethod

# ==========================================
# CONFIGURACIÓN DEL ARCHIVO DE LOGS
# ==========================================
# Configuramos el sistema para que guarde los errores y eventos en un archivo de texto,
# evitando que la aplicación se caiga y manteniendo la estabilidad.
logging.basicConfig(
    filename='sistema_errores.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ==========================================
# EXCEPCIONES PERSONALIZADAS
# ==========================================
class ErrorDatoInvalido(Exception):
    """Excepción lanzada cuando un dato ingresado no cumple con las validaciones."""
    pass

class ErrorOperacionNoPermitida(Exception):
    """Excepción lanzada cuando se intenta realizar una acción no autorizada o ilógica."""
    pass

class ErrorServicioNoDisponible(Exception):
    """Excepción lanzada cuando el servicio seleccionado no está activo o disponible."""
    pass


# ==========================================
# CLASES BASE Y ABSTRACTAS (POO)
# ==========================================
class EntidadSistema(ABC):
    """Clase abstracta general que representa cualquier entidad principal del sistema."""
    
    def __init__(self, id_entidad):
        self._id_entidad = id_entidad  # Encapsulación del ID

    @abstractmethod
    def obtener_detalles(self):
        """Método abstracto obligatorios para las clases hijas."""
        pass


class Cliente(EntidadSistema):
    """Clase Cliente con validaciones estrictas y encapsulación de datos personales."""
    
    def __init__(self, id_entidad, nombre, correo, telefono):
        super().__init__(id_entidad)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or len(valor.strip()) < 3:
            logging.error(f"Intento de registrar cliente con nombre inválido: {valor}")
            raise ErrorDatoInvalido("El nombre del cliente es muy corto o está vacío.")
        self._nombre = valor

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if "@" not in valor or "." not in valor:
            logging.error(f"Intento de registrar cliente con correo inválido: {valor}")
            raise ErrorDatoInvalido("El formato del correo electrónico no es válido.")
        self._correo = valor

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        if not str(valor).isdigit() or len(str(valor)) < 7:
            logging.error(f"Intento de registrar cliente con teléfono inválido: {valor}")
            raise ErrorDatoInvalido("El teléfono debe contener solo números y al menos 7 dígitos.")
        self._telefono = valor

    def obtener_detalles(self):
        return f"Cliente ID: {self._id_entidad} | Nombre: {self._nombre} | Correo: {self._correo}"


# ==========================================
# CLASE ABSTRACTA SERVICIO Y ESPECIALIZADOS
# ==========================================
class Servicio(ABC):
    """Clase abstracta Servicio para aplicar polimorfismo y herencia."""
    
    def __init__(self, codigo_servicio, nombre_servicio, costo_base):
        self.codigo_servicio = codigo_servicio
        self.nombre_servicio = nombre_servicio
        self.costo_base = costo_base
        self.disponible = True

    @abstractmethod
    def calcular_costo(self):
        """Método abstracto para el cálculo de costos con polimorfismo."""
        pass

    def obtener_detalles(self):
        return f"Servicio [{self.codigo_servicio}]: {self.nombre_servicio} - Costo Base: ${self.costo_base}"


class ReservaSalas(Servicio):
    """Servicio especializado 1: Reservas de salas."""
    
    def __init__(self, codigo, nombre, costo_base, capacidad_personas):
        super().__init__(codigo, nombre, costo_base)
        self.capacidad_personas = capacidad_personas

    # Método sobrecargado simulado (acepta descuento opcional)
    def calcular_costo(self, descuento_porcentaje=0):
        try:
            if descuento_porcentaje < 0 or descuento_porcentaje > 100:
                raise ErrorDatoInvalido("El porcentaje de descuento debe estar entre 0 y 100.")
            total = self.costo_base * (1 - descuento_porcentaje / 100)
            return total
        except Exception as e:
            logging.warning(f"Error en cálculo de salas: {e}")
            return self.costo_base


class AlquilerEquipos(Servicio):
    """Servicio especializado 2: Alquiler de equipos tecnológicos."""
    
    def __init__(self, codigo, nombre, costo_base, horas):
        super().__init__(codigo, nombre, costo_base)
        self.horas = horas

    # Método sobrecargado simulado (acepta horas extra o tarifa fija)
    def calcular_costo(self, horas_adicionales=0):
        try:
            if horas_adicionales < 0:
                raise ErrorDatoInvalido("Las horas adicionales no pueden ser negativas.")
            total = self.costo_base + (horas_adicionales * 15000)
            return total
        except Exception as e:
            logging.warning(f"Error en cálculo de equipos: {e}")
            return self.costo_base


class AsesoriasEspecializadas(Servicio):
    """Servicio especializado 3: Asesorías técnicas especializadas."""
    
    def __init__(self, codigo, nombre, costo_base, nivel_专家):
        super().__init__(codigo, nombre, costo_base)
        self.nivel_experto = nivel_专家

    # Método sobrecargado simulado (acepta recargo por complejidad)
    def calcular_costo(self, recargo_complejidad=1.0):
        try:
            if recargo_complejidad < 1.0:
                raise ErrorDatoInvalido("El factor de recargo no puede ser menor a 1.0.")
            total = self.costo_base * recargo_complejidad
            return total
        except Exception as e:
            logging.warning(f"Error en cálculo de asesorías: {e}")
            return self.costo_base

# Bloque de Clase Reserva y Gestión de Estados desarrollado por: Jorge Isaac Carvajal Alvear
# ==========================================
# CLASE RESERVA Y GESTIÓN DE ESTADOS
# ==========================================
class Reserva:
    """Clase Reserva que integra cliente, servicio, duración y manejo de excepciones."""
    
    contador_reservas = 1

    def __init__(self, cliente: Cliente, servicio: Servicio, duracion_dias: int):
        self.id_reserva = Reserva.contador_reservas
        Reserva.contador_reservas += 1
        self.cliente = cliente
        self.servicio = servicio
        self.duracion_dias = duracion_dias
        self.estado = "Creada"

    def confirmar_reserva(self):
        try:
            if not self.servicio.disponible:
                raise ErrorServicioNoDisponible(f"El servicio {self.servicio.nombre_servicio} no está disponible.")
            if self.duracion_dias <= 0:
                raise ErrorDatoInvalido("La duración de la reserva debe ser mayor a 0 días.")
            
            self.estado = "Confirmada"
            logging.info(f"Reserva #{self.id_reserva} confirmada con éxito para el cliente {self.cliente.nombre}.")
            print(f"-> [ÉXITO] Reserva #{self.id_reserva} confirmada correctamente.")
        
        except ErrorServicioNoDisponible as e:
            self.estado = "Fallida"
            logging.error(f"Fallo en Reserva #{self.id_reserva}: {e}")
            print(f"-> [ERROR CONTROLADO] {e}")
        except ErrorDatoInvalido as e:
            self.estado = "Fallida"
            logging.error(f"Fallo en datos de Reserva #{self.id_reserva}: {e}")
            print(f"-> [ERROR CONTROLADO] {e}")
        except Exception as e:
            self.estado = "Error Crítico"
            logging.critical(f"Error inesperado en Reserva #{self.id_reserva}: {e}")
            print(f"-> [CRÍTICO] Ocurrió un error inesperado.")
        finally:
            print(f"-> [PROCESO FINALIZADO] Estado actual de la reserva: {self.estado}\n")

    def cancelar_reserva(self):
        self.estado = "Cancelada"
        logging.info(f"La reserva #{self.id_reserva} ha sido cancelada.")
        print(f"-> La reserva #{self.id_reserva} fue cancelada correctamente.")

# Bloque Principal (Main) y 10 Simulaciones desarrollado por: Jorge Isaac Carvajal Alvear
# ==========================================
# SIMULACIÓN DE LAS 10 OPERACIONES (MAIN)
# ==========================================
if __name__ == "__main__":
    print("=== INICIANDO SIMULACIÓN DEL SISTEMA SOFTWARE FJ ===\n")

    # Listas en memoria (sin bases de datos)
    clientes_registrados = []
    servicios_disponibles = []
    historial_reservas = []

    # Operación 1: Registro Válido de Cliente 1
    try:
        c1 = Cliente(1, "Carlos Pérez", "carlos@mail.com", "3104567890")
        clientes_registrados.append(c1)
        logging.info("Cliente 1 registrado correctamente.")
        print("Op 1 [OK]: Cliente Carlos registrado.")
    except Exception as e:
        print(f"Op 1 [FAIL]: {e}")

    # Operación 2: Registro INVÁLIDO de Cliente (correo malo - dispara excepción)
    try:
        print("Op 2 [TEST]: Intentando registrar cliente con correo inválido...")
        c_malo = Cliente(2, "Ana Gómez", "correosinarroba.com", "3201234567")
        clientes_registrados.append(c_malo)
    except ErrorDatoInvalido as e:
        print(f"Op 2 [CAPTURADO]: Excepción manejada correctamente -> {e}")

    # Operación 3: Registro Válido de Cliente 3
    try:
        c3 = Cliente(3, "María Rodríguez", "maria@mail.com", "3159876543")
        clientes_registrados.append(c3)
        print("Op 3 [OK]: Cliente María registrado.")
    except Exception as e:
        print(f"Op 3 [FAIL]: {e}")

    # Operación 4: Creación de Servicio de Salas Válido
    try:
        s1 = ReservaSalas("SR-01", "Sala Ejecutiva A", 100000, 10)
        servicios_disponibles.append(s1)
        print("Op 4 [OK]: Servicio de Sala creado.")
    except Exception as e:
        print(f"Op 4 [FAIL]: {e}")

    # Operación 5: Creación de Servicio de Alquiler de Equipos Válido
    try:
        s2 = AlquilerEquipos("EQ-02", "Kit Laptops Dev", 250000, 5)
        servicios_disponibles.append(s2)
        print("Op 5 [OK]: Servicio de Equipos creado.")
    except Exception as e:
        print(f"Op 5 [FAIL]: {e}")

    # Operación 6: Creación de Servicio de Asesorías Válido
    try:
        s3 = AsesoriasEspecializadas("AS-03", "Asesoría Arquitectura SW", 300000, "Senior")
        servicios_disponibles.append(s3)
        print("Op 6 [OK]: Servicio de Asesorías creado.")
    except Exception as e:
        print(f"Op 6 [FAIL]: {e}")

    # Operación 7: Reserva Exitosa 1 (Cliente Carlos + Sala Ejecutiva con descuento)
    try:
        print("Op 7 [TEST]: Procesando reserva exitosa 1...")
        reserva1 = Reserva(clientes_registrados[0], servicios_disponibles[0], 3)
        costo_final = servicios_disponibles[0].calcular_costo(descuento_porcentaje=10)
        print(f"Costo calculado con descuento: ${costo_final}")
        reserva1.confirmar_reserva()
        historial_reservas.append(reserva1)
    except Exception as e:
        print(f"Op 7 [FAIL]: {e}")

    # Operación 8: Reserva Exitosa 2 (Cliente María + Alquiler de equipos con horas extra)
    try:
        print("Op 8 [TEST]: Procesando reserva exitosa 2...")
        reserva2 = Reserva(clientes_registrados[1], servicios_disponibles[1], 2)
        costo_final = servicios_disponibles[1].calcular_costo(horas_adicionales=2)
        print(f"Costo calculado con horas extra: ${costo_final}")
        reserva2.confirmar_reserva()
        historial_reservas.append(reserva2)
    except Exception as e:
        print(f"Op 8 [FAIL]: {e}")

    # Operación 9: Reserva FALLIDA por duración inválida (cero o negativo)
    try:
        print("Op 9 [TEST]: Intentando reserva con duración de días inválida...")
        reserva_invalida = Reserva(clientes_registrados[0], servicios_disponibles[2], 0)
        reserva_invalida.confirmar_reserva()
    except Exception as e:
        print(f"Op 9 [CAPTURADO]: {e}")

    # Operación 10: Intento de reserva con un servicio marcado como no disponible
    try:
        print("Op 10 [TEST]: Intentando reservar un servicio no disponible...")
        servicios_disponibles[0].disponible = False # Desactivamos el servicio
        reserva_fallida_servicio = Reserva(clientes_registrados[1], servicios_disponibles[0], 5)
        reserva_fallida_servicio.confirmar_reserva()
    except Exception as e:
        print(f"Op 10 [CAPTURADO]: {e}")

    print("=== FIN DE LA SIMULACIÓN. REVISAR ARCHIVO 'sistema_errores.log' PARA VER LOS REGISTROS ===")
