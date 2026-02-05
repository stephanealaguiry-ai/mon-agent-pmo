import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import pandas as pd
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="PMO Assistant 2.5", layout="centered")
st.title("🤖 Mon Agent PMO (Gemini 2.5 Flash)")

# --- VÉRIFICATION DES SECRETS ---
if "connections" not in st.secrets:
    st.error("⚠️ Erreur : La section [connections.gsheets] est manquante dans vos Secrets.")
    st.stop()

# --- INITIALISATION CONNEXION ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- INTERFACE ---
with st.form("pmo_form_25", clear_on_submit=True):
    st.markdown("### 📝 Saisie Intelligente")
    user_input = st.text_input("Détails :", placeholder="Projet, Action, Statut")
    submit = st.form_submit_button("🚀 Envoyer au Sheets")

if submit and user_input:
    try:
        # 1. IA - Configuration pour la version 2.5
        genai.configure(api_key=st.secrets["GEMINI_KEY"])
        
        # Note : Si 'gemini-2.5-flash' renvoie une erreur 404, 
        # vérifiez le nom exact dans AI Studio (ex: 'gemini-2.0-flash-exp')
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        with st.spinner("Gemini 2.5 analyse votre demande..."):
            # Voici le "Cerveau" : le prompt en langage naturel
            instructions = """
            Tu es un assistant PMO expert. Ta mission est d'extraire des informations structurées depuis une phrase libre.
            Tu dois identifier 3 éléments : 
            1. Le Nom du Projet
            2. La Description de la tâche
            3. Le Statut (choisis obligatoirement parmi : À faire, En cours, Terminé, ou En attente)

            Réponds UNIQUEMENT sous la forme d'une seule ligne avec les valeurs séparées par des points-virgules.
            Exemple : Mon Projet;Ma Tâche;En cours
            """
            
            response = model.generate_content(f"{instructions}\n\nTexte de l'utilisateur : {user_input}")
            
            # On nettoie la réponse
            clean_res = response.text.strip().replace("\n", "")
            data_cleaned = clean_res.split(";")
            
            # Sécurité pour s'assurer qu'on a bien nos 3 colonnes
            while len(data_cleaned) < 3:
                data_cleaned.append("Non spécifié")

        with st.spinner("Écriture dans le fichier..."):
            # 2. LECTURE & ÉCRITURE
            url_sheets = st.secrets["GSHEETS_URL"]
            # Lecture fraîche
            df_actuel = conn.read(spreadsheet=url_sheets, ttl=0)
            
            # Création de la ligne avec les noms de colonnes du Sheets
            new_row = pd.DataFrame([data_cleaned], columns=df_actuel.columns[:len(data_cleaned)])
            
            # Fusion
            df_final = pd.concat([df_actuel, new_row], ignore_index=True)
            
            # Mise à jour via Service Account
            conn.update(spreadsheet=url_sheets, data=df_final)
            
            st.success(f"✅ Enregistré (Moteur 2.5) : {data_cleaned[0]}")

    except Exception as e:
        if "404" in str(e):
            st.error(f"❌ Le modèle 'gemini-2.5-flash' n'est pas reconnu. Essayez 'gemini-2.0-flash' ou vérifiez le nom exact dans AI Studio.")
        elif "429" in str(e):
            st.error("⏳ Quota dépassé. Attendez une minute.")
        else:
            st.error(f"Erreur : {e}")

# --- APERÇU ---
st.divider()
if st.checkbox("📊 Afficher le tableau"):
    df_view = conn.read(spreadsheet=st.secrets["GSHEETS_URL"], ttl="1m")
    st.dataframe(df_view, use_container_width=True)
