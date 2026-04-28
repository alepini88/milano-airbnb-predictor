import streamlit as st
import joblib
import pandas as pd
import numpy as np

# 1. Carichiamo il "cervello" (modello) e le colonne
model = joblib.load('modello_airbnb.pkl')
features = joblib.load('features.pkl')

st.title("🏠 Airbnb Milano: Suggeritore di Prezzo")
st.write("Inserisci i dettagli del tuo alloggio per sapere a quanto affittarlo.")

# 2. Creiamo i pulsanti e gli slider per l'utente
col1, col2 = st.columns(2)

with col1:
    acc = st.slider("Persone ospitate", 1, 10, 2)
    rooms = st.number_input("Numero stanze", 1, 5, 1)
    dist = st.number_input("Distanza dal Duomo (km)", 0.0, 10.0, 2.0)

with col2:
    bath_per_p = st.number_input("Rapporto Bagni/Persone", 0.1, 1.0, 0.5)
    reviews = st.number_input("Numero di recensioni", 0, 500, 10)
    # Aggiungi qui gli altri input (latitudine, longitudine, ecc.)

# 3. Il tasto magico
if st.button("Calcola Prezzo Ottimale"):
    # Creiamo un dizionario con i dati inseriti dall'utente
    # NOTA: Qui dovrai inserire TUTTE le colonne che il modello si aspetta
    dati_utente = {f: 0 for f in features} # Inizializziamo tutto a zero
    dati_utente['accommodates'] = acc
    dati_utente['distance_from_center'] = dist
    dati_utente['number_of_reviews'] = reviews
    # ... compila tutte le altre variabili ...

    df_input = pd.DataFrame([dati_utente])
    
    # Previsione!
    prezzo = model.predict(df_input)[0]
    
    st.success(f"💰 Il prezzo suggerito per la tua casa è di {prezzo:.2f} € a notte")