import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai

# 1. Config IA
genai.configure(api_key=st.secrets["GEMINI_KEY"])
def get_model():
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            if '1.5-flash' in m.name or 'gemini-pro' in m.name:
                return m.name
    return 'models/gemini-pro' # Repli sécurisé
model_name = get_model()
model = genai.GenerativeModel(model_name)

st.title("🚀 Mon Agent PMO Simple")

# 2. Connexion au Sheets (via l'URL directe)
url = st.secrets["GSHEETS_URL"]
conn = st.connection("gsheets", type=GSheetsConnection)

# Interface
prompt = st.text_input("Que voulez-vous ajouter au projet ?")

if submitted:
    if not prompt:
        st.warning("Veuillez saisir un texte avant de valider.")
    else:
        try:
            with st.spinner("L'IA analyse et écrit dans le Sheets..."):
                # Instruction stricte pour l'IA
                instruction = "Transforme l'info en 3 colonnes séparées par des points-virgules (Projet;Tache;Statut). Ne réponds rien d'autre."
                response = model.generate_content(f"{instruction}\n\nTexte : {prompt}")
                
                # Nettoyage de la réponse
                data_list = response.text.strip().split(";")
                
                # Petite pause pour respecter le quota gratuit (évite l'erreur 429)
                time.sleep(1)

                # Lecture du Sheets actuel
                df_existant = conn.read(spreadsheet=url, ttl=0)
                
                # Vérification que l'IA a bien renvoyé 3 éléments
                if len(data_list) >= 3:
                    # Création de la nouvelle ligne
                    new_row = pd.DataFrame([data_list[:3]], columns=df_existant.columns[:3])
                    
                    # Fusion et Mise à jour
                    df_final = pd.concat([df_existant, new_row], ignore_index=True)
                    conn.update(spreadsheet=url, data=df_final)
                    
                    st.success("✅ Ajouté avec succès dans le Google Sheets !")
                    st.table(new_row)
                else:
                    st.error(f"L'IA a mal formaté la réponse : {response.text}")

        except Exception as e:
            if "429" in str(e):
                st.error("⏳ Quota dépassé : Attendez 60 secondes. L'API gratuite limite la vitesse d'envoi.")
            else:
                st.error(f"Une erreur est survenue : {e}")

# Affichage du tableau actuel pour vérification
if st.checkbox("Afficher le contenu actuel du Sheets"):
    df_visu = conn.read(spreadsheet=url, ttl="10m") # Cache de 10 min pour la lecture
    st.dataframe(df_visu)
