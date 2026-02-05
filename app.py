import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai

# 1. Config IA
genai.configure(api_key=st.secrets["GEMINI_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("🚀 Mon Agent PMO Simple")

# 2. Connexion au Sheets (via l'URL directe)
url = "https://docs.google.com/spreadsheets/d/1vw-Uzu2axUDawt8tfNVE0aY4OoXiXNhXuWYssysxkaY/edit?usp=sharing" # <--- COLLE TON URL ICI
conn = st.connection("gsheets", type=GSheetsConnection)

# Interface
prompt = st.text_input("Que voulez-vous ajouter au projet ?")

if st.button("Ajouter au Sheets"):
if prompt:
        with st.spinner("L'IA écrit dans le fichier..."):
            # L'IA génère les données structurées
            ai_response = model.generate_content(f"Transforme en 3 colonnes (Projet, Tache, Statut) : {prompt}. Réponds uniquement avec les valeurs séparées par des virgules.")
            new_row = ai_response.text.split(",")
            
            # Lecture des données existantes
            df_actuel = conn.read(spreadsheet=url)
            
            # Création de la nouvelle ligne
            new_data = pd.DataFrame([new_row], columns=df_actuel.columns)
            
            # Fusion et mise à jour réelle du Sheets
            df_final = pd.concat([df_actuel, new_data], ignore_index=True)
            conn.update(spreadsheet=url, data=df_final)
            
            st.success("✅ Ligne ajoutée avec succès dans Google Sheets !")
            st.table(new_data) # Affiche ce qui vient d'être ajouté
