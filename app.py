import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai

# 1. Config IA
genai.configure(api_key=st.secrets["GEMINI_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("🚀 Mon Agent PMO Simple")

# 2. Connexion au Sheets (via l'URL directe)
url = "TON_URL_SHEETS_ICI" # <--- COLLE TON URL ICI
conn = st.connection("gsheets", type=GSheetsConnection)

# Interface
prompt = st.text_input("Que voulez-vous ajouter au projet ?")

if st.button("Ajouter au Sheets"):
    if prompt:
        with st.spinner("L'IA prépare la ligne..."):
            # L'IA formate les données
            response = model.generate_content(f"Transforme en 3 mots séparés par des virgules (Projet, Tâche, Statut) : {prompt}")
            nouvelle_donnee = response.text.split(",")
            
            # Lecture des données actuelles
            df_actuel = conn.read(spreadsheet=url)
            
            # Ajout de la nouvelle ligne (simulation d'écriture)
            st.success(f"L'IA propose d'ajouter : {response.text}")
            st.info("Note : Pour l'écriture directe sans badge, l'IA vous donne le texte prêt à être copié !")
