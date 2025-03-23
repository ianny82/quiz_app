import streamlit as st
import time
import pandas as pd
import datetime
import os
import json
import random


def main():
    st.set_page_config(page_title="Quiz a Tempo", layout="centered")

    st.title("🧠 Quiz a Tempo")
    st.write("Rispondi a ciascuna domanda e invia. Il tempo di risposta verrà registrato.")
    
    # Inizializzazione delle variabili di stato
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    if 'results' not in st.session_state:
        st.session_state.results = []
    if 'quiz_start_date' not in st.session_state:
        st.session_state.quiz_start_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False
    if 'questions' not in st.session_state:
        genera_domande()

    # Se il quiz è completato
    if st.session_state.quiz_completed:
        mostra_risultati_finali()
        return
    
    # Mostra la domanda corrente
    if st.session_state.current_question_index < len(st.session_state.questions):
        mostra_domanda(st.session_state.questions[st.session_state.current_question_index])
    else:
        salva_risultati_su_file()
        st.session_state.quiz_completed = True
        st.rerun()


def genera_domande():
    domande = []
    coppie = set()

    while len(domande) < 5:  # Puoi aumentare a 20 se vuoi
        a = random.randint(1, 6)
        b = random.randint(1, 10)
        coppia = tuple(sorted((a, b)))
        if coppia not in coppie:
            coppie.add(coppia)
            domande.append({
                "question": f"Quanto fa {a} x {b}?",
                "correct_answer": a * b
            })

    st.session_state.questions = domande


def mostra_domanda(dati_domanda):
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()
    
    st.subheader(f"Domanda {st.session_state.current_question_index + 1}")
    st.write(dati_domanda["question"])
    
    risposta_utente = st.text_area("La tua risposta:", key=f"answer_{st.session_state.current_question_index}")
    
    if st.button("Invia Risposta"):
        end_time = time.time()
        tempo_impiegato = end_time - st.session_state.start_time

        corretta = False
        risposta_corretta = dati_domanda["correct_answer"]

        try:
            risposta_utente_num = float(risposta_utente.strip())
            corretta = risposta_utente_num == float(risposta_corretta)
        except (ValueError, TypeError):
            corretta = False

        risultato = {
            "indice_domanda": st.session_state.current_question_index,
            "domanda": dati_domanda["question"],
            "risposta_utente": risposta_utente,
            "risposta_corretta": risposta_corretta,
            "tempo_impiegato_secondi": round(tempo_impiegato, 2),
            "corretta": corretta
        }

        st.session_state.results.append(risultato)
        st.session_state.current_question_index += 1
        st.session_state.start_time = None
        st.rerun()


def mostra_risultati_finali():
    st.success("🎉 Complimenti! Hai completato il quiz.")
    
    st.subheader("📊 Riepilogo Quiz")
    df = pd.DataFrame(st.session_state.results)

    risposte_corrette = sum(df['corretta'])
    totale_domande = len(df)
    tempo_medio = df['tempo_impiegato_secondi'].mean()

    st.write(f"✅ Punteggio: {risposte_corrette} su {totale_domande}")
    st.write(f"⏱️ Tempo medio per domanda: {tempo_medio:.2f} secondi")

    st.subheader("📋 Dettaglio Risposte")
    for i, risultato in enumerate(st.session_state.results):
        with st.expander(f"Domanda {i+1}"):
            st.write(f"**Domanda:** {risultato['domanda']}")
            st.write(f"**Tua risposta:** {risultato['risposta_utente']}")
            st.write(f"**Risposta corretta:** {risultato['risposta_corretta']}")
            st.write(f"**Tempo impiegato:** {risultato['tempo_impiegato_secondi']} secondi")
            if risultato['corretta']:
                st.success("✅ Corretto")
            else:
                st.error("❌ Errato")

    if st.button("🔄 Ricomincia il Quiz"):
        reset_quiz()
        st.rerun()


def salva_risultati_su_file():
    if not os.path.exists("risultati_quiz"):
        os.makedirs("risultati_quiz")
    
    dati_quiz = {
        "data_quiz": st.session_state.quiz_start_date,
        "numero_domande": len(st.session_state.results),
        "risultati": st.session_state.results
    }

    filename_json = f"risultati_quiz/risultati_{st.session_state.quiz_start_date}.json"
    with open(filename_json, "w") as f:
        json.dump(dati_quiz, f, indent=4)

    df = pd.DataFrame(st.session_state.results)
    filename_csv = f"risultati_quiz/risultati_{st.session_state.quiz_start_date}.csv"
    df.to_csv(filename_csv, index=False)

    st.session_state.saved_filename = filename_json
    return filename_json


def reset_quiz():
    st.session_state.start_time = None
    st.session_state.current_question_index = 0
    st.session_state.results = []
    st.session_state.quiz_start_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    st.session_state.quiz_completed = False
    if 'questions' in st.session_state:
        del st.session_state.questions


if __name__ == "__main__":
    main()