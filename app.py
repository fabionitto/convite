import os
import json
import urllib.parse
import requests
import logging # 1. Importe a biblioteca nativa
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

# Configuração dos caminhos absolutos locais
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONVIDADOS_PATH = os.path.join(BASE_DIR, 'dados_convidados.json')
EVENTOS_PATH = os.path.join(BASE_DIR, 'dados_eventos.json')

# Configuração das URLs remotas (via Variáveis de Ambiente)
# Se a variável não estiver definida no sistema, ele retorna None
VERCEL_URL_CONVIDADOS = os.environ.get("VERCEL_URL_CONVIDADOS")
VERCEL_URL_EVENTOS = os.environ.get("VERCEL_URL_EVENTOS")

# Captura o token de segurança das variáveis de ambiente
VERCEL_BLOB_TOKEN = os.environ.get("BLOB_READ_WRITE_TOKEN")

def obter_dados(caminho_local, url_remota=None):
    if url_remota:
        try:
            # Prepara o cabeçalho de autorização (O Crachá)
            headers = {}
            if VERCEL_BLOB_TOKEN:
                headers['Authorization'] = f'Bearer {VERCEL_BLOB_TOKEN}'

            # Faz a requisição enviando o token
            resposta = requests.get(url_remota, headers=headers, timeout=5)
            resposta.raise_for_status() 
            
            logging.warning(f"✅ Dados carregados com sucesso do Vercel: {url_remota}")
            return resposta.json()
            
        except requests.RequestException as e:
            logging.warning(f"⚠️ Falha ao buscar no Vercel ({url_remota}): {e}")
            logging.warning("🔄 Fazendo fallback para o arquivo local...")

    # Rotina de Fallback para o arquivo local
    try:
        with open(caminho_local, 'r', encoding='utf-8') as f:
            logging.warning(f"Dados carregados do arquivo local: {caminho_local}")
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"❌ Erro: Arquivo local '{caminho_local}' não encontrado.")
        return {}
    except json.JSONDecodeError:
        logging.warning(f"❌ Erro: Arquivo local '{caminho_local}' possui JSON inválido.")
        return {}

# Carrega os dados na memória (executado ao iniciar o servidor Flask)
CONVIDADOS = obter_dados(CONVIDADOS_PATH, VERCEL_URL_CONVIDADOS)
EVENTOS = obter_dados(EVENTOS_PATH, VERCEL_URL_EVENTOS)


@app.route('/')
def landing_default():
    return render_template('landing.html', dados=None)


@app.route('/<token>')
def landing_personalizada(token):
    dados = CONVIDADOS.get(token)
    if not dados:
        return redirect(url_for('landing_default'))
    return render_template('landing.html', dados=dados, token=token)


@app.route('/convite/<token>')
def convite(token):
    dados = CONVIDADOS.get(token)
    if not dados:
        return redirect(url_for('landing_default'))
    return render_template('convite.html', token=token, dados=dados)


@app.route('/confirmar/<token>')
def confirmar(token):
    dados = CONVIDADOS.get(token)
    if not dados:
        return redirect(url_for('landing_default'))
    
    nomes = ", ".join(dados["nomes"])
    numero_whatsapp = "5561999999999" # Insira seu número
    
    texto_base = f"Olá! Gostaria de confirmar a presença do nosso grupo no casamento:\n\n{nomes}."
    mensagem_encoded = urllib.parse.quote(texto_base)
    
    whatsapp_link = f"https://wa.me/{numero_whatsapp}?text={mensagem_encoded}"
    return redirect(whatsapp_link)


@app.route('/presentes/<token>')
def presentes(token):
    pix_code = "00020126580014br.gov.bcb.pix0136sua-chave-pix-aqui..."
    return render_template('presentes.html', pix_code=pix_code, token=token)


@app.route('/cerimonia/<token>')
def cerimonia(token):
    evento = EVENTOS.get("cerimonia", {})
    return render_template('evento.html', evento=evento, token=token)


@app.route('/recepcao/<token>')
def recepcao(token):
    evento = EVENTOS.get("recepcao", {})
    return render_template('evento.html', evento=evento, token=token)


if __name__ == '__main__':
    app.run(debug=True)