from flask import Flask, render_template_string, jsonify
import mysql.connector
import json
import math
from datetime import datetime

app = Flask(__name__)

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'usuario_gps',
    'password': '1234',      
    'database': 'rastreo_gps'
}

# ==========================================
# 2. LÓGICA DE NEGOCIO (BACKEND)
# ==========================================
def obtener_datos_procesados():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vista_monitoreo ORDER BY fecha_reporte DESC LIMIT 2000")
        datos_crudos = cursor.fetchall()
        conn.close()

        datos_filtrados = []
        punto_futuro = None 

        def get_distancia(lat1, lon1, lat2, lon2):
            R = 6371000
            phi1, phi2 = math.radians(lat1), math.radians(lat2)
            dphi = math.radians(lat2 - lat1)
            dlambda = math.radians(lon2 - lon1)
            a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            return R * c

        for fila in datos_crudos:
            lat_actual = fila[2]
            lon_actual = fila[3]
            
            # Gestión de Fechas
            fecha_obj = fila[5]
            if isinstance(fecha_obj, str):
                try:
                    fecha_obj = datetime.strptime(fecha_obj, '%Y-%m-%d %H:%M:%S')
                except:
                    fecha_obj = datetime.now()

            guardar = False
            distancia = 0
            
            if punto_futuro is None:
                guardar = True
            else:
                distancia = get_distancia(punto_futuro['lat'], punto_futuro['lon'], lat_actual, lon_actual)
                if distancia > 10:
                    guardar = True

            if guardar:
                velocidad_kmh = 0
                estado_texto = "Inicio"

                # CÁLCULO DE VELOCIDAD
                if punto_futuro is not None:
                    delta_t = (punto_futuro['obj_fecha'] - fecha_obj).total_seconds()
                    
                    if delta_t > 0:
                        velocidad_ms = distancia / delta_t
                        velocidad_calculada = int(velocidad_ms * 3.6)
                        
                        # FILTRO ANTI-LOCURA (>130km/h es error)
                        if velocidad_calculada > 130:
                            velocidad_kmh = 0 
                            estado_texto = "GPS inestable"
                        else:
                            velocidad_kmh = velocidad_calculada
                            estado_texto = f"{velocidad_kmh} km/h" if velocidad_kmh > 3 else "Detenido"
                        
                        punto_futuro['velocidad'] = velocidad_kmh
                        punto_futuro['estado'] = estado_texto

                bat_raw = str(fila[4]).replace('%', '')

                item = {
                    'lat': lat_actual,
                    'lon': lon_actual,
                    'bateria': bat_raw,
                    'fecha_dia': fecha_obj.strftime('%d/%m/%Y'),
                    'hora': fecha_obj.strftime('%H:%M'),
                    'obj_fecha': fecha_obj, 
                    'velocidad': 0,        
                    'estado': "..."
                }
                datos_filtrados.append(item)
                punto_futuro = item 

        for d in datos_filtrados:
            del d['obj_fecha']

        return datos_filtrados

    except Exception as e:
        print(f"Error Backend: {e}")
        return []

