import datetime
from base64 import b64decode
from datetime import timedelta
from flask import Flask, request, render_template, redirect, flash, session, jsonify, make_response, url_for, json
import random
import os
import hmac
import hashlib
import sqlite3
import pickle
import logging
from pyChatGPT import ChatGPT
import openai
app = Flask(__name__)
app.secret_key = 'laclé'
app.config["SESSION_TYPE"]="filesystem"
openai.api_key = "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"

# Création du connecteur à la base de données database.db

import openai

openai.api_key = "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"


@app.route('/')
def main():
        return render_template("acceuilnotlogin.html")


@app.route('/login')
def login():
    if "user" in session:
        return redirect("/")
    else:
        return render_template("Login.html")

@app.route('/login', methods=['POST'])
def login_post():
    name = request.form.get('name')
    password = request.form.get('password')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT username from userinfo WHERE username = ? """, (name, ))
    liste = cursor.fetchall()
    if len(liste) == 0:
        flash("Ce pseudo n'est pas enregistré")
        return redirect("/login")
    elif len(name) > 20  or len(password) > 90:
        flash("L'adresse email , le mot de passe ou le nom est trop long !")
        return redirect("/login")
    cursor.execute("""SELECT password from userinfo WHERE username = ? """, (name, ))
    liste = cursor.fetchall()
    if liste[0][0] != password:
        flash("Mot de passe incorrect")
        return redirect("/login")
    session['user'] = name
    cursor.close()
    conn.commit()
    conn.close()
    return redirect("/")

@app.route('/signup')
def signin():

        if "user" in session:
            return redirect("/")
        return render_template("Signup.html")

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect("/")

@app.route('/signup', methods=['POST'])
def signup_post():
    name = request.form.get('name')
    password = request.form.get('password')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT username from userinfo WHERE username = ? """, (name, ))
    liste = cursor.fetchall()
    if len(liste) != 0:
        flash("Ce pseudo est déjà enregistré pour un autre soldat")
        return redirect("/signup")
    elif len(name) > 20  or len(password) > 90:
        flash("L'adresse email , le mot de passe ou le nom est trop long !")
        return redirect("/signup")
    requete = """INSERT INTO userinfo (username,password)VALUES(?,?)"""
    values = ( name,password,)
    cursor.execute(requete, values)
    session['user'] = name
    cursor.close()
    conn.commit()
    conn.close()
    return redirect("/")

@app.route('/apropos')
def apropos():
    return render_template("about.html")

@app.route('/cgu')
def cgu():
    return render_template("cgu.html")

@app.route('/profil')
def profil():
    return render_template("profil.html")

