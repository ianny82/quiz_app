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
    
    # Styling textarea height
    st.markdown("""
        <style>
            .element-container textarea {
                height: 60px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Step 1: Ask user how many questions
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False

    if not st.session_state.quiz_started:
        st.subheader("📋 Impostazioni Quiz")
        num_questions = st.number_input("Quante domande vuoi?", min_value=1, max_value=50, value=5, step=1)
        if st.button("Inizia Quiz"):
            st.session_state.num_questions = num_questions
            st.session_state.quiz_started = True
            st.session_state.quiz_start_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            st.session_state.current_question_index = 0
            st.session_state.results = []
            st.session_state.start_time = None
            st.session_state.quiz_completed = False
            genera_domande(num_questions)
            st.rerun()
        return

    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False

    if st.session_state.quiz_completed:
        mostra_risultati_finali()
        return

    if st.session_state.current_question_index < len(st.session_state.questions):
        mostra_domanda(st.session_state.questions[st.session_state.current_question_index])
    else:
        salva_risultati_su_file()
        st.session_state.quiz_completed = True
        st.rerun()


def genera_domande(n):
    domande = []
    coppie = set()
    while len(domande) < n:
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


def custom_keypad_input(question_index):
    st.markdown("### Inserisci la tua risposta:")

    # Keypad state key
    key = f"keypad_{question_index}"
    if key not in st.session_state:
        st.session_state[key] = ""

    # # Display the current input (centered)
    # st.text_input("Risposta corrente:", st.session_state[key], disabled=True, label_visibility="collapsed")

    # Compact display area aligned to the right (calculator-style)
    st.markdown(
        f"""
        <div style="
            font-size: 28px;
            font-weight: bold;
            text-align: right;
            border: 2px solid #ccc;
            border-radius: 8px;
            padding: 6px 12px;
            background-color: #f9f9f9;
            width: 100%;
            max-width: 280px;
            margin: 0 auto 12px auto;
            overflow-x: auto;
            box-sizing: border-box;
        ">
            {st.session_state[key] if st.session_state[key] else "&nbsp;"}
        </div>
        """,
        unsafe_allow_html=True
    )

    # CSS to shrink button spacing and size for mobile
    st.markdown("""
        <style>
            div[data-testid="column"] {
                padding: 2px !important;
            }
            button[kind="secondary"] {
                width: 100% !important;
                padding: 0.75em 0 !important;
                font-size: 18px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Define keypad layout (4 rows, 3 columns)
    layout = [
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"],
        ["C", "0", "←"]
    ]

    for row in layout:
        cols = st.columns(3)
        for i, label in enumerate(row):
            if cols[i].button(label, key=f"{key}_{label}"):
                if label == "C":
                    st.session_state[key] = ""
                elif label == "←":
                    st.session_state[key] = st.session_state[key][:-1]
                else:
                    st.session_state[key] += label
                st.rerun()  # Needed for real-time updates

    # Submit button centered
    submit_col = st.columns([1, 2, 1])[1]
    invia = submit_col.button("✅ Invia", key=f"submit_{question_index}")
    return st.session_state[key], invia


def reset_quiz():
    st.session_state.quiz_started = False
    st.session_state.quiz_completed = False
    st.session_state.questions = []
    st.session_state.current_question_index = 0
    st.session_state.results = []
    st.session_state.start_time = None

    # Remove any stored keypad input
    keys_to_clear = [key for key in st.session_state if key.startswith("keypad_") or key.startswith("submit_")]
    for key in keys_to_clear:
        del st.session_state[key]

def mostra_domanda(dati_domanda):
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    st.subheader(f"Domanda {st.session_state.current_question_index + 1}")
    st.markdown(f"<div style='font-size: 24px; font-weight: bold;'>{dati_domanda['question']}</div>", unsafe_allow_html=True)

    user_input, submitted = custom_keypad_input(st.session_state.current_question_index)

    if submitted:
        end_time = time.time()
        tempo_impiegato = end_time - st.session_state.start_time

        try:
            risposta_num = float(user_input)
            corretta = risposta_num == float(dati_domanda["correct_answer"])
        except:
            corretta = False

        risultato = {
            "Domanda": dati_domanda["question"],
            "Risposta Utente": user_input,
            "Risposta Corretta": dati_domanda["correct_answer"],
            "Corretta": "✅" if corretta else "❌",
            "Tempo (s)": round(tempo_impiegato, 2)
        }

        st.session_state.results.append(risultato)
        st.session_state.current_question_index += 1
        st.session_state.start_time = None
        st.rerun()



def mostra_risultati_finali():
    st.success("🎉 Hai completato il quiz!")

    st.subheader("📊 Risultati Finali")
    df = pd.DataFrame(st.session_state.results)[["Domanda", "Risposta Utente", "Corretta", "Tempo (s)"]]
    st.table(df)

    punteggio = df["Corretta"].value_counts().get("✅", 0)
    st.write(f"✅ Punteggio: {punteggio} su {len(df)}")

    if st.button("🔄 Ricomincia"):
        reset_quiz()
        st.rerun()


def salva_risultati_su_file():
    if not os.path.exists("risultati_quiz"):
        os.makedirs("risultati_quiz")

    filename_base = f"risultati_quiz/risultati_{st.session_state.quiz_start_date}"
    with open(f"{filename_base}.json", "w") as f:
        json.dump(st.session_state.results, f, indent=4)

    pd.DataFrame(st.session_state.results).to_csv(f"{filename_base}.csv", index=False)


def reset_quiz():
    st.session_state.quiz_started = False
    st.session_state.quiz_completed = False
    st.session_state.questions = []
    st.session_state.current_question_index = 0
    st.session_state.results = []
    st.session_state.start_time = None


if __name__ == "__main__":
    main()