# ==========================================
# 3. INTERFAZ (HTML + JS)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Monitor GPS Libre</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <style>
        body { background: #eef2f6; font-family: 'Segoe UI', sans-serif; }
        #map-card { border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); border: none; }
        #map { height: 650px; width: 100%; }
        .sidebar { height: 650px; border-radius: 16px; background: white; box-shadow: 0 4px 20px rgba(0,0,0,0.08); display: flex; flex-direction: column; }
        .sidebar-header { padding: 20px; border-bottom: 1px solid #eee; background: #fff; border-radius: 16px 16px 0 0; }
        .table-container { flex: 1; overflow-y: auto; }
        .fecha-separador { background: #f1f5f9; color: #64748b; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; }
        .badge-speed { width: 90px; font-weight: 500; }
        
        /* Botón flotante para recentrar */
        .btn-recentrar {
            position: absolute; bottom: 20px; right: 20px; z-index: 1000;
            background: white; border: 2px solid #3b82f6; color: #3b82f6;
            padding: 8px 15px; border-radius: 50px; font-weight: bold;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); cursor: pointer;
            transition: all 0.3s;
        }
        .btn-recentrar:hover { background: #3b82f6; color: white; }
    </style>
</head>
<body>

<div class="container-fluid p-4">
    <div class="row g-4">
        <div class="col-lg-8 position-relative">
            <div class="card" id="map-card">
                <div id="map"></div>
                <button class="btn-recentrar" onclick="centrarEnCoche()">
                    <i class="fas fa-crosshairs"></i> Ubicar Coche
                </button>
                <div class="card-footer bg-white d-flex justify-content-between align-items-center py-2">
                    <small class="text-muted"><i class="fas fa-hand-paper"></i> Modo exploración libre activado</small>
                    <span class="badge bg-success bg-opacity-10 text-success border border-success px-3">ONLINE</span>
                </div>
            </div>
        </div>

        <div class="col-lg-4">
            <div class="sidebar">
                <div class="sidebar-header">
                    <h5 class="m-0 fw-bold text-dark">Historial de Ruta</h5>
                </div>
                <div class="table-container">
                    <table class="table table-borderless mb-0 align-middle" id="tabla-gps">
                        <thead class="sticky-top bg-white border-bottom">
                            <tr class="text-muted small text-uppercase">
                                <th class="ps-4">Hora</th>
                                <th>Estado</th>
                                <th>Bat</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
    var map = L.map('map').setView([25.6866, -100.3161], 14);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', { attribution: '©OpenStreetMap' }).addTo(map);

    var layerGroup = L.layerGroup().addTo(map);
    var pathGroup = L.layerGroup().addTo(map);
    
    var iconCar = L.icon({
        iconUrl: 'https://cdn-icons-png.flaticon.com/512/3097/3097144.png',
        iconSize: [42, 42], iconAnchor: [21, 21], popupAnchor: [0, -10]
    });

    // Variable para controlar si es la primera carga
    var primeraCarga = true;
    var ultimaPosicion = null; // Guardamos la coord del coche para el botón

    function centrarEnCoche() {
        if(ultimaPosicion) {
            map.flyTo(ultimaPosicion, 16);
        }
    }

    function refreshData() {
        fetch('/api/data')
            .then(res => res.json())
            .then(data => {
                if(!data.length) return;

                layerGroup.clearLayers();
                pathGroup.clearLayers();
                
                let tbody = document.getElementById('tabla-gps').querySelector('tbody');
                tbody.innerHTML = '';

                let coords = [];
                let orderedData = [...data].reverse(); 

                orderedData.forEach((pt, i) => {
                    coords.push([pt.lat, pt.lon]);
                    
                    if (i === orderedData.length - 1) {
                        // Guardamos la última posición por si pulsas el botón
                        ultimaPosicion = [pt.lat, pt.lon];

                        L.marker([pt.lat, pt.lon], {icon: iconCar}).addTo(layerGroup)
                            .bindPopup(`<b>🚗 ACTUAL</b><br>${pt.estado}`).openPopup();
                        
                        // --- AQUÍ ESTÁ EL CAMBIO ---
                        // Solo centramos automáticamente LA PRIMERA VEZ
                        if (primeraCarga) {
                            map.setView([pt.lat, pt.lon], 16);
                            primeraCarga = false; // Ya no lo volvemos a hacer
                        }
                        // ---------------------------
                    } else {
                        L.circleMarker([pt.lat, pt.lon], {
                            radius: 4, color: '#3b82f6', fillColor: 'white', weight: 2, fillOpacity: 1
                        }).addTo(layerGroup);
                    }
                });

                if(coords.length > 1) {
                    L.polyline(coords, {color: '#3b82f6', weight: 5, opacity: 0.7, lineJoin:'round'}).addTo(pathGroup);
                }

                // Tabla
                let lastDate = '';
                let lastMinute = '';

                data.forEach(pt => {
                    if (pt.fecha_dia !== lastDate) {
                        tbody.innerHTML += `<tr class="fecha-separador text-center"><td colspan="3">${pt.fecha_dia}</td></tr>`;
                        lastDate = pt.fecha_dia;
                        lastMinute = ''; 
                    }

                    if (pt.hora !== lastMinute) {
                        let badgeClass = 'bg-secondary';
                        let badgeIcon = 'fa-parking';
                        
                        if(pt.estado.includes('km/h')) {
                            badgeClass = 'bg-primary';
                            badgeIcon = 'fa-tachometer-alt';
                        }
                        else if(pt.estado.includes('GPS')) {
                            badgeClass = 'bg-warning text-dark';
                            badgeIcon = 'fa-exclamation-triangle';
                        }

                        let row = `
                            <tr>
                                <td class="ps-4 fw-bold text-dark">${pt.hora}</td>
                                <td>
                                    <span class="badge ${badgeClass} badge-speed py-2">
                                        <i class="fas ${badgeIcon} me-1"></i> ${pt.estado}
                                    </span>
                                </td>
                                <td><small class="text-muted">${pt.bateria}%</small></td>
                            </tr>
                        `;
                        tbody.innerHTML += row;
                        lastMinute = pt.hora;
                    }
                });
            });
    }

    refreshData();
    setInterval(refreshData, 3000);
</script>
</body>
</html>
"""

# ==========================================
# 4. RUTAS
# ==========================================
@app.route('/')
def home(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/data')
def api(): return jsonify(obtener_datos_procesados())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)