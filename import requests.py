import requests

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"  # tu URL

def enviar_alerta_slack(mensaje: str):
    payload = {
        "text": mensaje  # Puedes usar también "blocks" para formato avanzado
    }
    r = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if r.status_code != 200:
        print("Error al enviar a Slack:", r.status_code, r.text)

# Uso
enviar_alerta_slack("🚨 Alerta crítica: servicio X falló a las 12:34")
