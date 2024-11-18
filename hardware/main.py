import network
import time
from machine import Pin, PWM
import umqtt.simple as mqtt

import urequests

# URL para a requisição GET
url = "URL_SSEND_MAIL"  # Exemplo de URL

# Função para enviar a requisição HTTP GET
def http_get_request():
    try:
        # Enviar a requisição
        response = urequests.get(url)
        
        # Exibir a resposta
        print("Status Code:", response.status_code)
        print("Resposta:", response.text)
        
        # Fechar a resposta
        response.close()
    except Exception as e:
        print("Erro ao fazer a requisição HTTP:", e)




# Configuração Wi-Fi
SSID = 'GRANDES EVENTOS'
PASSWORD = '@GRANDESEVENTOS2023'

# Configuração MQTT
MQTT_BROKER = 'a22wgjycrazooz-ats.iot.us-east-2.amazonaws.com'
MQTT_PORT = 8883
CLIENT_ID = 'BBoxESP32'
TOPIC_COMMAND = 'bbox/command'
TOPIC_STATUS = 'bbox/status'



# Caminhos dos arquivos de certificado e chave
KEY_FILE = "cert/bbox.private.key"
CERT_FILE = "cert/bbox.cert.pem"

# Configuração dos pinos dos LEDs
LED_CAIXA_FECHADA = Pin(2, Pin.OUT)
LED_CAIXA_ABERTA = Pin(4, Pin.OUT)
LED_PROCESSANDO = Pin(5, Pin.OUT)

# Configuração do servo motor
servo_pin = PWM(Pin(18), freq=50)  # Frequência de 50Hz para o servo

# Variáveis de controle
open_close_counter = 0  # Contador para abrir/fechar ciclos

# Função para definir o ângulo do servo
def set_servo_angle(angle):
    duty = int((angle / 180) * 102) + 26
    servo_pin.duty(duty)


set_servo_angle(90)  # Fechar a caixa   

# Função de conexão Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print("Conectando ao Wi-Fi...")
        time.sleep(1)
    print("Conectado ao Wi-Fi", wlan.ifconfig())

# Função de callback para lidar com mensagens MQTT
def message_callback(topic, msg):
    global LED_CAIXA_FECHADA, LED_CAIXA_ABERTA, LED_PROCESSANDO, open_close_counter
    print("Mensagem recebida:", msg)
    if msg == b'abrir':
        LED_CAIXA_FECHADA.off()
        LED_CAIXA_ABERTA.on()
        set_servo_angle(0)  # Abrir a caixa
    elif msg == b'fechar':
        LED_CAIXA_FECHADA.on()
        LED_CAIXA_ABERTA.off()
        set_servo_angle(90)  # Fechar a caixa
        # Incrementar o contador de abrir/fechar
        open_close_counter += 1
        print(f"Ciclo de abrir/fechar: {open_close_counter}")
        # Enviar e-mail após 3 ciclos de abrir/fechar
        if open_close_counter >= 1:
            http_get_request()
            open_close_counter = 0  # Resetar o contador
    elif msg == b'processando':
        LED_PROCESSANDO.on()
    elif msg == b'fim':
        LED_PROCESSANDO.off()

# Função para configurar MQTT com os certificados
def load_certificates():
    with open(KEY_FILE, "r") as f:
        key = f.read()
    with open(CERT_FILE, "r") as f:
        cert = f.read()
    return key, cert

# Conexão MQTT
def connect_mqtt():
    key, cert = load_certificates()
    client = mqtt.MQTTClient(
        client_id=CLIENT_ID,
        server=MQTT_BROKER,
        port=MQTT_PORT,
        keepalive=4000,
        ssl=True,
        ssl_params={
            "key": key,
            "cert": cert,
            "server_side": False
        }
    )
    client.set_callback(message_callback)
    client.connect()
    client.subscribe(TOPIC_COMMAND)
    print("Conectado ao MQTT e inscrito no tópico")
    return client

# Loop principal
try:
    connect_wifi()
    client = connect_mqtt()
    while True:
        client.check_msg()  # Verifica se há mensagens
        time.sleep(1)

except Exception as e:
    print("Erro:", e)
finally:
    client.disconnect()