@app.route('/apprentissage')
def apprentissage():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT titre, description FROM lecon""")
    liste = cursor.fetchall()
    print(liste)
    cursor.close()


    return render_template("apprentissage.html",lecon = liste,n=len(liste))

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/add')
def add():
    return render_template("ajout.html")

@app.route('/challenge')
def challenge():
    return render_template('challenge.html')

@app.route('/scoreboard')
def scoreboard():
    return render_template('scoreboard.html')

@app.route('/coursparticulier')
def coursparticulier():
    return render_template('coursparticulier.html')

@app.route('/vocabulaire')
def vocabulaire():
    return render_template('ajout.html')

@app.route('/leçon/<id_lecon>',methods=['GET','POST'])
def lecon(id_lecon):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT titre, lecon FROM lecon WHERE id_lecon == ?""", (id_lecon,))
    liste = cursor.fetchall()
    cursor.close()

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT question FROM lecon WHERE id_lecon == ?""", (id_lecon,))
    question = cursor.fetchall()
    cursor.close()

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT nb_question FROM lecon WHERE id_lecon == ?""", (id_lecon,))
    nbquestion = cursor.fetchall()[0][0]
    cursor.close()

    if request.method == 'POST':
        lrep = ""
        for k in range(1,nbquestion+1):
            q = "q" + str(k)
            lrep += "Question " + str(k) + " : " + str(request.form.get(q)) + ", "

        prompt = """Un élève a été soumis à ces questions, ici écrites en HTML :""" + str(question) + """
    Il a répondu : 
    """ + lrep + """
    
    Tu es un professeur d'anglais qui doit corriger les réponses de l'élève. Génère uniquement le code HTML (sans me répondre) de la correction de ces questions avec une explication de l'erreur et un mot d'encouragement pour les réponses fausses. Ne met pas de if et de else pour vérifier si les réponses sont bonnes. De plus, lorsque la réponse est fausse, colore la en rouge et lorsque qu'elle est juste, colore la en vert
     
     Voici un exemple de ce que tu dois me répondre :
     
     <dl class="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-1">
        <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
            <fieldset>
                <legend>Question 1 : Quand utilise-t-on 'the' en anglais ?</legend>
                <label for="q1"></label>
                <input type="text" class="w-max text-center h-[50px] text-sm font-medium bg-white bg-opacity-20 placeholder-white text-black rounded mb-4 mx-10 outline-yes border border-[#ed2939] focus-visible:shadow-none focus:border-[#10B981]"" name="q1" id="q1" value="Les lundis" required>
                <p style="color: red;">Erreur : La réponse attendue était : "On utilise 'the' devant des noms communs définis", continuez comme ça, vous pouvez y arriver !</p>
            </fieldset>
        </div>
    </dl>
    <dl class="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-1">
        <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
            <fieldset>
                <legend>Question 2 : Quel est le rôle de 'the' en anglais ?</legend>
                <label for="q2">Choisissez la réponse qui convient :</label>
                <select class="w-max text-center h-[50px] text-sm font-medium bg-white bg-opacity-20 placeholder-white text-black rounded mb-4 mx-10 outline-yes border border-[#10B981] focus-visible:shadow-none focus:border-[#10B981]" name="q2" id="q2" required>
                    <option value="">-- Choisissez une réponse --</option>
                    <option value="1" name="q2">Article indéfini</option>
                    <option value="2" name="q2" selected>Article défini</option>
                    <option value="3" name="q2">Pronom personnel</option>
                    <option value="4" name="q2">Préposition</option>
                </select>
                <p style="color: green;">Félicitations ! Vous avez donné la bonne réponse.</p>
            </fieldset>
        </div>
    </dl>
    <dl class="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-1">
        <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
            <fieldset>
                <legend>Question 3 : Peut-on utiliser 'the' avec des noms propres en anglais ?</legend>
                <label for="q3">Répondez par oui ou par non :</label>
                <input type="radio" name="q3" id="q3_oui" value="oui" disabled> <label for="q3_oui" style="color: red;">Non</label>
                <input type="radio" name="q3" id="q3_non" value="non" checked> <label for="q3_non" style="color: green;">Oui</label>
                <p style="color: red;">Erreur : La réponse attendue était : "Non, on n'utilise pas 'the' avec des noms propres". Courage, vous êtes sur la bonne voie !</p>
            </fieldset>
        </div>
    </dl>
    <dl class="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-1">
        <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
            <fieldset>
                <legend>Question 4 : Dans quels cas doit-on utiliser 'the' avec des noms de lieux en anglais ?</legend>
                <label for="q4">Choisissez la réponse qui convient :</label>
                <select class="w-max text-center h-[50px] text-sm font-medium bg-white bg-opacity-20 placeholder-white text-black rounded mb-4 mx-10 outline-yes border border-[#ed2939] focus-visible:shadow-none focus:border-[#10B981]" name="q4" id="q4" required>
                    <option value="">-- Choisissez une réponse --</option>
                    <option value="1" name="q4" selected>Pour les noms de pays</option>
                    <option value="2" name="q4">Pour les noms de villes</option>
                    <option value="3" name="q4">Pour les noms de régions géographiques (montagnes, rivières, océans...)</option>
                    <option value="4" name="q4">Pour tous les noms de lieux en anglais</option>
                </select>
                <p style="color: red;">Erreur : La réponse attendue était : "On utilise 'the' devant les noms de régions géographiques (montagnes, rivières, océans...)". Ne vous découragez pas, vous pouvez y arriver !</p>
            </fieldset>
        </div>
    </dl>
    <dl class="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-1">
        <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
            <fieldset>
                <legend>Question 5 : Peut-on utiliser 'the' avec des noms comptables et dénombrables en anglais ?</legend>
                <label for="q5">Répondez par oui ou par non :</label>
                <input type="radio" name="q5" id="q5_oui" value="oui" checked> <label for="q5_oui" style="color: green;">Oui</label>
                <input type="radio" name="q5" id="q5_non" value="non" disabled> <label for="q5_non" style="color: red;">Non</label>
                <p style="color: red;">Erreur : La réponse attendue était : "On n'utilise pas 'the' avec des noms comptables et dénombrables". Bravo pour vos efforts !</p>
            </fieldset>
        </div>
    </dl>
     
     """
        reponse = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt},
            ]
        )
        print(reponse.choices[0].message.content)
        return render_template('leçon.html', lecon=liste, question=question, n=len(question),question_reponse=reponse.choices[0].message.content)
    return render_template('leçon.html', lecon=liste, question=question, n=len(question),question_reponse=question[0][0])



