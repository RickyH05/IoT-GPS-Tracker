import socket
import json
import mysql.connector
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN DE TU BASE DE DATOS
# ==========================================
DB_HOST = "localhost"
DB_USER = "usuario_gps"     # O "root" si no usaste el usuario nuevo
DB_PASS = "1234"            # <--- ¡PON TU CONTRASEÑA AQUÍ!
DB_NAME = "rastreo_gps"     # La base de datos nueva

# ==========================================
# 2. CONFIGURACIÓN DEL SERVIDOR
# ==========================================
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5050 

def guardar_en_bd_normalizada(device_id_traccar, lat, lon, bat_str):
    """
    Guarda los datos respetando la integridad referencial (3NF).
    1. Verifica si el dispositivo existe en 'cat_dispositivos'.
    2. Si no, lo crea.
    3. Inserta el rastro en 'bitacora_rutas' usando el ID numérico.
    """
    try:
        conexion = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        cursor = conexion.cursor()
        
        # PASO A: Buscar el ID interno del dispositivo (Relación)
        sql_check = "SELECT id_interno FROM cat_dispositivos WHERE serial_traccar = %s"
        cursor.execute(sql_check, (device_id_traccar,))
        resultado = cursor.fetchone()
        
        if resultado:
            # Ya existe, tomamos su ID numérico
            id_interno = resultado[0]
        else:
            # No existe, lo registramos automáticamente (Upsert)
            print(f"🆕 Dispositivo nuevo detectado ({device_id_traccar}). Creando perfil...")
            sql_insert_dev = "INSERT INTO cat_dispositivos (serial_traccar, nombre_asignado) VALUES (%s, 'Dispositivo Nuevo')"
            cursor.execute(sql_insert_dev, (device_id_traccar,))
            conexion.commit()
            id_interno = cursor.lastrowid # Recuperamos el ID recién creado
            
        # PASO B: Preparar datos (Limpieza)
        # Convertir "55%" -> 55 (entero para TINYINT)
        try:
            bat_nivel = int(float(bat_str.replace('%', '')))
        except:
            bat_nivel = 0
        
        # PASO C: Insertar en la tabla de hechos (Bitácora)
        sql_log = """
            INSERT INTO bitacora_rutas (device_id_fk, latitud, longitud, bateria_nivel) 
            VALUES (%s, %s, %s, %s)
        """
        valores = (id_interno, lat, lon, bat_nivel)
        
        cursor.execute(sql_log, valores)
        conexion.commit()
        
        print(f"✅ ¡GUARDADO RELACIONAL! -> ID Interno: {id_interno} | Lat: {lat}")
        
        cursor.close()
        conexion.close()
        
    except mysql.connector.Error as err:
        print(f"❌ Error de MySQL: {err}")
    except Exception as e:
        print(f"❌ Error general al guardar: {e}")

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        servidor.bind((SERVER_HOST, SERVER_PORT))
        servidor.listen(5)
        print("="*50)
        print(f"🚀 SERVIDOR IOT INICIADO (Modo: Normalizado)")
        print(f"📡 Escuchando en puerto: {SERVER_PORT}")
        print("="*50)
        
        while True:
            conn, addr = servidor.accept()
            datos = conn.recv(4096)
            
            if datos:
                texto = datos.decode('utf-8', errors='ignore')
                
                # BUSCAR EL JSON DENTRO DEL MENSAJE HTTP
                inicio_json = texto.find('{')
                if inicio_json != -1:
                    json_str = texto[inicio_json:] 
                    
                    try:
                        data_json = json.loads(json_str)
                        
                        print("\n" + "-"*30)
                        print(f"📦 JSON CRUDO RECIBIDO:\n{json.dumps(data_json)}")
                        print("-" * 30)
                        
                        # Extraemos los datos
                        d_id = data_json.get('device_id', 'Desconocido')
                        coords = data_json.get('location', {}).get('coords', {})
                        bateria_info = data_json.get('location', {}).get('battery', {})
                        
                        lat = coords.get('latitude')
                        lon = coords.get('longitude')
                        
                        # Convertir batería
                        nivel_bat = bateria_info.get('level', 0)
                        bat_str = f"{int(float(nivel_bat) * 100)}%"

                        # Resumen humano
                        print(f"📍 Procesado: ID {d_id} | Pos: {lat}, {lon} | Bat: {bat_str}")

                        # --- REQUISITO 2: GUARDADO EN BD NORMALIZADA ---
                        if lat and lon: 
                            guardar_en_bd_normalizada(d_id, lat, lon, bat_str)
                            
                    except json.JSONDecodeError:
                        print("⚠️ Error leyendo JSON.")
                
                # RESPONDER AL CELULAR (ACK)
                respuesta = "HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n"
                conn.sendall(respuesta.encode('utf-8'))
            
            conn.close()

    except Exception as e:
        print(f"❌ Error fatal del servidor: {e}")

if __name__ == "__main__":
    iniciar_servidor()