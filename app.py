# =======================
# IMPORTY
# =======================
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =======================
# KONFIGURACJA STRONY
# =======================
st.set_page_config(
    page_title="CT & ALARA – analiza populacyjna",
    layout="wide"
)

# =======================
# TYTUŁ I WSTĘP
# =======================
st.title(
    "Interaktywna analiza populacyjnego narażenia na promieniowanie jonizujące pochodzące z tomografii komputerowej w wybranych krajach\n" 
    "w latach 2005-2019"
)

st.markdown("""
### Dlaczego analizujemy liczbę badań tomografii komputerowej?

Tomografia komputerowa (CT) jest jedną z najczęściej stosowanych metod diagnostyki 
obrazowej, a jednocześnie stanowi **największe źródło dawki efektywnej pochodzącej 
z procedur radiologicznych w populacji**.

Zgodnie z zasadą **ALARA (As Low As Reasonably Achievable)** ekspozycja pacjentów 
na promieniowanie jonizujące powinna być utrzymywana na możliwie najniższym poziomie,
przy zachowaniu jakości diagnostycznej badania.

Celem niniejszej analizy jest:
- Identyfikacji długoterminowych trendów liczby badań CT na 1000 mieszkańców,
- porównanie praktyk diagnostycznych pomiędzy wybranymi krajami,
- wskazanie potencjalnych obszarów wymagających optymalizacji procedur
  w kontekście ochrony radiologicznej populacji.
""")

st.markdown("---")

# =======================
# WCZYTANIE DANYCH
# =======================
df = pd.read_csv("ct_exams_per_1000.csv")

df = df.rename(columns={
    "Reference area": "KRAJ",
    "TIME_PERIOD": "ROK",
    "OBS_VALUE": "LICZBA_CT_NA_1000"
})

df["ROK"] = df["ROK"].astype(int)
df["LICZBA_CT_NA_1000"] = pd.to_numeric(df["LICZBA_CT_NA_1000"], errors="coerce")

mapa_krajow = {
    "Poland": "Polska",
    "Germany": "Niemcy",
    "France": "Francja",
    "United States": "Stany Zjednoczone",
    "United Kingdom": "Wielka Brytania",
    "Italy": "Włochy",
    "Spain": "Hiszpania",
    "Netherlands": "Holandia",
    "Finland": "Finlandia",
    "Japan": "Japonia",
    "Canada": "Kanada",
    "Australia": "Australia"
}

df["KRAJ_PL"] = df["KRAJ"].map(mapa_krajow)
df = df.dropna(subset=["KRAJ_PL", "LICZBA_CT_NA_1000"])

kraje = sorted(df["KRAJ_PL"].unique())


# =======================
# FILTRY GLOBALNE
# =======================
st.subheader("Ustawienia analizy")

c1, c2 = st.columns(2)

with c1:
    wybrane_kraje = st.multiselect(
        "Wybierz kraje",
        kraje,
        default=["Polska", "Niemcy", "Francja"]
    )

with c2:
    zakres_lat = st.slider(
        "Zakres lat",
        int(df["ROK"].min()),
        int(df["ROK"].max()),
        (2005, 2019)
    )

df_filt = df[
    (df["KRAJ_PL"].isin(wybrane_kraje)) &
    (df["ROK"] >= zakres_lat[0]) &
    (df["ROK"] <= zakres_lat[1])
]

# =======================
# PANEL WIDOKU
# =======================
st.markdown("---")
st.subheader("Panel sterowania")

c1, c2, c3 = st.columns(3)

with c1:
    show_trendy = st.checkbox("📈 Trendy CT", True)
    show_stat = st.checkbox("📊 Analiza statystyczna", True)
    show_profil = st.checkbox("🧭 Profil kraju", True)

with c2:
    show_msv = st.checkbox("💡 Dawka populacyjna (mSv)")
    show_head = st.checkbox("⚔️ Porównanie 2 krajów")

with c3:
    show_risk = st.checkbox("🚦 ALARA Risk Score")
    show_export = st.checkbox("⬇️ Eksport CSV")

