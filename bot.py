import os
import time
import requests

# --- TUS CREDENCIALES INTEGRADAS ---
TELEGRAM_TOKEN = "8717685244:AAHSMZhIA72ojuClN9q6zyuXTQCXDlRRuys"
CHAT_ID = "5484160028"

# --- CONTROL DE BANCA INICIAL ---
BANKROLL_INICIAL = 500000.0  # Banca inicial (Ej: 500,000 COP)
STAKE_UNIDADES_FIJAS = 2.0   # 2 unidades por apuesta recomendada

def obtener_partidos_y_cuotas():
    """
    Función de adquisición de partidos y cuotas (Betplay / Betano u otras casas).
    Puedes conectar aquí tu API deportiva o de cuotas favorita.
    """
    try:
        # Estructura simulada de alta precisión para análisis estadístico y de cuotas:
        partidos_simulados = [
            {
                "local": "Independiente Medellín",
                "visitante": "Millonarios",
                "mercado": "Más de 2.5 Goles",
                "cuota_casa": 2.15,          # Cuota ofrecida por la casa
                "probabilidad_modelo": 57.0  # Porcentaje real determinado por tus estadísticas
            }
        ]
        return partidos_simulados
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return []

def evaluar_y_filtrar_apuestas(partido, bankroll_actual):
    """
    Motor matemático: Calcula el Expected Value (EV) y define si hay error de cuota.
    """
    prob_real = partido["probabilidad_modelo"] / 100.0
    cuota_ofrecida = partido["cuota_casa"]
    
    # Cuota justa matemática limpia
    cuota_justa = 1 / prob_real if prob_real > 0 else 99.0
    
    # Expected Value (EV > 0.04 significa valor positivo superior al 4%)
    expected_value = (prob_real * cuota_ofrecida) - 1
    es_value_bet = expected_value > 0.04  
    
    # Control de Banca y Riesgo Monetario
    valor_unidad = bankroll_actual * 0.01  # 1 unidad equivale al 1% de la banca actual
    riesgo_dinero = STAKE_UNIDADES_FIJAS * valor_unidad
    
    return {
        "es_apuesta": es_value_bet,
        "cuota_justa": round(cuota_justa, 2),
        "ev_porcentaje": round(expected_value * 100, 2),
        "stake_uds": STAKE_UNIDADES_FIJAS,
        "riesgo": round(riesgo_dinero, 2)
    }

def enviar_alerta_telegram(partido, analisis, banca):
    """
    Envía la alerta estructurada directamente a tu chat personal de Telegram.
    """
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
    
    url_tg = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url_tg, json=payload)
        if response.status_code == 200:
            print("Alerta enviada con éxito a Telegram.")
        else:
            print(f"Error al enviar a Telegram: {response.text}")
    except Exception as e:
        print(f"Excepción de red enviando a Telegram: {e}")

def ciclo_principal():
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
                
        # El bot descansa 3 horas (10800 segundos) antes de volver a escanear para optimizar uso de APIs
        time.sleep(10800) 

if __name__ == "__main__":
    ciclo_principal()
