from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

#config banco de dados mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://wanderdex_user:wanderdex@localhost/wanderdex_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Chave secreta para sessões e mensagens de feedback (flash messages)
app.config['SECRET_KEY'] = 'chave_super_secreta_wanderdex'

# Inicializa o banco
db = SQLAlchemy(app)

#tabelas bnco de dados

class Cidade(db.Model):
    __tablename__ = 'cidades'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    subtitulo = db.Column(db.String(150))
    descricao = db.Column(db.Text)
    imagem_url = db.Column(db.String(255))
    
    atracoes = db.relationship('Atracao', backref='cidade', lazy=True, cascade="all, delete-orphan")

class Atracao(db.Model):
    __tablename__ = 'atracoes'
    id = db.Column(db.Integer, primary_key=True)
    cidade_id = db.Column(db.Integer, db.ForeignKey('cidades.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    local = db.Column(db.String(150))
    horario = db.Column(db.String(100))
    imagem_url = db.Column(db.String(255))

    cartoes = db.relationship('Cartao', backref='atracao', lazy=True, cascade="all, delete-orphan")

class Cartao(db.Model):
    __tablename__ = 'cartoes'
    id = db.Column(db.Integer, primary_key=True)
    atracao_id = db.Column(db.Integer, db.ForeignKey('atracoes.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    imagem_url = db.Column(db.String(255))

usuario_cartoes = db.Table('usuario_cartoes',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuarios.id'), primary_key=True),
    db.Column('cartao_id', db.Integer, db.ForeignKey('cartoes.id'), primary_key=True))

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    cartoes = db.relationship('Cartao', secondary=usuario_cartoes, lazy='subquery',
    backref=db.backref('colecionadores', lazy=True))

    # Método para definir a senha (criptografar)
    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    # Método para verificar a senha (comparar texto com a criptografia)
    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)


#rotas site

@app.route('/')
def root_index():
    cidades = Cidade.query.limit(3).all()
    return render_template('Index.html', cidades=cidades)

@app.route('/explorar')
def explorar_clean():
    q = request.args.get('q', '')
    if q:
        resultados = Cidade.query.filter(Cidade.nome.ilike(f'%{q}%')).all()
    else:
        resultados = Cidade.query.all()
    return render_template('explorar.html', resultados=resultados)

@app.route('/galeria')
def galeria_clean():
    cidades = Cidade.query.all()
    return render_template('galeria.html', cidades=cidades)

@app.route('/cidade/<int:cidade_id>')
def cidade_clean(cidade_id):
    cidade = Cidade.query.get_or_404(cidade_id)
    return render_template('cidade_turistica.html', cidade=cidade)

@app.route('/atracao/<int:atracao_id>')
def atracao_detalhe(atracao_id):
    atracao = Atracao.query.get_or_404(atracao_id)
    return render_template('galeria_cidade1.html', atracao=atracao)


#CONFIGURAR PRA FUNCIONAR SEM USUÁRIO LOGADO E COM USUÁRIO LOGADO
@app.route('/login', methods=['GET', 'POST'])
def login_clean():
    if request.method == 'POST':
        username = request.form['username']
        senha = request.form['password']

        # Busca o usuário no banco
        usuario = Usuario.query.filter_by(username=username).first()

        # Verifica se o usuário existe E se a senha bate com a hash
        if usuario and usuario.verificar_senha(senha):
            session['usuario_logado'] = True
            session['username'] = usuario.username
            session['user_id'] = usuario.id
            session['is_admin'] = usuario.is_admin # Salva se é admin ou não
            
            flash(f'Bem-vindo de volta, {usuario.username}!')
            
            # Se for admin, manda pro dashboard. Se não, manda pro perfil.
            if usuario.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('perfil_clean'))
        else:
            flash('Usuário ou senha incorretos.')

    return render_template('login.html')

@app.route('/registre-se', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        nome = request.form['username']
        email = request.form['email']
        senha = request.form['password']

        # Verifica se usuário já existe
        usuario_existente = Usuario.query.filter_by(username=nome).first()
        if usuario_existente:
            flash('Nome de usuário já está em uso.')
            return redirect(url_for('registrar'))

        # Cria novo usuário
        novo_usuario = Usuario(username=nome, email=email)
        novo_usuario.set_senha(senha) # Criptografa a senha aqui!
        
        db.session.add(novo_usuario)
        db.session.commit()

        flash('Conta criada com sucesso! Faça login.')
        return redirect(url_for('login_clean'))
    
    return render_template('registre-se.html')

@app.route('/recuperar-senha')
def recuperar_senha():
    return render_template('recuperar_senha.html')

@app.route('/perfil', methods=['GET', 'POST'])
def perfil_clean():
    if 'usuario_logado' not in session:
        flash('Faça login para acessar seu perfil.')
        return redirect(url_for('login_clean'))
    
    usuario_id = session.get('user_id')
    usuario = Usuario.query.get(usuario_id)
    
    #SALVAR ALTERAÇÕES
    if request.method == 'POST':
        novo_username = request.form.get('username')
        novo_email = request.form.get('email')

        # Validação: Verifica se já existe OUTRO usuário com esse nome
        usuario_existente = Usuario.query.filter(Usuario.username == novo_username, Usuario.id != usuario_id).first()
        email_existente = Usuario.query.filter(Usuario.email == novo_email, Usuario.id != usuario_id).first()

        if usuario_existente:
            flash('Erro: Este nome de usuário já está em uso por outra pessoa.', 'error')
        elif email_existente:
            flash('Erro: Este e-mail já está cadastrado em outra conta.', 'error')
        else:
            usuario.username = novo_username
            usuario.email = novo_email
            try:
                # Salva no MySQL
                db.session.commit()
                session['username'] = novo_username
                
                flash('Perfil atualizado com sucesso!', 'success')
            except:
                db.session.rollback()
                flash('Erro ao salvar no banco de dados.', 'error')
            
            # Recarrega a página para mostrar os dados novos
            return redirect(url_for('perfil_clean'))
        
    #EXIBIÇÃO
    cidades_visitadas = set()
    for cartao in usuario.cartoes:
        # Pega a cidade através da atração do cartão
        cidades_visitadas.add(cartao.atracao.cidade.nome)
    
    estatisticas = {
        'cartoes': len(usuario.cartoes),          # Total de cartões do usuário
        'total_cartoes': Cartao.query.count(),    # Total de cartões no sistema
        'cidades': len(cidades_visitadas),        # Cidades únicas do usuário
        'total_cidades': Cidade.query.count()     # Total de cidades no sistema
    }

    dados_usuario = {
        'username': usuario.username,
        'email': usuario.email
    }

    return render_template('perfil.html', user=dados_usuario, stats=estatisticas)

@app.route('/logout')
def logout():
    # Remove os dados de sessão do usuário
    session.pop('usuario_logado', None)
    session.pop('username', None)
    session.pop('user_id', None)
    session.pop('is_admin', None)
    
    flash('Você saiu da sua conta.')
    return redirect(url_for('login_clean'))


#ADMIN

@app.route('/admin')
def admin_dashboard():
    return render_template('admin/dashboard.html')

#Gerenciar Cidades

@app.route('/admin/cidades')
def admin_cidades():
    cidades = Cidade.query.all()
    return render_template('admin/lista_cidades.html', cidades=cidades)

@app.route('/admin/cidades/nova', methods=['GET', 'POST'])
def admin_nova_cidade():
    if request.method == 'POST':
        nova_cidade = Cidade(
            nome=request.form['nome'],
            subtitulo=request.form['subtitulo'],
            descricao=request.form['descricao'],
            imagem_url=request.form['imagem_url']
        )
        db.session.add(nova_cidade)
        db.session.commit()
        flash('Cidade criada com sucesso!')
        return redirect(url_for('admin_cidades'))
    
    return render_template('admin/form_cidade.html')

@app.route('/admin/cidades/deletar/<int:id>')
def admin_deletar_cidade(id):
    cidade = Cidade.query.get_or_404(id)
    db.session.delete(cidade)
    db.session.commit()
    flash('Cidade removida!')
    return redirect(url_for('admin_cidades'))


#Gerenciar atrações

@app.route('/admin/atracoes')
def admin_atracoes():
    atracoes = Atracao.query.all()
    return render_template('admin/atracoes.html', attractions=atracoes)

@app.route('/admin/atracoes/nova', methods=['GET', 'POST'])
def admin_nova_atracao():
    if request.method == 'POST':
        nova_atracao = Atracao(
            nome=request.form['name'],
            local=request.form['location'],
            horario=request.form['hours'],
            imagem_url=request.form['image'],
            cidade_id=request.form['cidade_id']
        )
        db.session.add(nova_atracao)
        db.session.commit()
        flash('Atração criada com sucesso!')
        return redirect(url_for('admin_atracoes'))
    
    #lista de cidades
    cidades = Cidade.query.all()
    return render_template('admin/gerencia_atracao.html', attraction=None, cidades=cidades)

@app.route('/admin/atracoes/editar/<int:id>', methods=['GET', 'POST'])
def admin_editar_atracao(id):
    atracao = Atracao.query.get_or_404(id)
    
    if request.method == 'POST':
        atracao.nome = request.form['name']
        atracao.local = request.form['location']
        atracao.horario = request.form['hours']
        atracao.imagem_url = request.form['image']
        atracao.cidade_id = request.form['cidade_id']
        
        db.session.commit()
        flash('Atração atualizada!')
        return redirect(url_for('admin_atracoes'))
    
    cidades = Cidade.query.all()
    return render_template('admin/gerencia_atracao.html', attraction=atracao, cidades=cidades)

@app.route('/admin/atracoes/excluir/<int:id>')
def admin_excluir_atracao(id):
    atracao = Atracao.query.get_or_404(id)
    db.session.delete(atracao)
    db.session.commit()
    flash('Atração excluída!')
    return redirect(url_for('admin_atracoes'))


if __name__ == '__main__':
    # Cria as tabelas no banco de dados se elas ainda não existirem
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)