@app.route('/listevocabulaire')
def listevocabulaire():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT titre , description , id FROM vocabulaire""")
    liste = cursor.fetchall()
    cursor.close()
    return render_template('listevocab.html', vocabulaire = liste)

@app.route('/vocab/create')
def vocabcreate():
    return render_template('vocabcreate.html')

@app.route('/create', methods=['POST'])
def create():
    titre = request.form.get('title')
    description = request.form.get('description')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    requete = """INSERT INTO vocabulaire (titre,description)VALUES(?,?)"""
    values = ( titre,description,)
    cursor.execute(requete, values)
    cursor.close()
    conn.commit()
    conn.close()
    return redirect("/listevocabulaire")

@app.route('/vocab/<id_vocab>/edit')
def vocabedit(id_vocab):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT titre, description FROM vocabulaire WHERE id == ?""", (id_vocab,))
    liste = cursor.fetchall()
    print(id_vocab)
    cursor.execute("""SELECT mot, traduction FROM vocabulaire_mot WHERE id_vocabulaire == ?""", (id_vocab,))
    mots = cursor.fetchall()
    print(mots)
    cursor.close()
    return render_template('vocabedit.html', vocabulaire = liste , mots = mots , id_vocab = id_vocab)

@app.route('/ajout/<id_vocab>', methods=['POST'])
def ajout(id_vocab):
    mot = request.form.get('mot')
    traduction = request.form.get('traduction')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    requete = """INSERT INTO vocabulaire_mot (mot,id_vocabulaire,traduction)VALUES(?,?,?)"""
    values = ( mot,id_vocab,traduction,)
    cursor.execute(requete, values)
    cursor.close()
    conn.commit()
    conn.close()
    return redirect("/vocab/"+id_vocab+"/edit")

@app.route('/suppression/<mot>/<id_vocab>')
def suppression(mot,id_vocab):
    #Suppresion de la ligne correspondant a mot et id_vocab dans vocabulaire_mot
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""DELETE FROM vocabulaire_mot WHERE mot == ? AND id_vocabulaire == ?""", (mot,id_vocab,))
    cursor.close()
    conn.commit()
    conn.close()
    return redirect("/vocab/"+id_vocab+"/edit")

@app.route('/vocab/<id_vocab>')
def vocablearn(id_vocab):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT mot, traduction FROM vocabulaire_mot WHERE id_vocabulaire == ?""", (id_vocab,))
    liste = cursor.fetchall()
    cursor.close()
    return render_template('vocablearn.html', vocabulaire = liste , id_vocab = id_vocab)

