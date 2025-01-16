from datetime import date, datetime
import mysql.connector
from flask import Flask, jsonify, request
from fpdf import FPDF
import subprocess

from flask_cors import CORS


import os


app = Flask(__name__)
CORS(app)

def format_date_to_ddmmyyyy(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")  # Convertir la chaîne en objet date
        return date_obj.strftime("%d/%m/%Y")  # Retourner la date formatée
    except ValueError:
        return None  

# Configuration de la base de données MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '', 
    'database': 'distribeton'
}

@app.route('/test-db', methods=['GET'])
def test_db():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify({"message": f"Connexion réussie à la base de données : {db_name[0]}"})
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)})
@app.route('/ajouterChauffeur', methods=['POST'])
def ajouter_chauffeur():
    try:
        # Récupérer les données du chauffeur envoyées en JSON
        data = request.get_json()
        nom = data.get('nom')
        telephone = data.get('telephone')
        plaque_camion = data.get('plaque_camion')

        if not nom or not telephone or not plaque_camion:
            return jsonify({"error": "Tous les champs doivent être remplis"}), 400

        # Connexion à la base de données
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Requête pour insérer un chauffeur
        query = """
        INSERT INTO chauffeurs (nom, telephone, plaque_camion) 
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (nom, telephone, plaque_camion))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Chauffeur ajouté avec succès"}), 201

    except mysql.connector.Error as err:
        return jsonify({"error": f"Erreur SQL : {str(err)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Erreur : {str(e)}"}), 500
@app.route('/chauffeur/<int:id>', methods=['GET'])
def lister_chauffeur(id):
    try:
        # Connexion à la base de données
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Requête pour récupérer un chauffeur par ID
        query = "SELECT id, nom, telephone, plaque_camion FROM chauffeurs WHERE id = %s"
        cursor.execute(query, (id,))
        chauffeur = cursor.fetchone()

        cursor.close()
        conn.close()

        if chauffeur:
            chauffeur_data = {
                "id": chauffeur[0],
                "nom": chauffeur[1],
                "telephone": chauffeur[2],
                "plaque_camion": chauffeur[3]
            }
            return jsonify(chauffeur_data), 200
        else:
            return jsonify({"error": "Chauffeur non trouvé"}), 404

    except mysql.connector.Error as err:
        return jsonify({"error": f"Erreur SQL : {str(err)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Erreur : {str(e)}"}), 500
@app.route('/getAllChauffeurs', methods=['GET'])
def get_all_chauffeurs():
    try:
        # Connexion à la base de données
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Requête pour récupérer tous les chauffeurs
        query = "SELECT id, nom, telephone, plaque_camion FROM chauffeurs"
        cursor.execute(query)
        chauffeurs = cursor.fetchall()

        cursor.close()
        conn.close()

        # Construire la liste des chauffeurs
        chauffeurs_list = []
        for chauffeur in chauffeurs:
            chauffeurs_list.append({
                "id": chauffeur[0],
                "nom": chauffeur[1],
                "telephone": chauffeur[2],
                "plaque_camion": chauffeur[3]
            })

        # Retourner la réponse JSON
        return jsonify({"chauffeurs": chauffeurs_list}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": f"Erreur SQL : {str(err)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Erreur : {str(e)}"}), 500

# Ajouter une commande dans la table bonCommande
@app.route('/ajouterBonCommande', methods=['POST'])
def ajouter_bon_commande():
    try:
        data = request.get_json()

        # Extraction des données comme avant
        nomclient = data['nomclient']
        adresse_chantier = data['adresse_chantier']
        quantite_commande = data['quantite_commande']
        quantite_charge = data['quantite_charge']
        quantite_restante = data['quantite_restante']
        formulation = data['formulation']
        plaque_camion = data['plaque_camion']
        livraison_type = data['livraison_type']
        statut = data['statut']
        date_commande = data['date_commande']
        date_production = data['date_production']
        heure_depart = data['heure_depart']
        heure_darrive = data['heure_darrive']
        chauffeur = data['chauffeur']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = """
        INSERT INTO bonCommande (nomclient, adresse_chantier, quantite_commande, quantite_charge, quantite_restante, formulation, plaque_camion, livraison_type, statut, date_commande, date_production, heure_depart, heure_darrive, chauffeur) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (nomclient, adresse_chantier, quantite_commande, quantite_charge, quantite_restante, formulation, plaque_camion, livraison_type, statut, date_commande, date_production, heure_depart, heure_darrive, chauffeur))

        # Récupérer l'ID généré pour la commande
        bon_commande_id = cursor.lastrowid
        conn.commit()

        # Générer le PDF
        bon_commande = {
            'id': bon_commande_id,
            'nomclient': nomclient,
            'adresse_chantier': adresse_chantier,
            'quantite_commande': quantite_commande,
            'quantite_charge': quantite_charge,
            'quantite_restante': quantite_restante,
            'formulation': formulation,
            'plaque_camion': plaque_camion,
            'livraison_type': livraison_type,
            'statut': statut,
            'date_commande': date_commande,
            'date_production': date_production,
            'heure_depart': heure_depart,
            'heure_darrive': '',
            'chauffeur': chauffeur
        }

        #pdf_path = generer_pdf(bon_commande)
       # if not pdf_path:
           # raise Exception("Erreur lors de la génération du PDF")

        cursor.close()
        conn.close()

        return jsonify({"message": "Bon de commande ajouté avec succès", "idcommande": bon_commande_id}), 201
           # return jsonify({"message": "Bon de commande ajouté avec succès", "pdf_path": pdf_path}), 201


    except mysql.connector.Error as err:
        return jsonify({"error": f"Erreur SQL : {str(err)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Erreur : {str(e)}"}), 500

