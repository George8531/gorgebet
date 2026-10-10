import os
import time
import threading
import requests

# --- TUS CREDENCIALES INTEGRADAS ---
TELEGRAM_TOKEN = "8717685244:AAHSMZhIA72ojuClN9q6zyuXTQCXDlRRuys"
CHAT_ID = "5484160028"

# --- CONTROL DE BANCA INICIAL ---
BANKROLL_INICIAL = 500000.0  # Banca inicial (Ej: 500,000 COP)
STAKE_UNIDADES_FIJAS = 2.0   # 2 unidades por apuesta recomendada

def enviar_mensaje_telegram(texto, chat_target=CHAT_ID):
    """
    Envía cualquier mensaje de texto a Telegram.
    """
    url_tg = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_target,
        "text": texto,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url_tg, json=payload)
    except Exception as e:
        print(f"Error enviando mensaje a Telegram: {e}")

def escuchar_comandos():
    """
    Escucha de forma continua los mensajes que le envías al bot en Telegram (como /start).
    """
    offset = 0
    print("Iniciando escuchador de comandos de Telegram...")
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={offset}&timeout=30"
            response = requests.get(url)
            data = response.json()
            
            if data.get("ok"):
                for result in data.get("result", []):
                    offset = result["update_id"] + 1
                    message = result.get("message", {})
                    text = message.get("text", "")
                    chat_id_remitente = str(message.get("chat", {}).get("id", ""))
                    
                    if text.startswith("/start"):
                        respuesta = "✅ *¡Bot activado con éxito!* Ya estoy en marcha y buscando las mejores apuestas basadas en datos estadísticos para ti."
                        enviar_mensaje_telegram(respuesta, chat_target=chat_id_remitente)
        except Exception as e:
            print(f"Error en el escuchador de Telegram: {e}")
            time.sleep(5)

def obtener_partidos_y_cuotas():
    """
    Función de adquisición de partidos y cuotas (Betplay / Betano u otras casas).
    """
    try:
        partidos_simulados = [
            {
                "local": "Independiente Medellín",
                "visitante": "Millonarios",
                "mercado": "Más de 2.5 Goles",
                "cuota_casa": 2.15,
                "probabilidad_modelo": 57.0
            }
        ]
        return partidos_simulados
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return []

def evaluar_y_filtrar_apuestas(partido, bankroll_actual):
    prob_real = partido["probabilidad_modelo"] / 100.0
    cuota_ofrecida = partido["cuota_casa"]
    
    cuota_justa = 1 / prob_real if prob_real > 0 else 99.0
    expected_value = (prob_real * cuota_ofrecida) - 1
    es_value_bet = expected_value > 0.04  
    
    valor_unidad = bankroll_actual * 0.01
    riesgo_dinero = STAKE_UNIDADES_FIJAS * valor_unidad
    
    return {
        "es_apuesta": es_value_bet,
        "cuota_justa": round(cuota_justa, 2),
        "ev_porcentaje": round(expected_value * 100, 2),
        "stake_uds": STAKE_UNIDADES_FIJAS,
        "riesgo": round(riesgo_dinero, 2)
    }

def enviar_alerta_telegram(partido, analisis, banca):
    mensaje = f"""
🚨 **ALERTA DE VALOR DETECTADA** 🚨

⚽ **Partido:** {partido['local']} vs {partido['visitante']}
📊 **Mercado Sugerido:** {partido['mercado']}
🔢 **Cuota Betplay/Betano:** `{partido['cuota_casa']}` *(Justa estimada: `{analisis['cuota_justa']}`)*
📈 **Probabilidad del Modelo:** `{partido['probabilidad_modelo']}%`
💰 **Valor Esperado (EV):** `+{analisis['ev_porcentaje']}%`
🎯 **Stake Recomendado:** `{analisis['stake_uds']} Unidades` ($`{analisis['riesgo']}` COP)
🏦 **Banca Actual Registrada:** $`{banca}`

📝 *Análisis automatizado basado en datos estadísticos y desajuste de líneas.*
    """
    enviar_mensaje_telegram(mensaje, chat_target=CHAT_ID)

def ciclo_analisis():
    """
    Motor principal que analiza partidos y envía alertas automáticas cada cierto tiempo.
    """
    print("Iniciando motor de análisis y control de banca 24/7...")
    banca_actual = BANKROLL_INICIAL
    
    while True:
        print("Escaneando partidos y evaluando cuotas...")
        partidos = obtener_partidos_y_cuotas()
        
        for partido in partidos:
            analisis = evaluar_y_filtrar_apuestas(partido, banca_actual)
            
            if analisis["es_apuesta"]:
                print(f"¡Value Bet encontrada en {partido['local']} vs {partido['visitante']}! Notificando...")
                enviar_alerta_telegram(partido, analisis, banca_actual)
            else:
                print(f"Partido descartado: {partido['local']} vs {partido['visitante']} (Sin margen de valor suficiente).")
                
        time.sleep(10800) # Descansa 3 horas antes del próximo escaneo

if __name__ == "__main__":
    # Usamos hilos (threads) para que el bot escuche el comando /start y analice partidos al mismo tiempo
    hilo_escucha = threading.Thread(target=escuchar_comandos)
    hilo_escucha.start()

    ciclo_analisis()
