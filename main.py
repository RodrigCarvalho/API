from flask import Flask, jsonify, request, render_template_string
import json

app = Flask(__name__)

def carregar_dados():
    try:
        with open('db.json', 'r') as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        return {"erro": "Arquivo não encontrado"}
    except json.JSONDecodeError:
        return {"erro": "Erro ao decodificar o arquivo JSON"}

@app.route('/', methods=['GET'])
def formulario():
    html_form = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Buscar Dados por Data e Sinal</title>
        <script>
            async function buscarDados(event) {
                event.preventDefault();
                const dataInicial = document.getElementById('dataInicial').value;
                const sinal = document.getElementById('sinal').value;
                const operador = document.getElementById('operador').value;
                let url = `/dados?dataInicial=${dataInicial}`;
                if (sinal) {
                    url += `&sinal=${sinal}&operador=${operador}`;
                }
                const response = await fetch(url);
                const result = await response.json();
                const resultadoDiv = document.getElementById('resultado');
                resultadoDiv.innerHTML = '';
                if (result.erro) {
                    resultadoDiv.innerHTML = `<p>${result.erro}</p>`;
                } else {
                    result.forEach(dado => {
                        resultadoDiv.innerHTML += `<p>Dispositivo: ${dado.dispositivo}, ID: ${dado.id}, Localização: ${dado.localizacao}, Sinal: ${dado.sinal}, Tempo: ${dado.tempo}</p>`;
                    });
                }
            }
        </script>
    </head>
    <body>
        <h1>Buscar Dados por Data e Sinal</h1>
        <form onsubmit="buscarDados(event)">
            <label for="dataInicial">Data Inicial:</label>
            <input type="date" id="dataInicial" name="dataInicial" required>
            <label for="sinal">Sinal:</label>
            <input type="number" id="sinal" name="sinal">
            <label for="operador">Operador:</label>
            <select id="operador" name="operador">
                <option value="=">=</option>
                <option value=">">></option>
                <option value="<"><</option>
                <option value=">=">>=</option>
                <option value="<="><=</option>
            </select>
            <input type="submit" value="Buscar">
        </form>
        <div id="resultado"></div>
    </body>
    </html>
    '''
    return render_template_string(html_form)

@app.route('/dados', methods=['GET'])
def obter_dados():
    dados = carregar_dados()
    if "erro" in dados:
        return jsonify(dados), 404

    data_inicial = request.args.get('dataInicial')
    sinal_fornecido = request.args.get('sinal')
    operador = request.args.get('operador')

    if data_inicial:
        dados_filtrados = [dado for dado in dados if dado.get('tempo').split('T')[0] == data_inicial]

        if sinal_fornecido:
            try:
                sinal_fornecido = int(sinal_fornecido)
            except ValueError:
                return jsonify({"erro": "O sinal deve ser um número inteiro"}), 400

            operadores = {
                "=": lambda x, y: x == y,
                ">": lambda x, y: x > y,
                "<": lambda x, y: x < y,
                ">=": lambda x, y: x >= y,
                "<=": lambda x, y: x <= y
            }

            if operador not in operadores:
                return jsonify({"erro": "Operador inválido"}), 400

            dados_filtrados = [dado for dado in dados_filtrados if operadores[operador](dado.get('sinal'), sinal_fornecido)]

        if not dados_filtrados:
            return jsonify({"erro": "Nenhum dado encontrado para os critérios fornecidos"}), 404

        return jsonify(dados_filtrados)

    return jsonify({"erro": "A data inicial é obrigatória"}), 400

if __name__ == '__main__':
    app.run(debug=True)
