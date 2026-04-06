import os
from flask import Flask, request, render_template_string
from libsql_client import create_client_sync

app = Flask(__name__)

# Configuração do Turso usando Variáveis de Ambiente
TURSO_URL = os.environ.get("TURSO_DATABASE_URL")
TURSO_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")

# Template HTML minimalista (Mantido igual ao anterior)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RSVP Casamento</title>
    <style>
        body { font-family: sans-serif; text-align: center; margin-top: 50px; background-color: #fafafa; }
        .card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: inline-block; max-width: 400px; width: 90%; }
        .btn { padding: 12px 24px; margin: 10px; border: none; cursor: pointer; border-radius: 5px; font-weight: bold; width: 80%; transition: 0.2s; }
        .btn-yes { background-color: #2e7d32; color: white; }
        .btn-yes:hover { background-color: #1b5e20; }
        .btn-no { background-color: #c62828; color: white; }
        .btn-no:hover { background-color: #b71c1c; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Olá, {{ nome }}!</h2>
        <p>Estamos muito felizes em convidar você para o nosso casamento.</p>
        <p>Este convite é exclusivo para <strong>{{ vagas }} pessoa(s)</strong>.</p>
        
        <form method="POST">
            <button class="btn btn-yes" type="submit" name="status" value="confirmado">Confirmar Presença</button>
            <button class="btn btn-no" type="submit" name="status" value="recusado">Não Poderei Ir</button>
        </form>
    </div>
</body>
</html>
"""

def get_db_client():
    """Cria a conexão com o banco Turso"""
    return create_client_sync(url=TURSO_URL, auth_token=TURSO_TOKEN)

@app.route('/rsvp/<token>', methods=['GET', 'POST'])
def rsvp(token):
    # Conecta ao banco de dados
    client = get_db_client()
    
    # Busca o convidado pelo token
    resultado = client.execute("SELECT nome, vagas, status FROM convidados WHERE token = ?", [token])
    
    # Se a query não retornar linhas, o token não existe
    if not resultado.rows:
        return "<h3>Convite inválido ou não encontrado.</h3>", 404

    # Extrai os dados do convidado retornado
    linha = resultado.rows[0]
    nome_convidado = linha[0]
    vagas_convidado = linha[1]
    
    if request.method == 'POST':
        novo_status = request.form.get('status')
        
        # Atualiza o status no banco de dados
        client.execute(
            "UPDATE convidados SET status = ? WHERE token = ?", 
            [novo_status, token]
        )
        
        mensagem = "Presença confirmada! Te esperamos lá." if novo_status == "confirmado" else "Que pena! Sentiremos sua falta."
        return f"<h3>Obrigado! {mensagem}</h3>"

    # GET: Renderiza o formulário com os dados do banco
    return render_template_string(HTML_TEMPLATE, nome=nome_convidado, vagas=vagas_convidado)

if __name__ == '__main__':
    app.run(debug=True)