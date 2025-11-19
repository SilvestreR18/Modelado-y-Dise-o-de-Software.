import os
import sys
from services.juego_service import JuegoService
from models.usuario import Usuario, EstadoCuenta
from models.maquina import MaquinaTragamonedas, EstadoMaquina
from services.json_service import JSONService

class CasinoApp:
    def __init__(self):
        self.juego_service = JuegoService()
        self.usuario_actual = None
    
    def limpiar_pantalla(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def mostrar_menu_principal(self):
        print("🎰 CASINO VASIJA DORADA 🎰")
        print("1. Iniciar Sesión")
        print("2. Registrarse")
        print("3. Jugar como Invitado")
        print("4. Salir")
    
    def mostrar_menu_juego(self):
        print(f"\n🎰 BIENVENIDO {self.usuario_actual.nombre.upper()} 🎰")
        print(f"Saldo: ${self.usuario_actual.saldo}")
        print("1. Jugar en Máquina Vasija Dorada")
        print("2. Ver máquinas disponibles")
        print("3. Recargar saldo")
        print("4. Cerrar sesión")
    
    def iniciar_sesion(self):
        email = input("Email: ")
        contraseña = input("Contraseña: ")
        
        usuario = self.juego_service.encontrar_usuario_por_email(email)
        
        if usuario and usuario.contraseña == contraseña and usuario.estado == EstadoCuenta.ACTIVA:
            self.usuario_actual = usuario
            print(f"¡Bienvenido {usuario.nombre}!")
            return True
        else:
            print("Credenciales incorrectas o cuenta inactiva")
            return False
    
    def registrar_usuario(self):
        print("\n--- REGISTRO ---")
        nombre = input("Nombre: ")
        email = input("Email: ")
        contraseña = input("Contraseña: ")
        
        # Verificar si email ya existe
        if self.juego_service.encontrar_usuario_por_email(email):
            print("Este email ya está registrado")
            return
        
        from models.usuario import Usuario
        import uuid
        
        nuevo_usuario = Usuario(
            id=str(uuid.uuid4()),
            nombre=nombre,
            email=email,
            contraseña=contraseña,
            estado=EstadoCuenta.ACTIVA,
            saldo=100.0,  # Saldo inicial
            roles=["jugador"]
        )
        
        self.juego_service.usuarios.append(nuevo_usuario)
        self.juego_service.guardar_usuarios()
        print("¡Registro exitoso! Saldo inicial: $100")
    
    def jugar_como_invitado(self):
        from models.usuario import Usuario
        import uuid
        
        self.usuario_actual = Usuario(
            id=str(uuid.uuid4()),
            nombre="Invitado",
            email="invitado@casino.com",
            contraseña="",
            estado=EstadoCuenta.ACTIVA,
            saldo=50.0,
            roles=["invitado"]
        )
        print("Modo invitado - Saldo: $50")
    
    def mostrar_maquinas(self):
        print("\n--- MÁQUINAS DISPONIBLES ---")
        for i, maquina in enumerate(self.juego_service.maquinas, 1):
            estado = "" if maquina.estado == EstadoMaquina.ACTIVA else ""
            print(f"{i}. {maquina.nombre} - ${maquina.denominacion} {estado}")
            print(f"   Vasija: {maquina.vasija.nivel_actual}/{maquina.vasija.capacidad_maxima}")
    
    def jugar_en_maquina(self):
        self.mostrar_maquinas()
        
        try:
            opcion = int(input("\nSelecciona máquina (número): ")) - 1
            if 0 <= opcion < len(self.juego_service.maquinas):
                maquina = self.juego_service.maquinas[opcion]
                
                if maquina.estado != EstadoMaquina.ACTIVA:
                    print("Esta máquina no está disponible")
                    return
                
                resultado = self.juego_service.jugar_en_maquina(
                    self.usuario_actual.email, 
                    maquina.id
                )
                
                print(f"\n🎲 RESULTADO: {resultado['mensaje']}")
                if 'premio_bonus' in resultado:
                    print(f"🎰 PREMIO: ${resultado['premio_bonus']}")
                print(f"🎰 Saldo actual: ${self.usuario_actual.saldo}")
                
            else:
                print("Opción inválida")
        except ValueError:
            print("Por favor ingresa un número válido")
    
    def recargar_saldo(self):
        try:
            monto = float(input("Monto a recargar: $"))
            self.usuario_actual.acreditar_saldo(monto)
            self.juego_service.guardar_usuarios()
            print(f"¡Saldo recargado! Total: ${self.usuario_actual.saldo}")
        except ValueError:
            print("Monto inválido")
    
    def inicializar_datos(self):
        # Crear datos iniciales si no existen
        if not self.juego_service.usuarios:
            import uuid
            usuario_admin = Usuario(
                id=str(uuid.uuid4()),
                nombre="Admin",
                email="admin@casino.com",
                contraseña="admin123",
                estado=EstadoCuenta.ACTIVA,
                saldo=1000.0,
                roles=["admin", "jugador"]
            )
            self.juego_service.usuarios.append(usuario_admin)
            self.juego_service.guardar_usuarios()
        
        if not self.juego_service.maquinas:
            maquina_vasija = MaquinaTragamonedas(
                id=str(uuid.uuid4()),
                nombre="Vasija Dorada",
                denominacion=5.0,
                estado=EstadoMaquina.ACTIVA
            )
            self.juego_service.maquinas.append(maquina_vasija)
            self.juego_service.guardar_maquinas()
    
    def ejecutar(self):
        self.limpiar_pantalla()
        self.inicializar_datos()
        
        while True:
            if not self.usuario_actual:
                self.mostrar_menu_principal()
                opcion = input("Selecciona opción: ")
                
                if opcion == "1":
                    if self.iniciar_sesion():
                        self.limpiar_pantalla()
                elif opcion == "2":
                    self.registrar_usuario()
                elif opcion == "3":
                    self.jugar_como_invitado()
                    self.limpiar_pantalla()
                elif opcion == "4":
                    print("¡Gracias por visitar el Casino Vasija Dorada!")
                    break
                else:
                    print("Opción inválida")
            else:
                self.mostrar_menu_juego()
                opcion = input("Selecciona opción: ")
                
                if opcion == "1":
                    self.jugar_en_maquina()
                elif opcion == "2":
                    self.mostrar_maquinas()
                elif opcion == "3":
                    self.recargar_saldo()
                elif opcion == "4":
                    self.usuario_actual = None
                    self.limpiar_pantalla()
                else:
                    print("Opción inválida")

if __name__ == "__main__":
    app = CasinoApp()
    app.ejecutar()