@app.route('/updateCommande/<int:id>', methods=['PUT'])
def update_commande(id):
    try:
        # Récupérer les données envoyées en JSON
        data = request.get_json()

        if not data:
            return jsonify({"error": "Aucune donnée envoyée pour la mise à jour"}), 400

        # Connexion à la base de données
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Construire la requête SQL pour la mise à jour
        update_fields = []
        values = []
        for key, value in data.items():
            update_fields.append(f"{key} = %s")
            values.append(value)

        # Ajouter l'ID comme dernier paramètre pour la clause WHERE
        values.append(id)

        # Préparer la requête SQL
        query = f"UPDATE bonCommande SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(query, values)
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Aucune commande trouvée avec cet ID"}), 404

        # Récupérer les données complètes de la commande mise à jour
        cursor.execute("SELECT * FROM bonCommande WHERE id = %s", (id,))
        updated_commande = cursor.fetchone()

        if not updated_commande:
            return jsonify({"error": "Commande introuvable après mise à jour"}), 404

        # Mapper les colonnes avec les valeurs
        columns = [desc[0] for desc in cursor.description]
        bon_commande = dict(zip(columns, updated_commande))

        # Générer le PDF avec les données mises à jour
        pdf_path = generer_pdf(bon_commande)
        if not pdf_path:
            raise Exception("Erreur lors de la génération du PDF")

        cursor.close()
        conn.close()

        # Retourner le chemin complet du PDF
        return jsonify({
            "message": "Commande mise à jour avec succès",
            "pdf_path": pdf_path  # Chemin complet vers le fichier PDF
        }), 200

    except mysql.connector.Error as err:
        return jsonify({"error": f"Erreur SQL : {str(err)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Erreur : {str(e)}"}), 500

# Récupérer toutes les commandes
@app.route('/getAllCommande', methods=['GET'])
def get_all_commandes():
    """
    Retourne la liste des bons de commande au format JSON.
    """
    try:
        # Connexion à la base de données
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Exécuter la requête pour récupérer toutes les commandes
        cursor.execute("SELECT * FROM bonCommande")
        commandes = cursor.fetchall()
        cursor.close()
        conn.close()

        # Construire une liste de commandes
        commandes_list = []
        for commande in commandes:
            commandes_list.append({
                "id": commande[0],
                "nomclient": commande[1],
                "adresse_chantier": commande[2],
                "quantite_commande": commande[3],
                "quantite_charge": commande[4],
                "quantite_restante": commande[5],
                "formulation": commande[6],
                "chauffeur_id": commande[7],
                "plaque_camion": commande[8],
                "livraison_type": commande[9],
                "statut": commande[10],
                "date_commande": str(commande[11]) if commande[11] else None,  # Convertir en string
                "date_production": str(commande[12]) if commande[12] else None,
                "heure_depart": str(commande[13]) if commande[13] else None,
                "heure_arrivee": str(commande[14]) if commande[14] else None,
            })

        # Retourner la réponse JSON
        return jsonify({"data": commandes_list})

    except mysql.connector.Error as err:
        return jsonify({"error": f"Erreur SQL : {str(err)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Erreur : {str(e)}"}), 500

