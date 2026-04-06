import urllib.parse
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

# Exemplo de banco de dados em memória. 
# Totaliza cerca de 70 convidados agrupados por família/grupos.
CONVIDADOS = {
    "123e4567-e89b-12d3-a456-426614174001": {"familia": "Família Silva", "nomes": ["Carlos Silva", "Ana Silva", "Lucas Silva", "Mariana Silva"]},
    "123e4567-e89b-12d3-a456-426614174002": {"familia": "Família Costa", "nomes": ["Roberto Costa", "Juliana Costa", "Bebê Pedro"]},
    "123e4567-e89b-12d3-a456-426614174003": {"familia": "Família Oliveira", "nomes": ["Fernando Oliveira", "Cláudia Oliveira", "Tiago", "Beatriz", "Sofia"]},
    "123e4567-e89b-12d3-a456-426614174004": {"familia": "Família Souza", "nomes": ["Marcos Souza", "Helena Souza"]},
    "123e4567-e89b-12d3-a456-426614174005": {"familia": "Família Santos", "nomes": ["João Santos", "Maria Santos", "Felipe", "Camila", "Rafael", "Larissa"]},
    "123e4567-e89b-12d3-a456-426614174006": {"familia": "Família Pereira", "nomes": ["Antônio Pereira", "Lúcia Pereira", "Bruno"]},
    "123e4567-e89b-12d3-a456-426614174007": {"familia": "Família Rodrigues", "nomes": ["José Rodrigues", "Marta Rodrigues", "Ricardo", "Paulo"]},
    "123e4567-e89b-12d3-a456-426614174008": {"familia": "Família Almeida", "nomes": ["Pedro Almeida", "Teresa Almeida"]},
    "123e4567-e89b-12d3-a456-426614174009": {"familia": "Família Lima", "nomes": ["Luiz Lima", "Sandra Lima", "Igor", "Vanessa", "Diego"]},
    "123e4567-e89b-12d3-a456-426614174010": {"familia": "Família Gomes", "nomes": ["Marcelo Gomes", "Patrícia Gomes", "Amanda"]},
    "123e4567-e89b-12d3-a456-426614174011": {"familia": "Família Martins", "nomes": ["Eduardo Martins", "Camila Martins", "Thiago", "Letícia"]},
    "123e4567-e89b-12d3-a456-426614174012": {"familia": "Amigos da Faculdade", "nomes": ["Rafael", "Gabriel", "Vítor", "Henrique", "Renato", "Gustavo"]},
    "123e4567-e89b-12d3-a456-426614174013": {"familia": "Amigas da Noiva", "nomes": ["Laura", "Isabela", "Juliana", "Carol", "Fernanda"]},
    "123e4567-e89b-12d3-a456-426614174014": {"familia": "Família Carvalho", "nomes": ["Sérgio Carvalho", "Mônica Carvalho", "André"]},
    "123e4567-e89b-12d3-a456-426614174015": {"familia": "Família Mendes", "nomes": ["Rodrigo Mendes", "Tatiana Mendes", "Gustavo", "Carolina", "Alice", "Miguel"]},
    "123e4567-e89b-12d3-a456-426614174016": {"familia": "Primos", "nomes": ["Leandro", "Matheus", "Jéssica", "Bianca", "Thiago"]},
}

@app.route('/')
def landing_default():
    """Página mostrada se nenhum UUID for passado"""
    return render_template('landing.html', dados=None)

@app.route('/<token>')
def landing_personalizada(token):
    """Landing page com os nomes da família e botão para o convite"""
    dados = CONVIDADOS.get(token)
    if not dados:
        return redirect(url_for('landing_default'))
    return render_template('landing.html', dados=dados, token=token)

@app.route('/convite/<token>')
def convite(token):
    """Página do convite real com os 4 botões de navegação"""
    dados = CONVIDADOS.get(token)
    if not dados:
        return redirect(url_for('landing_default'))
    return render_template('convite.html', token=token, dados=dados)

@app.route('/confirmar/<token>')
def confirmar(token):
    """Gera o link dinâmico do WhatsApp e redireciona"""
    dados = CONVIDADOS.get(token)
    if not dados:
        return redirect(url_for('landing_default'))
    
    nomes = ", ".join(dados["nomes"])
    numero_whatsapp = "5561999999999" # DDD 61
    
    # Monta uma mensagem customizada com a lista de nomes atrelada àquele UUID
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
    evento = {
        "titulo": "Cerimônia",
        "descricao": "Nossa cerimônia religiosa será realizada na Igreja Matriz, às 19h00.",
        "maps_link": "https://maps.app.goo.gl/seu_link_aqui"
    }
    return render_template('evento.html', evento=evento, token=token)

@app.route('/recepcao/<token>')
def recepcao(token):
    evento = {
        "titulo": "Recepção",
        "descricao": "Após a cerimônia, esperamos você no Salão de Festas XYZ para comemorarmos juntos!",
        "maps_link": "https://maps.app.goo.gl/seu_link_aqui"
    }
    return render_template('evento.html', evento=evento, token=token)

if __name__ == '__main__':
    app.run(debug=True)