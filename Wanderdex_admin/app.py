from flask import Flask, render_template, request, redirect, url_for
import itertools

app = Flask(__name__)

# Geradores simples de ID
next_attr_id = itertools.count(1)
next_card_id = itertools.count(1)

# Dados em memória
attractions = []
postcards = []

# ----------------------- ROTAS PÚBLICAS -----------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/perfil")
def perfil():
    return render_template("perfil.html")

# ----------------------- ATRAÇÕES -----------------------
@app.route("/atracoes")
def listar_atracoes():
    return render_template("atracoes.html", attractions=attractions)

@app.route("/atracoes/nova", methods=["GET", "POST"])
def nova_atracao():
    if request.method == "POST":
        attractions.append({
            "id": next(next_attr_id),
            "name": request.form.get("name"),
            "location": request.form.get("location"),
            "hours": request.form.get("hours"),
            "image": request.form.get("image"),
            "postcards": []
        })
        return redirect(url_for("listar_atracoes"))

    return render_template("gerencia_atracao.html", attraction=None)

@app.route("/atracoes/<int:attr_id>", methods=["GET", "POST"])
def editar_atracao(attr_id):
    atr = next((a for a in attractions if a["id"] == attr_id), None)
    if not atr:
        return "Atração não encontrada", 404

    if request.method == "POST":
        atr["name"] = request.form.get("name")
        atr["location"] = request.form.get("location")
        atr["hours"] = request.form.get("hours")
        atr["image"] = request.form.get("image")
        return redirect(url_for("listar_atracoes"))

    return render_template("gerencia_atracao.html", attraction=atr)

@app.route("/atracoes/<int:attr_id>/excluir")
def excluir_atracao(attr_id):
    global attractions
    attractions = [a for a in attractions if a["id"] != attr_id]
    return redirect(url_for("listar_atracoes"))

# ----------------------- CARTÕES -----------------------
@app.route("/cartoes")
def listar_cartoes():
    return render_template("cartoes.html", postcards=postcards, attractions=attractions)

@app.route("/cartoes/novo", methods=["GET", "POST"])
def novo_cartao():
    if request.method == "POST":
        card = {
            "id": next(next_card_id),
            "name": request.form.get("name"),
            "description": request.form.get("description"),
            "image": request.form.get("image"),
            "attraction": int(request.form.get("attraction"))
        }
        postcards.append(card)

        # adiciona referência na atração
        atr = next((a for a in attractions if a["id"] == card["attraction"]), None)
        if atr:
            atr["postcards"].append(card["id"])

        return redirect(url_for("listar_cartoes"))

    return render_template("gerencia_cartoes.html", postcard=None, attractions=attractions)

@app.route("/cartoes/<int:card_id>", methods=["GET", "POST"])
def editar_cartao(card_id):
    card = next((c for c in postcards if c["id"] == card_id), None)
    if not card:
        return "Cartão não encontrado", 404

    if request.method == "POST":
        # remover cartão da atração antiga
        old_atr = next((a for a in attractions if a["id"] == card["attraction"]), None)
        if old_atr and card["id"] in old_atr["postcards"]:
            old_atr["postcards"].remove(card["id"])

        # atualizar dados
        card["name"] = request.form.get("name")
        card["description"] = request.form.get("description")
        card["image"] = request.form.get("image")
        card["attraction"] = int(request.form.get("attraction"))

        # adicionar na nova atração
        new_atr = next((a for a in attractions if a["id"] == card["attraction"]), None)
        if new_atr:
            new_atr["postcards"].append(card["id"])

        return redirect(url_for("listar_cartoes"))

    return render_template("gerencia_cartoes.html", postcard=card, attractions=attractions)

@app.route("/cartoes/<int:card_id>/excluir")
def excluir_cartao(card_id):
    global postcards
    card = next((c for c in postcards if c["id"] == card_id), None)

    if card:
        # remover referência da atração
        atr = next((a for a in attractions if a["id"] == card["attraction"]), None)
        if atr and card_id in atr["postcards"]:
            atr["postcards"].remove(card_id)

        postcards = [c for c in postcards if c["id"] != card_id]

    return redirect(url_for("listar_cartoes"))

# ----------------------- RUN -----------------------
if __name__ == "__main__":
    app.run(debug=True)