@app.route('/commande/<int:id>', methods=['GET'])
def get_commande_by_id(id):
    try:
        # Connexion à la base de données
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Requête pour récupérer une commande par ID
        query = "SELECT * FROM bonCommande WHERE id = %s"
        cursor.execute(query, (id,))
        commande = cursor.fetchone()

        cursor.close()
        conn.close()

        if commande:
            commande_data = {
                "id": commande[0],
                "nomclient": commande[1],
                "adresse_chantier": commande[2],
                "quantite_commande": commande[3],
                "quantite_charge": commande[4],
                "quantite_restante": commande[5],
                "formulation": commande[6],
                "plaque_camion": commande[7],
                "chauffeur": commande[8],
                "livraison_type": commande[9],
                "statut": commande[10],
                "date_commande": str(commande[11]) if commande[11] else None,  # Convertir en string
                "date_production": str(commande[12]) if commande[12] else None,
                "heure_depart": str(commande[13]) if commande[13] else None,
                "heure_arrivee": str(commande[14]) if commande[14] else None,
            }
            return jsonify(commande_data), 200
        else:
            return jsonify({"error": "Commande non trouvée"}), 404

    except mysql.connector.Error as err:
        return jsonify({"error": f"Erreur SQL : {str(err)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Erreur : {str(e)}"}), 500

def lancer_impression(filepath):
    """
    Lance l'impression du fichier PDF en fonction du système d'exploitation.
    """
    try:
        if os.name == 'nt':  # Windows
            os.startfile(filepath, "print")
        elif os.name == 'posix':  # macOS / Linux
            subprocess.run(["lp", filepath], check=True)
        else:
            print("Impression non supportée sur ce système.")
    except Exception as e:
        print(f"Erreur lors de l'impression : {e}")

class PDF(FPDF):
    def header(self):
        # En-tête de l'entreprise
        self.set_font('Arial', 'B', 30)
        self.set_text_color(47,59,233)
        self.cell(0, 10, 'DISTRICO SÉNÉGAL', border=False, ln=True, align='C')
        self.set_font('Arial', '', 10)
        self.cell(0, 10, 'Adresse : Rue XYZ, Dakar, Sénégal | Téléphone : +221 33 123 45 67', border=False, ln=True, align='C')
        self.ln(10)  # Espace sous l'en-tête

    def footer(self):
        # Pied de page avec le numéro de page
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

import os
import os
from pathlib import Path

def generer_pdf(bon_commande):
    try:
        # Initialiser un document PDF
        pdf = PDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Titre du bon de commande
        pdf.set_font('Arial', 'B', 24)
        pdf.cell(0, 10, 'BON DE LIVRAISON', ln=True, align='C')
        pdf.ln(5)

        # Entêtes du tableau
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(60, 10, 'Désignation', border=1, fill=True, align='C')
        pdf.cell(0, 10, 'Valeurs', border=1, fill=True, align='C')
        pdf.ln()

        # Contenu du tableau
        pdf.set_font('Arial', '', 12)
        mapping = {
            'nomclient': 'Nom du client',
            'adresse_chantier': 'Adresse du chantier',
            'quantite_commande': 'Quantité commandée',
            'quantite_charge': 'Quantité chargée',
            'quantite_restante': 'Quantité restante',
            'formulation': 'Formulation',
            'plaque_camion': 'Plaque du camion',
            'livraison_type': 'Type de livraison',
            'statut': 'Statut de la commande',
            'date_commande': 'Date de la commande',
            'date_production': 'Date de production',
            'heure_depart': "Heure de départ",
            'heure_darrive': "Heure d'arrivée",
            'chauffeur': 'Chauffeur'
        }

        for key, value in bon_commande.items():
            if key in mapping:
                pdf.set_fill_color(240, 240, 240)
                pdf.cell(80, 10, mapping[key], border=1, fill=True, align='L')
                pdf.cell(0, 10, str(value), border=1, ln=True, align='L')

        pdf.ln(10)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(60, 10, 'OPERATEUR', align='L')
        pdf.cell(60, 10, 'CHAUFFEUR', align='C')
        pdf.cell(60, 10, 'CLIENT', align='R')

        # Détecter le dossier "Desktop" indépendamment du système
        desktop = Path.home() / 'Desktop'  # Fonctionne sur Windows, macOS et Linux
        output_dir = desktop / 'BONDECOMMANDE'

        # Créer le dossier s'il n'existe pas
        os.makedirs(output_dir, exist_ok=True)

        # Nom complet du fichier PDF
        pdf_filename = output_dir / f"bon_commande_{bon_commande['id']}.pdf"
        pdf.output(str(pdf_filename))
         # Lancer l'impression automatique
        lancer_impression(str(pdf_filename))

        return str(pdf_filename)
    except Exception as e:
        print(f"Erreur lors de la génération du PDF : {e}")
        return None

