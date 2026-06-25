import streamlit as st
import random
import unicodedata
import difflib
import os


def normalitza(text):
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


BASE_DIR = os.path.dirname(__file__)

# ----------------------------
# MODE SELECTOR
# ----------------------------
mode = st.selectbox(
    "Select mode",
    ["Premier League", "La Liga", "Totes"]
)


FILES_MAP = {
    "Premier League": ["data/premier_league.txt"],
    "La Liga": ["data/laliga.txt"],
    "Totes": [
        "data/premier_league.txt",
        "data/laliga.txt",
        "data/serieA.txt",
        "data/bundesliga.txt",
        "data/ligue1.txt"
    ]
}

FILES = FILES_MAP[mode]


# ----------------------------
# LOAD PLAYERS
# ----------------------------
jugadors = []

for file in FILES:
    path = os.path.join(BASE_DIR, file)

    if not os.path.exists(path):
        continue

    with open(path, "r", encoding="utf-8") as f:
        for linia in f:
            linia = linia.strip()
            if not linia:
                continue

            dades = linia.replace("–", ";").replace("-", ";").split(";")
            dades = [d.strip() for d in dades]

            if len(dades) != 5:
                continue

            nom, posicio, edat, club, pais = dades

            try:
                edat = int(edat)
            except:
                continue

            jugadors.append({
                "nom": nom,
                "nom_norm": normalitza(nom),
                "posicio": posicio,
                "edat": edat,
                "club": club,
                "pais": pais
            })

if not jugadors:
    st.error("No s'han carregat jugadors")
    st.stop()


# ----------------------------
# SEARCH FUNCTIONS
# ----------------------------
def busca_jugador(entrada):
    entrada = entrada.strip()

    for j in jugadors:
        if entrada == j["nom_norm"]:
            return j
        if entrada in j["nom_norm"]:
            return j
    return None


def suggereix_jugador(entrada_raw):
    entrada_norm = normalitza(entrada_raw)

    noms_norm = [j["nom_norm"] for j in jugadors]

    coincidencies = difflib.get_close_matches(
        entrada_norm,
        noms_norm,
        n=1,
        cutoff=0.6
    )

    if coincidencies:
        for j in jugadors:
            if j["nom_norm"] == coincidencies[0]:
                return j["nom"]
    return None


# ----------------------------
# GAME STATE
# ----------------------------
if "secret" not in st.session_state or st.session_state.get("mode") != mode:
    st.session_state.secret = random.choice(jugadors)
    st.session_state.intents = 0
    st.session_state.historial_data = []
    st.session_state.game_over = False
    st.session_state.mode = mode


secret = st.session_state.secret


# ----------------------------
# UI
# ----------------------------
st.title("⚽ Who Is The Player")
st.write(f"Mode: {mode}")
st.write("Guess the hidden football player")
st.write("You have 8 attempts")


entrada = st.text_input("Enter player")


# ----------------------------
# SUBMIT
# ----------------------------
if st.button("Submit") and not st.session_state.game_over:

    entrada_norm = normalitza(entrada)

    trobat = busca_jugador(entrada_norm)

    if not trobat:
        suggerit = suggereix_jugador(entrada)

        if suggerit:
            st.warning(f"Did you mean: {suggerit}?")
        else:
            st.error("Player not found")
        st.stop()

    st.session_state.intents += 1
    st.session_state.historial_data.append(trobat)

    st.write(trobat["nom"])

    if trobat["club"] == secret["club"]:
        st.success("Same club")
    else:
        st.error("Different club")

    if trobat["pais"] == secret["pais"]:
        st.success("Same country")
    else:
        st.error("Different country")

    if trobat["posicio"] == secret["posicio"]:
        st.success("Same position")
    else:
        st.error("Different position")

    if trobat["edat"] < secret["edat"]:
        st.info("The player is older")
    elif trobat["edat"] > secret["edat"]:
        st.info("The player is younger")
    else:
        st.success("Same age")

    if trobat["nom_norm"] == secret["nom_norm"]:
        st.balloons()
        st.success(f"You guessed it! {secret['nom']}")
        st.session_state.game_over = True

    if st.session_state.intents >= 8:
        st.error(f"You lost. It was {secret['nom']}")
        st.session_state.game_over = True


# ----------------------------
# HISTORY
# ----------------------------
st.write("Guess history")

for i, h in enumerate(st.session_state.historial_data):
    st.write(f"{i+1}: {h['nom']}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("Club")
        st.write("Yes" if h["club"] == secret["club"] else "No")

    with col2:
        st.write("Country")
        st.write("Yes" if h["pais"] == secret["pais"] else "No")

    with col3:
        st.write("Position")
        st.write("Yes" if h["posicio"] == secret["posicio"] else "No")

    st.write("---")


# ----------------------------
# NEW GAME
# ----------------------------
if st.button("New game"):
    st.session_state.secret = random.choice(jugadors)
    st.session_state.intents = 0
    st.session_state.historial_data = []
    st.session_state.game_over = False
    st.rerun()