# =======================
# TRENDY
# =======================
if show_trendy:
    st.markdown("---")
    st.subheader("Trendy CT")

    df_g = (
        df_filt
        .groupby(["KRAJ_PL", "ROK"], as_index=False)
        .agg({"LICZBA_CT_NA_1000": "mean"})
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    for k in wybrane_kraje:
        d = df_g[df_g["KRAJ_PL"] == k]
        ax.plot(d["ROK"], d["LICZBA_CT_NA_1000"], marker="o", label=k)

    ax.set_xlabel("Rok")
    ax.set_ylabel("CT / 1000 mieszkańców")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

# =======================
# STATYSTYKA
# =======================
if show_stat:
    st.markdown("---")
    st.subheader("Analiza statystyczna")

    stat = (
        df_filt
        .groupby("KRAJ_PL")
        .agg(
            ŚREDNIA=("LICZBA_CT_NA_1000", "mean"),
            MIN=("LICZBA_CT_NA_1000", "min"),
            MAX=("LICZBA_CT_NA_1000", "max")
        )
        .round(2)
    )

    st.dataframe(stat)

# =======================
# PROFIL KRAJU
# =======================
if show_profil:
    st.markdown("---")
    st.subheader("Profil kraju")

    kraj_pl = st.selectbox("Wybierz kraj", kraje)

    df_k = (
        df[df["KRAJ_PL"] == kraj_pl]
        .groupby("ROK", as_index=False)
        .agg({"LICZBA_CT_NA_1000": "mean"})
    )

    figp, axp = plt.subplots(figsize=(12, 5))
    axp.plot(df_k["ROK"], df_k["LICZBA_CT_NA_1000"], marker="o")
    axp.set_xlabel("Rok")
    axp.set_ylabel("CT / 1000 mieszkańców")
    axp.grid(True)
    st.pyplot(figp)

# =======================
# DAWKA mSv
# =======================
if show_msv:
    st.markdown("---")
    st.subheader("Hipotetyczna dawka populacyjna")

    dawka = st.slider("Średnia dawka CT [mSv]", 1.0, 20.0, 8.0)

    df_m = (
        df_filt
        .groupby("ROK", as_index=False)
        .agg({"LICZBA_CT_NA_1000": "mean"})
    )

    df_m["DAWKA"] = df_m["LICZBA_CT_NA_1000"] * dawka

    figm, axm = plt.subplots(figsize=(12, 5))
    axm.plot(df_m["ROK"], df_m["DAWKA"], marker="o", color="darkred")
    axm.set_ylabel("mSv / 1000 mieszkańców")
    axm.grid(True)
    st.pyplot(figm)

# =======================
# HEAD-TO-HEAD
# =======================
if show_head:
    st.markdown("---")
    st.subheader("Porównanie dwóch krajów")

    k1 = st.selectbox("Kraj 1", kraje, key="h1")
    k2 = st.selectbox("Kraj 2", kraje, index=1, key="h2")

    d1 = df[df["KRAJ_PL"] == k1].groupby("ROK", as_index=False).agg({"LICZBA_CT_NA_1000": "mean"})
    d2 = df[df["KRAJ_PL"] == k2].groupby("ROK", as_index=False).agg({"LICZBA_CT_NA_1000": "mean"})

    fig2, ax2 = plt.subplots(figsize=(12, 5))
    ax2.plot(d1["ROK"], d1["LICZBA_CT_NA_1000"], marker="o", label=k1)
    ax2.plot(d2["ROK"], d2["LICZBA_CT_NA_1000"], marker="o", label=k2)
    ax2.legend()
    ax2.grid(True)
    st.pyplot(fig2)

# =======================
# ALARA SCORE
# =======================
if show_risk:
    st.markdown("---")
    st.subheader("ALARA Risk Score")

    risk = (
        df_filt
        .groupby("KRAJ_PL")
        .agg(CT=("LICZBA_CT_NA_1000", "mean"))
    )

    risk["ALARA_SCORE"] = (
        (risk["CT"] - risk["CT"].min()) /
        (risk["CT"].max() - risk["CT"].min())
    ).round(3)

    st.dataframe(risk.sort_values("ALARA_SCORE", ascending=False))

# =======================
# EKSPORT
# =======================
if show_export:
    st.markdown("---")
    st.subheader("Eksport danych")

    csv = risk.reset_index().to_csv(index=False).encode("utf-8")
    st.download_button("Pobierz CSV", csv, "alara_score.csv", "text/csv")