@app.route('/download-pdf/<int:id>', methods=['GET'])
def download_pdf(id):
    """
    Télécharge un PDF existant à partir de l'ID de la commande.
    """
    pdf_path = f"generated_pdfs/bon_commande_{id}.pdf"
    if os.path.exists(pdf_path):
        return os.sendfile(pdf_path, as_attachment=True)
    else:
        return jsonify({"error": "Le fichier PDF n'existe pas"}), 404

class PDFx(FPDF):
    def header(self):
        # En-tête de l'entreprise
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Distribeton - Rapport de Production', border=False, ln=True, align='C')
        self.set_font('Arial', '', 10)
        self.cell(0, 10, 'Adresse : Rue XYZ, Dakar, Sénégal | Téléphone : +221 33 123 45 67', border=False, ln=True, align='C')
        self.ln(10)  # Espace sous l'en-tête

    def footer(self):
        # Pied de page avec le numéro de page
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')
# Fonction pour générer le rapport PDF
@app.route('/genererRapport', methods=['POST'])
def generer_rapport():
    try:
        # Récupérer la date du paramètre de la requête
        data = request.get_json()
        date_rapport = data.get('date_rapport', None)

        # Si la date n'est pas fournie, utiliser la date d'aujourd'hui
        if not date_rapport:
            from datetime import datetime
            date_rapport = datetime.today().strftime('%Y-%m-%d')

        # Connexion à la base de données
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Récupérer les bons de commande du jour (ou de la date spécifiée)
        query = """
        SELECT nomclient, adresse_chantier, formulation, quantite_charge, chauffeur_id 
        FROM bonCommande 
        WHERE date_commande = %s
        """
        cursor.execute(query, (date_rapport,))
        commandes = cursor.fetchall()

        # Générer le PDF
        pdf = PDFx()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Titre du rapport
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, f"Rapport de Production - {date_rapport}", ln=True, align='C')
        pdf.ln(10)

        # Entêtes du tableau
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(200, 220, 255)  # Couleur d'arrière-plan des entêtes
        pdf.cell(40, 10, 'Nom du Client', border=1, fill=True, align='C')
        pdf.cell(50, 10, 'Adresse Chantier', border=1, fill=True, align='C')
        pdf.cell(40, 10, 'Formulation', border=1, fill=True, align='C')
        pdf.cell(30, 10, 'Quantité (cm³)', border=1, fill=True, align='C')
        pdf.cell(40, 10, 'Chauffeur', border=1, fill=True, align='C')
        pdf.ln()
        total_quantite = 0
        # Contenu du tableau
        pdf.set_font('Arial', '', 12)
        for row in commandes:
            pdf.cell(40, 10, row[0], border=1, align='L')  # Nom du client
            pdf.cell(50, 10, row[1], border=1, align='L')  # Adresse chantier
            pdf.cell(40, 10, row[2], border=1, align='L')  # Formulation
            pdf.cell(30, 10, str(row[3]), border=1, align='L')  # Quantité chargée
            pdf.cell(40, 10, str(row[4]), border=1, align='L')  # Chauffeur
            pdf.ln()
            total_quantite += row[3]
         # Ajouter une ligne pour afficher le total
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(160, 10, 'Total de la Production : ', align='R')
        pdf.cell(30, 10, f'{total_quantite} cm³', align='L')
        pdf.ln()    

        # Chemin du fichier PDF
        output_dir = "generated_reports"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        pdf_filename = f"{output_dir}/rapport_{date_rapport}.pdf"
        pdf.output(pdf_filename)

        cursor.close()
        conn.close()

        return jsonify({"message": "Rapport généré avec succès", "pdf_path": pdf_filename}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": f"Erreur SQL : {str(err)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Erreur : {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