@app.route('/verif/<id_vocab>', methods=['POST'])
def verif(id_vocab):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT mot, traduction FROM vocabulaire_mot WHERE id_vocabulaire == ?""", (id_vocab,))
    liste = cursor.fetchall()
    cursor.close()
    n = len(liste)
    somme = 0
    fautes = []
    for mot in liste:
        if request.form.get(mot[0]) == mot[1]:
            somme += 1
        else:
            fautes.append((mot[0],mot[1],request.form.get(mot[0])))
    return render_template('verif.html', vocabulaire = liste , id_vocab = id_vocab , somme = somme , n = n, fautes = fautes)

@app.route('/generer', methods=['POST'])
def generer():
    titre = request.form.get('Titre')
    fomat = request.form.get('format')
    difficulte = request.form.get('difficulte')
    nombre = request.form.get('nombre')
    # create a prompt
    prompt = """Génère un cours d'anglais en français sur le thème de""" + titre + """ avec des exemples en HTML mais seulement la partie entre les balises body tu rajouteras du style visuel au balise. Génère simplement le cours sans me répondre. Inspires toi de cet exemple pour générer le cours : 
        <style>
    			h1 {
    				font-size: 2.5rem;
    				font-weight: bold;
    				text-align: center;
    				margin-top: 2rem;
    			}
    			h2 {
    				font-size: 1.5rem;
    				font-weight: bold;
    				margin-top: 1.5rem;
    			}
    			p {
    				font-size: 1.2rem;
    				line-height: 1.5;
    				margin-top: 1rem;
    			}
    			ul {
    				font-size: 1.2rem;
    				line-height: 1.5;
    				margin-top: 1rem;
    				margin-left: 2rem;
    			}
    			.list {
    				list-style: disc;
    			}
    		</style>
    	<div class="container">
    	<h1>Le Present Perfect Continuous</h1>
    	<p>Le <em>Present Perfect Continuous</em> est un temps qui est utilisé pour décrire une action qui a commencé dans le passé et qui se poursuit jusqu'à maintenant. Ce temps est également appelé <em>Present Perfect Progressive</em>.</p>
    	<h2>Formation</h2>
    <p>Le Present Perfect Continuous est formé en utilisant le Present Perfect de "to be" (au présent) + le participe présent de "to be" + le verbe principal avec "-ing".</p>
    <p>Exemple : I have been studying for two hours. (J'étudie depuis deux heures.)</p>

    <h2>Utilisation</h2>
    <p>Le Present Perfect Continuous est souvent utilisé pour :</p>
    <ul>
    	<li class="list">Décrire une action qui a commencé dans le passé et qui se poursuit jusqu'à maintenant.</li>
    	<li class="list">Décrire une action qui a été répétée plusieurs fois dans le passé et qui continue jusqu'à maintenant.</li>
    	<li class="list">Exprimer une action qui a commencé dans le passé mais qui est toujours en cours dans le présent et qui peut continuer dans le futur.</li>
    	<li class="list">Exprimer un changement graduel ou une évolution.</li>
    </ul>

    <h2>Exemples</h2>
    <p>Voici quelques exemples de phrases avec le Present Perfect Continuous :</p>
    <ul>
    	<li class="list">I have been studying for two hours. (J'étudie depuis deux heures.)</li>
    	<li class="list">She has been working in this company for five years. (Elle travaille dans cette entreprise depuis cinq ans.)</li>
    	<li class="list">They have been playing tennis every Saturday. (Ils jouent au tennis tous les samedis.)</li>
    	<li class="list">The tree has been growing slowly for many years. (L'arbre pousse lentement depuis de nombreuses années.)</li>
    </ul>
    </div>
    """

    # call openai api using the model davinci

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ]
    )

    # print the response
    reponse = response.choices[0].message.content
    "0_0"
    # insert the response in the database
    descr = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user",
             "content": """Ecrit uniquement le contenu que je te demande ne me répond pas .Fait un résumé en HTML mais uniquement le contenu entre les balises body de ce cours : """ + reponse + """ , tu dois reprendre le modèle de l'exemple de résumé suivant : Cette leçon présente l'utilisation du present perfect continuous en anglais. Elle est composée de 3 parties :<br>
    •	La première partie présente la forme du present perfect continuous et son utilisation.<br>
    •	La deuxième partie présente des exemples d'utilisation du present perfect continuous.<br>
    •	La troisième partie présente des exercices d'application."""},
        ]
    )

    quest = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user",
             "content": """Ecrit uniquement le contenu que je te demande ne me répond pas .Fait"""+nombre+"""questions en HTML ( uniquement le contenu entre les balises body) de ce cours : """ + reponse + """ . Tu dois faire des question au format : """+fomat+""". Les questions seront de difficulté : +"""+difficulte+""". Tu dois reprendre le modèle de l'exemple de questions suivant : <dl class="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-1">
            <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
    		<fieldset>
    			<legend>Question 1 : Quand utilise-t-on 'the' en anglais ?</legend>
    			<label for="q1"></label>
    			<input  type="text"
                            class="
                              w-max
                              text-center
                              h-[50px]
                              text-sm
                              font-medium
                              bg-white bg-opacity-20
                              placeholder-white
                              text-black
                              rounded
                              mb-4
                              mx-10
                              outline-yes
                              border border-black
                              focus-visible:shadow-none
                              focus:border-white
                            "
                        name="q1" id="q1" required>
            </fieldset></div></dl>
            <dl class="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-1">
            <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
    	<fieldset>
    		<legend>Question 2 : Quel est le rôle de 'the' en anglais ?</legend>
    		<label for="q2">Choisissez la réponse qui convient :</label>
    		<select type="text"
                            class="
                              w-max
                              text-center
                              h-[50px]
                              text-sm
                              font-medium
                              bg-white bg-opacity-20
                              placeholder-white
                              text-black
                              rounded
                              mb-4
                              mx-10
                              outline-yes
                              border border-black
                              focus-visible:shadow-none
                              focus:border-white
                            "

                    name="q2" id="q2" required>
    			<option value="">-- Choisissez une réponse --</option>
    			<option value="1" name="q2">Article indéfini</option>
    			<option value="2" name="q2">Article défini</option>
    			<option value="3" name="q2">Pronom personnel</option>
    			<option value="4" name="q2">Préposition</option>
    		</select>
        </fieldset></div></dl>
        <dl class="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-1">
            <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
    	<fieldset>
    		<legend>Question 3 : Peut-on utiliser 'the' avec des noms propres en anglais ?</legend>
    		<label for="q3">Répondez par oui ou par non :</label>
    		<input type="radio" name="q3" id="q3_oui" value="oui" required> <label for="q3_oui">Oui</label>
    		<input type="radio" name="q3" id="q3_non" value="non"> <label for="q3_non">Non</label>
        </fieldset></div></dl>
        <dl class="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-1">
            <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
    	<fieldset>
    		<legend>Question 4 : Dans quels cas doit-on utiliser 'the' avec des noms de lieux en anglais ?</legend>
    		<label for="q4">Choisissez la réponse qui convient :</label>
    		<select  type="text"
                            class="
                              w-max
                              text-center
                              h-[50px]
                              text-sm
                              font-medium
                              bg-white bg-opacity-20
                              placeholder-white
                              text-black
                              rounded
                              mb-4
                              mx-10
                              outline-yes
                              border border-black
                              focus-visible:shadow-none
                              focus:border-white
                            "
                    name="q4" id="q4" required>
    			<option value="">-- Choisissez une réponse --</option>
    			<option value="1" name="q4">Pour les noms de pays</option>
    			<option value="2" name="q4">Pour les noms de villes</option>
    			<option value="3" name="q4">Pour les noms de régions géographiques (montagnes, rivières, océans...)</option>
    			<option value="4" name="q4">Pour tous les noms de lieux en anglais</option>
    		</select>
        </fieldset></div></dl>
        <dl class="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-1">
            <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
    	<fieldset>
    		<legend>Question 5 : Peut-on utiliser 'the' avec des noms comptables et dénombrables en anglais ?</legend>
    		<label for="q5">Répondez par oui ou par non :</label>
    		<input type="radio" name="q5" id="q5_oui" value="oui" required> <label for="q5_oui">Oui</label>
    		<input type="radio" name="q5" id="q5_non" value="non"> <label for="q5_non">Non</label>
        </fieldset></div></dl>"""},
        ]
    )

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    requete = """INSERT INTO lecon (titre,lecon,description,question,nb_question)VALUES(?,?,?,?,?)"""
    values = (titre, str(reponse), str(descr.choices[0].message.content), str(quest.choices[0].message.content), 5,)
    cursor.execute(requete, values)
    cursor.close()
    # get the id of the last inserted row
    cursor = conn.cursor()
    cursor.execute("""SELECT id_lecon FROM lecon ORDER BY id_lecon DESC LIMIT 1""")
    id_lecon = cursor.fetchall()
    cursor.close()
    conn.commit()
    conn.close()
    return redirect("/leçon/" + str(id_lecon[0][0]))

@app.route('/creation')
def creation():
    return render_template('creation.html')

@app.route('/present_perfect',methods=['GET','POST'])
def present_perfect():
    correct = [2 for k in range(5)]
    if request.method == 'POST':
        rep = ["1","3","oui","1","oui"]
        for k in range(5):
            print(request.form.get("q" + str(k + 1)))
            if request.form.get("q" + str(k + 1)) == rep[k]:
                correct[k] = 1
            else:
                correct[k] = 0
    return render_template('Present_perfect.html',correct=correct)


@app.route('/the',methods=['GET','POST'])
def the():
    correct = [2 for k in range(5)]
    if request.method == 'POST':
        rep = ["2","oui","oui","4","oui"]
        for k in range(5):
            print(request.form.get("q" + str(k + 1)))
            if request.form.get("q" + str(k + 1)) == rep[k]:
                correct[k] = 1
            else:
                correct[k] = 0
    return render_template('the.html',correct=correct)

if __name__ == '__main__':

    app.run()


