from flask import Flask, request, jsonify, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
import subprocess
import json

app = Flask(__name__)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "API de Gestão de IPs"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.post('/gestion')
def gestion():
    file = request.files['file']
    json_data = json.load(file)

    ip_arr = json_data
    no_responden = []

    for item in ip_arr:
        ip = item['Ip']
        if ping_ip(ip):
            print(f'Resposta OK de {ip}')
        else:
            no_responden.append(ip)

    notificar(no_responden, json_data)

    return jsonify({'message': 'Processamento concluído'})


def ping_ip(ip):
    try:
        output = subprocess.run(["ping", "-c", "1", "-W", "2", ip], capture_output=True)
        return output.returncode == 0
    except Exception as e:
        print(f'Erro ao pingar {ip}: {e}')
        return False


def notificar(no_responden, json_data):
    for ip in no_responden:
        sede = next(item['Nombre'] for item in json_data if item['Ip'] == ip)
        print(f'Sede {sede} no responde')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(port=5000)
