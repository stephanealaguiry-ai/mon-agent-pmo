import streamlit as st
import pandas as pd
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import time

# 1. Configuration de la page
st.set_page_config(page_title="PMO Stabilisé", layout="centered")

st.title("🚀 Mon Agent PMO (Mode Stable)")

# On vérifie que les secrets sont présents pour éviter de lancer l'app dans le vide
if "GEMINI_KEY" not in st.secrets or "GSHEETS_URL" not in st.secrets:
    st.error("⚠️ Les clés API ou l'URL Sheets manquent dans les Secrets de Streamlit.")
    st.stop()

# 2. Interface de saisie
with st.form("pmo_input_form", clear_on_submit=True):
    st.info("Entrez vos infos et cliquez sur Envoyer. L'IA ne s'activera qu'au clic.")
    user_input = st.text_input("Détails (ex: Projet Web, Design Logo, En cours)")
    btn_submit = st.form_submit_button("Envoyer au Sheets")

# 3. Logique d'activation (UNIQUEMENT au clic)
if btn_submit and user_input:
    try:
        # Initialisation de l'IA à l'intérieur du bloc pour économiser le quota
        genai.configure(api_key=st.secrets["GEMINI_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        with st.spinner("1. Analyse par l'IA..."):
            # On force un délai pour calmer les appels successifs
            time.sleep(1)
            prompt_ia = f"Réponds uniquement au format CSV strict (Projet,Tache,Statut) pour ce texte : {user_input}"
            response = model.generate_content(prompt_ia)
            
            # Nettoyage de la réponse IA
            data_raw = response.text.strip().split(",")
            # On s'assure d'avoir exactement 3 éléments, sinon on complète avec du vide
            data_cleaned = [item.strip() for item in data_raw][:3]
            while len(data_cleaned) < 3:
                data_cleaned.append("-")

        with st.spinner("2. Connexion et écriture dans le Sheets..."):
            # Initialisation de la connexion Sheets
            conn = st.connection("gsheets", type=GSheetsConnection)
            
            # Lecture du Sheets (ttl=0 pour être sûr d'avoir la version à jour)
            df_actuel = conn.read(spreadsheet=st.secrets["GSHEETS_URL"], ttl=0)
            
            # Préparation de la nouvelle ligne
            new_row = pd.DataFrame([data_cleaned], columns=df_actuel.columns[:3])
            
            # Fusion
            df_final = pd.concat([df_actuel, new_row], ignore_index=True)
            
            # Envoi vers Google Sheets
            conn.update(spreadsheet=st.secrets["GSHEETS_URL"], data=df_final)
            
            st.success(f"✅ Ajouté : {data_cleaned[0]} | {data_cleaned[1]} | {data_cleaned[2]}")

    except Exception as e:
        if "429" in str(e):
            st.error("⏳ Limite de vitesse Google atteinte. Attendez 60 secondes sans rien toucher.")
        else:
            st.error(f"Une erreur est survenue : {e}")

# Optionnel : bouton séparé pour voir les données (évite de charger le Sheets au démarrage)
if st.button("Voir le contenu du Sheets"):
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_check = conn.read(spreadsheet=st.secrets["GSHEETS_URL"], ttl=0)
    st.dataframe(df_check)
