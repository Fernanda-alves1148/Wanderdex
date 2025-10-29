from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret')

# Usuários de exemplo
USERS = {
    'user': 'pass'
}

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if USERS.get(username) == password:
            session['user'] = username
            return redirect(url_for('home'))
        return render_template('login.html', error='Usuário ou senha incorretos')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', user=session.get('user'), active='home')

@app.route('/galeria')
def galeria():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('galeria.html', user=session.get('user'), active='galeria')

@app.route('/configuracoes')
def configuracoes():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('configuracoes.html', user=session.get('user'), active='configuracoes')

if __name__ == '__main__':
    app.run(debug=True)