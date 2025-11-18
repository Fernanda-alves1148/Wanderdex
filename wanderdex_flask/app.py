from flask import Flask, render_template, request

app = Flask(__name__, static_folder='static', template_folder='templates')

# --------- Dados Dinâmicos ---------
# Exemplo de cidades e atrações
cidades = [
    {
        'id': 1,
        'nome': 'Paris',
        'subtitulo': 'Cidade da Luz',
        'descricao': 'Paris é a capital da França, famosa por seus monumentos e cultura.',
        'atracoes': [
            {'id': 1, 'nome': 'Torre Eiffel'},
            {'id': 2, 'nome': 'Museu do Louvre'},
            {'id': 3, 'nome': 'Catedral de Notre-Dame'}
        ]
    },
    {
        'id': 2,
        'nome': 'Rio de Janeiro',
        'subtitulo': 'Cidade Maravilhosa',
        'descricao': 'Rio é conhecida por suas praias e o Cristo Redentor.',
        'atracoes': [
            {'id': 4, 'nome': 'Cristo Redentor'},
            {'id': 5, 'nome': 'Pão de Açúcar'},
            {'id': 6, 'nome': 'Copacabana'}
        ]
    }
]

# --------- Rotas Principais ---------
@app.route('/')
def root_index():
    return render_template('Index.html')

@app.route('/explorar')
def explorar_clean():
    q = request.args.get('q', '').lower()
    resultados = [c for c in cidades if q in c['nome'].lower()] if q else cidades
    return render_template('explorar.html', resultados=resultados)

@app.route('/galeria')
def galeria_clean():
    return render_template('galeria.html', cidades=cidades)

@app.route('/cidade/<int:cidade_id>')
def cidade_clean(cidade_id):
    cidade = next((c for c in cidades if c['id'] == cidade_id), None)
    if not cidade:
        return "Cidade não encontrada", 404
    return render_template('cidade_turistica.html', cidade=cidade)

@app.route('/login', methods=['GET','POST'])
def login_clean():
    if request.method == 'POST':
        # aqui você processaria login
        pass
    return render_template('login.html')

@app.route('/perfil', methods=['GET','POST'])
def perfil_clean():
    user = {'username':'fernanda', 'email':'fernanda@example.com'}
    stats = {'cartoes': 10, 'total_cartoes': 50, 'cidades': 5, 'total_cidades': 20}
    return render_template('perfil.html', user=user, stats=stats)

@app.route('/registre-se', methods=['GET','POST'])
def registrar():
    if request.method == 'POST':
        # processar registro
        pass
    return render_template('registre-se.html')

@app.route('/recuperar-senha', methods=['GET','POST'])
def recuperar_senha():
    if request.method == 'POST':
        # enviar email de recuperação
        pass
    return render_template('recuperar_senha.html')

# --------- Rota para Atrações ---------
@app.route('/atracao/<int:atracao_id>')
def atracao_detalhe(atracao_id):
    # busca atracao em todas as cidades
    atracao = next((a for c in cidades for a in c['atracoes'] if a['id']==atracao_id), None)
    if not atracao:
        return "Atração não encontrada", 404
    return f"Detalhes da atração: {atracao['nome']}"

# --------- Sidebar / Footer páginas extras ---------
@app.route('/destinos-populares')
def destinos_populares_clean():
    return render_template('galeria.html', cidades=cidades)

@app.route('/cartao-personalizado')
def cartao_personalizado_clean():
    return render_template('personalizacao.html')

@app.route('/faq')
def faq_clean():
    return render_template('faq.html')

@app.route('/contato')
def contato_clean():
    return render_template('contato.html')

# --------- Run app ---------
if __name__ == '__main__':
    app.run(debug=True)
