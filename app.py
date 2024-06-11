from flask import Flask, request, jsonify, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
import matplotlib.pyplot as plt
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
    json_data = request.json

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

@app.post('/graficar')
def graficar():
    json_data = request.json

    data = []
    for item in json_data:
        data.append(item)

    plt.figure(figsize=(10, 6))
    plt.bar(data[0].keys(), data[0].values())
    plt.xlabel('Protocolos')
    plt.ylabel('Quantidade')
    plt.title('Quantidade de pacotes por protocolo')
    plt.xticks(rotation=45)
    plt.savefig('static/bar_chart.png')
    plt.close()

    media = {}
    for key in data[0].keys():
        media[key] = sum(item[key] for item in data) / len(data)

    plt.figure(figsize=(8, 8))
    plt.pie(media.values(), labels=media.keys(), autopct='%1.1f%%')
    plt.title('Média de pacotes por protocolo')
    plt.savefig('static/pie_chart.png')
    plt.close()

    return jsonify({
        'message': 'Gráficos gerados com sucesso',
        'bar_chart': '/static/bar_chart.png',
        'pie_chart': '/static/pie_chart.png'
    })

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
        print(f'{sede} no responde')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(port=5000)
