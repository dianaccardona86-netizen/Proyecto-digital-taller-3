from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# [LÍNEA IMPORTADA] Almacén de datos global
# Aquí se guarda lo que Thonny (la ESP32) nos manda
current_data = {
    "temp": 0, "ref": 0, "luz": 0,
    "sistema": "Desconectado", "servo": "Cerrado", "led": "Ninguno"
}

@app.route('/')
def index():
    # Muestra la página web (index.html debe estar en carpeta /templates)
    return render_template('index.html')
# este metodo es el que recibe los datos de la ESP32
@app.route('/update', methods=['POST'])
def update():
    global current_data
    # Recibe la información que manda la ESP32 desde Thonny
    current_data = request.json 
    return "OK", 200

@app.route('/api/data')
def get_data():
    # Esta línea la usa el JavaScript de la web para actualizarse sola
    return jsonify(current_data)

if __name__ == '__main__':
    # Ponemos host='0.0.0.0' para que Thonny pueda encontrar este servidor
    print("Servidor iniciado. Revisa tu IP con 'ipconfig' para ponerla en Thonny.")
    app.run(host='0.0.0.0', port=5000)