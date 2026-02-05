import streamlit as st
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials

# 1. Config IA
genai.configure(api_key=st.secrets["GEMINI_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Config Google Sheets
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["GCP_SERVICE_ACCOUNT"], scopes=scope)
client = gspread.authorize(creds)

st.title("🚀 Mon Agent PMO")

# Interface
prompt = st.text_input("Que voulez-vous ajouter au Sheets ?")

if st.button("Ajouter"):
    if prompt:
        with st.spinner("L'IA prépare les données..."):
            # L'IA formate la réponse pour le Sheets
            response = model.generate_content(f"Extrais les infos suivantes du texte : '{prompt}'. Réponds uniquement sous ce format : Projet | Tâche | Statut")
            infos = response.text.split("|")
            
            # Ouverture du fichier et écriture
            sheet = client.open("test_pmo").sheet1
            sheet.append_row([i.strip() for i in infos])
            
            st.success(f"Ajouté avec succès : {response.text}")
