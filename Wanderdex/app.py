from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'segredo-super-seguro'

# Simulação de "banco de dados"
usuarios = {
    "admin": {
        "email": "admin@teste.com",
        "senha": "1234",
        "cartoes": 5
    }
}


@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('home'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('username')
        senha = request.form.get('password')

        if usuario in usuarios and usuarios[usuario]['senha'] == senha:
            session['user'] = usuario
            flash(f'Bem-vindo(a), {usuario}!', 'sucesso')
            return redirect(url_for('home'))
        else:
            flash('Usuário ou senha incorretos.', 'erro')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario = request.form.get('username')
        email = request.form.get('email')
        senha = request.form.get('password')

        if usuario in usuarios:
            flash('Usuário já existe. Escolha outro nome.', 'erro')
            return redirect(url_for('register'))

        usuarios[usuario] = {"email": email, "senha": senha, "cartoes": 0}
        flash('Cadastro realizado com sucesso! Faça login.', 'sucesso')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/home')
def home():
    if 'user' not in session:
        flash('Faça login para continuar.', 'info')
        return redirect(url_for('login'))
    user = session['user']
    return render_template('home.html', user=user)


@app.route('/galeria')
def galeria():
    if 'user' not in session:
        flash('Faça login para continuar.', 'info')
        return redirect(url_for('login'))
    return render_template('galeria.html', user=session['user'])


@app.route('/configuracoes')
def configuracoes():
    if 'user' not in session:
        flash('Faça login para continuar.', 'info')
        return redirect(url_for('login'))
    return render_template('configuracoes.html', user=session['user'])


@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if 'user' not in session:
        flash('Faça login para continuar.', 'info')
        return redirect(url_for('login'))

    usuario = session['user']
    dados = usuarios[usuario]

    if request.method == 'POST':
        senha = request.form.get('senha')
        if senha == dados['senha']:
            del usuarios[usuario]
            session.pop('user', None)
            flash('Conta excluída com sucesso.', 'sucesso')
            return redirect(url_for('index'))
        else:
            flash('Senha incorreta. Conta não excluída.', 'erro')

    return render_template('perfil.html', user=usuario, email=dados['email'], cartoes=dados['cartoes'])


@app.route('/faq')
def faq():
    return render_template('faq.html', logado=('user' in session))


@app.route('/contato', methods=['GET', 'POST'])
def contato():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        mensagem = request.form.get('mensagem')
        print(f"Mensagem de {nome} ({email}): {mensagem}")
        flash('Mensagem enviada com sucesso!', 'sucesso')
        return redirect(url_for('index'))

    return render_template('contato.html', logado=('user' in session))


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
