import sqlite3

#Création de la base de données database.db

conn = sqlite3.connect('database.db')
print("Opened database successfully")

#Création de la table user
cursor = conn.cursor()
# Création de la table user avec les champs id, username, password
cursor.execute('''DROP TABLE IF EXISTS userinfo''')
cursor.execute('''DROP TABLE IF EXISTS lecon''')
cursor.execute('''DROP TABLE IF EXISTS vocabulaire''')
cursor.execute('''DROP TABLE IF EXISTS vocabulaire_mot''')
cursor.execute('''DROP TABLE IF EXISTS cours''')
cursor.execute('''DROP TABLE IF EXISTS lecon_corrigee''')
cursor.execute('''CREATE TABLE userinfo (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)''')
cursor.execute('''CREATE TABLE lecon (id_lecon INTEGER PRIMARY KEY AUTOINCREMENT, titre TEXT, description TEXT, lecon TEXT, question TEXT, nb_question INTEGER)''')
cursor.execute('''CREATE TABLE vocabulaire (id INTEGER PRIMARY KEY AUTOINCREMENT, titre TEXT , description TEXT) ''')
cursor.execute('''CREATE TABLE vocabulaire_mot (id INTEGER PRIMARY KEY AUTOINCREMENT, id_vocabulaire INTEGER, mot TEXT, traduction TEXT) ''')
cursor.execute('''CREATE TABLE cours (id INTEGER PRIMARY KEY AUTOINCREMENT, titre TEXT , contenu TEXT) ''')
cursor.execute('''CREATE TABLE lecon_corrigee (id_lecon INTEGER PRIMARY KEY, titre TEXT, description TEXT, lecon TEXT, questions TEXT, reponses TEXT) ''')

