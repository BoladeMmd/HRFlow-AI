import os
import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import plotly.express as px
from datetime import date

# =====================================================
# CONFIGURATION
# =====================================================

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="HRFlow AI",
    page_icon="🤖",
    layout="centered"
)

# =====================================================
# STYLE
# =====================================================

st.markdown("""
<style>
.stApp {
    background-color: #f4f7fb;
}

.login-title {
    text-align: center;
    color: #12345a;
    font-size: 36px;
    font-weight: bold;
}

.login-subtitle {
    text-align: center;
    color: #64748b;
    margin-bottom: 30px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# INITIALISATION DE LA SESSION
# =====================================================

if "token" not in st.session_state:
    st.session_state.token = None

if "utilisateur" not in st.session_state:
    st.session_state.utilisateur = None

# =====================================================
# EN-TÊTE
# =====================================================

st.markdown(
    '<p class="login-title">HRFlow AI</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="login-subtitle">Plateforme intelligente de gestion des ressources humaines</p>',
    unsafe_allow_html=True
)

# =====================================================
# CONNEXION
# =====================================================

if st.session_state.token is None:

    with st.form("login_form"):

        username = st.text_input("Nom d'utilisateur")

        password = st.text_input(
            "Mot de passe",
            type="password"
        )

        submitted = st.form_submit_button(
            "Se connecter",
            use_container_width=True
        )

    if submitted:

        if not username or not password:

            st.warning("Veuillez renseigner tous les champs.")

        else:

            try:
                response = requests.post(
                    f"{API_URL}/auth/login",
                    data={
                        "username": username,
                        "password": password
                    },
                    timeout=10
                )

                if response.status_code == 200:

                    resultat = response.json()
                    token = resultat["access_token"]

                    profil = requests.get(
                        f"{API_URL}/auth/me",
                        headers={
                            "Authorization": f"Bearer {token}"
                        },
                        timeout=10
                    )

                    if profil.status_code == 200:

                        st.session_state.token = token
                        st.session_state.utilisateur = profil.json()

                        st.success("Connexion réussie !")
                        st.rerun()

                    else:

                        st.error(
                            "Impossible de récupérer votre profil."
                        )

                elif response.status_code == 401:

                    st.error(
                        "Nom d'utilisateur ou mot de passe incorrect."
                    )

                else:

                    st.error(
                        f"Erreur de connexion : {response.text}"
                    )

            except requests.exceptions.RequestException:

                st.error(
                    "Impossible de contacter le serveur FastAPI."
                )

# =====================================================
# ESPACE UTILISATEUR CONNECTÉ
# =====================================================

else:

    utilisateur = st.session_state.utilisateur
    role = utilisateur.get("role", "").lower()

    headers = {
        "Authorization": f"Bearer {st.session_state.token}"
    }

    st.sidebar.title("HRFlow AI")

    st.sidebar.write(
        f"Bienvenue, {utilisateur.get('username', 'Utilisateur')}"
    )

    # =================================================
    # ESPACE EMPLOYÉ
    # =================================================

    if role in ["employe", "employé"]:

        page = st.sidebar.radio(
            "Navigation",
            [
                "Tableau de bord",
                "Mes demandes",
                "Mes notifications",
                "Mon solde de congés"
            ]
        )

        st.title("Espace Employé")

        # ---------------------------------------------
        # TABLEAU DE BORD
        # ---------------------------------------------

        if page == "Tableau de bord":

            st.subheader("Tableau de bord")

            st.write("Bienvenue dans votre espace personnel.")

            try:
                # Récupération des demandes de l'employé
                response_demandes = requests.get(
                    f"{API_URL}/demandes-absence/mes-demandes",
                    headers=headers,
                    timeout=10
                )

                # Récupération des soldes de congés
                response_soldes = requests.get(
                    f"{API_URL}/soldes-conges/mon-solde",
                    headers=headers,
                    timeout=10
                )

                if response_demandes.status_code == 200 and response_soldes.status_code == 200:

                    demandes = response_demandes.json()
                    soldes = response_soldes.json()

                    # Comptage des demandes selon leur statut
                    en_attente = sum(
                        1 for d in demandes
                        if d["statut"] == "en_attente"
                    )

                    approuvees = sum(
                        1 for d in demandes
                        if d["statut"] == "approuvee"
                    )

                    rejetees = sum(
                        1 for d in demandes
                        if d["statut"] == "rejetee"
                    )

                    # Recherche du solde de l'année en cours
                    annee_actuelle = datetime.now().year

                    solde_actuel = next(
                        (
                            s for s in soldes
                            if s["annee"] == annee_actuelle
                        ),
                        None
                    )

                    solde_disponible = (
                        float(solde_actuel["solde_disponible"])
                        if solde_actuel else 0
                    )

                    # Affichage des indicateurs
                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric("Demandes en attente", en_attente)

                    with col2:
                        st.metric("Demandes approuvées", approuvees)

                    col3, col4 = st.columns(2)

                    with col3:
                        st.metric("Demandes rejetées", rejetees)

                    with col4:
                        st.metric(
                            "Solde disponible",
                            f"{solde_disponible:.2f} jours"
                        )

                else:
                    st.error("Erreur lors de la récupération des données.")

            except requests.exceptions.RequestException as e:
                st.error(f"Impossible de contacter le serveur : {e}")

        # ---------------------------------------------
        # MES DEMANDES
        # ---------------------------------------------

        elif page == "Mes demandes":

            st.subheader("Nouvelle demande d'absence")

            # RÉCUPÉRATION DES TYPES D'ABSENCE

            try:

                types_response = requests.get(
                    f"{API_URL}/types-absence/",
                    headers=headers,
                    timeout=10
                )

                if types_response.status_code == 200:

                    types_absence = types_response.json()

                    if types_absence:

                        types_dict = {
                            type_absence["nom"]: type_absence["id"]
                            for type_absence in types_absence
                        }

                        with st.form("form_demande_absence"):

                            type_nom = st.selectbox(
                                "Type d'absence",
                                options=list(types_dict.keys())
                            )

                            col1, col2 = st.columns(2)

                            with col1:

                                date_debut = st.date_input(
                                    "Date de début"
                                )

                            with col2:

                                date_fin = st.date_input(
                                    "Date de fin"
                                )

                            motif = st.text_area(
                                "Motif de la demande",
                                placeholder=(
                                    "Expliquez le motif de votre absence..."
                                )
                            )

                            envoyer = st.form_submit_button(
                                "Soumettre ma demande"
                            )

                            if envoyer:

                                if date_fin < date_debut:

                                    st.error(
                                        "La date de fin doit être "
                                        "postérieure ou égale à "
                                        "la date de début."
                                    )

                                elif len(motif.strip()) < 3:

                                    st.error(
                                        "Veuillez saisir un motif "
                                        "d'au moins 3 caractères."
                                    )

                                else:

                                    payload = {
                                        "type_absence_id": types_dict[type_nom],
                                        "date_debut": date_debut.isoformat(),
                                        "date_fin": date_fin.isoformat(),
                                        "motif": motif.strip()
                                    }

                                    response = requests.post(
                                        f"{API_URL}/demandes-absence/",
                                        json=payload,
                                        headers=headers,
                                        timeout=10
                                    )

                                    if response.status_code in [200, 201]:

                                        st.success(
                                            "Votre demande a été "
                                            "envoyée avec succès !"
                                        )

                                        st.rerun()

                                    else:

                                        st.error(
                                            f"Erreur : {response.text}"
                                        )

                    else:

                        st.info(
                            "Aucun type d'absence disponible."
                        )

                else:

                    st.error(
                        "Impossible de récupérer les types : "
                        f"{types_response.text}"
                    )

            except requests.exceptions.RequestException as e:

                st.error(
                    f"Erreur de connexion à l'API : {e}"
                )

            # -----------------------------------------
            # HISTORIQUE DES DEMANDES
            # -----------------------------------------

            st.divider()

            st.subheader("Mes demandes d'absence")

            try:

                response = requests.get(
                    f"{API_URL}/demandes-absence/mes-demandes",
                    headers=headers,
                    timeout=10
                )

                if response.status_code == 200:

                    demandes = response.json()

                    # RÉCUPÉRATION DES NOMS DES TYPES

                    types_response = requests.get(
                        f"{API_URL}/types-absence/",
                        headers=headers,
                        timeout=10
                    )

                    types_dict = {}

                    if types_response.status_code == 200:

                        types_absence = types_response.json()

                        types_dict = {
                            type_absence["id"]: type_absence["nom"]
                            for type_absence in types_absence
                        }

                    if not demandes:

                        st.info(
                            "Vous n'avez encore soumis aucune demande."
                        )

                    else:

                        st.metric(
                            "Nombre total de demandes",
                            len(demandes)
                        )

                        for demande in demandes:

                            with st.container(border=True):

                                st.write(
                                    f"**Demande N° {demande['id']}**"
                                )

                                nom_type = types_dict.get(
                                    demande["type_absence_id"],
                                    "Type inconnu"
                                )

                                st.write(
                                    f"Type d'absence : {nom_type}"
                                )

                                st.write(
                                    f"Date de début : {demande['date_debut']}"
                                )

                                st.write(
                                    f"Date de fin : {demande['date_fin']}"
                                )

                                statut = demande["statut"]

                                if statut == "approuvee":

                                    st.success("Demande approuvée")

                                elif statut == "rejetee":

                                    st.error("Demande rejetée")

                                else:

                                    st.warning(
                                        "En attente de validation"
                                    )

                else:

                    st.error(
                        f"Erreur API : {response.text}"
                    )

            except requests.exceptions.RequestException:

                st.error(
                    "Impossible de contacter le serveur."
                )

        # ---------------------------------------------
        # MES NOTIFICATIONS
        # ---------------------------------------------

        elif page == "Mes notifications":

            st.subheader("Mes notifications")

            try:

                response = requests.get(
                    f"{API_URL}/notifications/mes-notifications",
                    headers=headers,
                    timeout=10
                )

                if response.status_code == 200:

                    notifications = response.json()

                    non_lues = sum(
                        1 for n in notifications if not n["lu"]
                    )

                    st.metric(
                        "Notifications non lues",
                        non_lues
                    )

                    if not notifications:

                        st.info(
                            "Vous n'avez aucune notification."
                        )

                    for notification in notifications:

                        with st.container(border=True):

                            st.write(
                                f"**{notification['titre']}**"
                            )

                            st.write(
                                notification["message"]
                            )

                            if notification["lu"]:

                                st.caption("Déjà lue")

                            else:

                                st.caption("Non lue")

                                if st.button(
                                    "Marquer comme lue",
                                    key=f"lire_{notification['id']}"
                                ):

                                    resultat = requests.patch(
                                        f"{API_URL}/notifications/{notification['id']}/lire",
                                        headers=headers,
                                        timeout=10
                                    )

                                    if resultat.status_code == 200:

                                        st.success(
                                            "Notification marquée comme lue."
                                        )

                                        st.rerun()

                                    else:

                                        st.error(
                                            f"Erreur : {resultat.text}"
                                        )

                else:

                    st.error(
                        f"Erreur API : {response.text}"
                    )

            except requests.exceptions.RequestException:

                st.error(
                    "Impossible de contacter le serveur."
                )

        # ---------------------------------------------
        # MON SOLDE DE CONGÉS
        # ---------------------------------------------

        
        elif page == "Mon solde de congés":

            st.subheader("Mon solde de congés")

            try:
                response = requests.get(
                    f"{API_URL}/soldes-conges/mon-solde",
                    headers=headers,
                    timeout=10
                )

                if response.status_code == 200:

                    soldes = response.json()

                    if not soldes:
                        st.info("Aucun solde de congés disponible.")

                    else:
                        # Afficher les soldes par année
                        for solde in sorted(
                            soldes,
                            key=lambda x: x["annee"],
                            reverse=True
                        ):

                            st.markdown(
                                f"### Année {solde['annee']}"
                            )

                            col1, col2, col3 = st.columns(3)

                            with col1:
                                st.metric(
                                    "Solde initial",
                                    f"{float(solde['solde_initial']):.2f} jours"
                                )

                            with col2:
                                st.metric(
                                    "Jours acquis",
                                    f"{float(solde['jours_acquis']):.2f} jours"
                                )

                            with col3:
                                st.metric(
                                    "Jours reportés",
                                    f"{float(solde['solde_reporte']):.2f} jours"
                                )

                            col4, col5 = st.columns(2)

                            with col4:
                                st.metric(
                                    "Jours pris",
                                    f"{float(solde['jours_pris']):.2f} jours"
                                )

                            with col5:
                                st.metric(
                                    "Solde disponible",
                                    f"{float(solde['solde_disponible']):.2f} jours"
                                )

                            st.divider()

                else:
                    st.error(
                        f"Erreur API : {response.text}"
                    )

            except requests.exceptions.RequestException as e:
                st.error(
                    f"Impossible de contacter le serveur : {e}"
                )


    
    
    # =================================================
    # ESPACE RESPONSABLE
    # =================================================

    elif role == "responsable":

        page = st.sidebar.radio(
            "Navigation",
            [
                "Tableau de bord",
                "Demandes à valider",
                "Suivi du personnel",
                "Rapports",
                "Assistant IA RH"
            ]
        )

        st.title("Espace Responsable")

        # ---------------------------------------------
        # TABLEAU DE BORD
        # ---------------------------------------------

        if page == "Tableau de bord":
            st.title("Tableau de bord Responsable RH")
            st.caption("Vue générale du suivi des absences et des validations")

            headers = {"Authorization": f"Bearer {st.session_state.token}"}

            try:
                rep_employes = requests.get(
                    f"{API_URL}/employes/",
                    headers=headers,
                    timeout=10
                )

                rep_demandes = requests.get(
                    f"{API_URL}/demandes-absence/",
                    headers=headers,
                    timeout=10
                )

                if rep_employes.status_code == 200 and rep_demandes.status_code == 200:

                    employes = rep_employes.json()
                    demandes = rep_demandes.json()

                    employes_actifs = sum(
                        1 for e in employes if e["statut"] == "actif"
                    )

                    en_attente = sum(
                        1 for d in demandes if d["statut"] == "en_attente"
                    )

                    approuvees = sum(
                        1 for d in demandes if d["statut"] == "approuvee"
                    )

                    rejetees = sum(
                        1 for d in demandes if d["statut"] == "rejetee"
                    )

                    st.subheader("Vue d'ensemble")

                    col1, col2, col3, col4 = st.columns(4)

                    col1.metric("Employés actifs", employes_actifs)
                    col2.metric("En attente", en_attente)
                    col3.metric("Approuvées", approuvees)
                    col4.metric("Rejetées", rejetees)

                    st.divider()

                    st.subheader("Demandes récemment soumises")

                    if demandes:
                        df = pd.DataFrame(demandes)

                        df["date_debut"] = pd.to_datetime(
                            df["date_debut"]
                        ).dt.strftime("%d/%m/%Y")

                        df["date_fin"] = pd.to_datetime(
                            df["date_fin"]
                        ).dt.strftime("%d/%m/%Y")

                        st.dataframe(
                            df[[
                                "id",
                                "employe_id",
                                "type_absence_id",
                                "date_debut",
                                "date_fin",
                                "nombre_jours",
                                "statut"
                            ]].head(10),
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("Aucune demande d'absence enregistrée.")

                else:
                    st.error("Impossible de récupérer les données du tableau de bord.")

            except requests.exceptions.RequestException as e:
                st.error(f"Erreur de connexion à l'API : {e}")

        # ---------------------------------------------
        # DEMANDES À VALIDER
        # ---------------------------------------------

        elif page == "Demandes à valider":

            st.subheader("Demandes d'absence en attente")

            try:
                response = requests.get(
                    f"{API_URL}/validations/demandes-en-attente",
                    headers=headers,
                    timeout=10
                )

                if response.status_code == 200:

                    demandes = response.json()

                    if not demandes:
                        st.info("Aucune demande en attente.")

                    else:
                        st.metric("Demandes à traiter", len(demandes))

                        # Récupération des types d'absence
                        types_response = requests.get(
                            f"{API_URL}/types-absence/",
                            headers=headers,
                            timeout=10
                        )

                        types_dict = {}

                        if types_response.status_code == 200:
                            types_dict = {
                                t["id"]: t["nom"]
                                for t in types_response.json()
                            }

                        # Affichage des demandes
                        for demande in demandes:

                            with st.container(border=True):

                                st.markdown(
                                    f"### Demande N° {demande['id']}"
                                )

                                st.write(
                                    f"**Employé ID :** {demande['employe_id']}"
                                )

                                st.write(
                                    f"**Type :** {types_dict.get(demande['type_absence_id'], 'Inconnu')}"
                                )

                                st.write(
                                    f"**Période :** {demande['date_debut']} au {demande['date_fin']}"
                                )

                                st.write(
                                    f"**Nombre de jours :** {demande['nombre_jours']}"
                                )

                                st.write(
                                    f"**Motif :** {demande.get('motif') or 'Non renseigné'}"
                                )

                                commentaire = st.text_area(
                                    "Commentaire du responsable",
                                    key=f"commentaire_{demande['id']}"
                                )

                                col1, col2 = st.columns(2)

                                with col1:
                                    approuver = st.button(
                                        "Approuver",
                                        key=f"approuver_{demande['id']}",
                                        use_container_width=True
                                    )

                                with col2:
                                    rejeter = st.button(
                                        "Rejeter",
                                        key=f"rejeter_{demande['id']}",
                                        use_container_width=True
                                    )

                                if approuver or rejeter:

                                    payload = {
                                        "decision": (
                                            "approuvee"
                                            if approuver else "rejetee"
                                        ),
                                        "commentaire": commentaire.strip()
                                    }

                                    try:
                                        resultat = requests.post(
                                            f"{API_URL}/validations/{demande['id']}",
                                            json=payload,
                                            headers=headers,
                                            timeout=10
                                        )

                                        if resultat.status_code in [200, 201]:
                                            st.success(
                                                "Décision enregistrée avec succès."
                                            )
                                            st.rerun()

                                        else:
                                            st.error(
                                                f"Erreur API : {resultat.text}"
                                            )

                                    except requests.exceptions.RequestException as e:
                                        st.error(
                                            f"Erreur de connexion : {e}"
                                        )

                else:
                    st.error(f"Erreur API : {response.text}")

            except requests.exceptions.RequestException as e:
                st.error(
                    f"Impossible de contacter le serveur : {e}"
                )

        # ---------------------------------------------
        # SUIVI DU PERSONNEL
        # ---------------------------------------------

        elif page == "Suivi du personnel":

            st.subheader("Suivi du personnel")

            try:
                response = requests.get(
                    f"{API_URL}/employes/",
                    headers=headers,
                    timeout=10
                )

                if response.status_code == 200:

                    employes = response.json()

                    if not employes:
                        st.info("Aucun employé enregistré.")

                    else:
                        # Indicateurs
                        total = len(employes)

                        actifs = sum(
                            1 for e in employes
                            if e["statut"] == "actif"
                        )

                        inactifs = total - actifs

                        col1, col2, col3 = st.columns(3)

                        col1.metric("Total employés", total)
                        col2.metric("Employés actifs", actifs)
                        col3.metric("Employés inactifs", inactifs)

                        st.divider()

                        # Recherche
                        recherche = st.text_input(
                            "Rechercher par nom ou matricule",
                            placeholder="Exemple : Moussa ou IT001"
                        )

                        # Filtre par statut
                        statut_filtre = st.selectbox(
                            "Filtrer par statut",
                            ["Tous", "actif", "inactif"]
                        )

                        employes_filtres = employes

                        if recherche:
                            employes_filtres = [
                                e for e in employes_filtres
                                if recherche.lower() in (
                                    f"{e['prenom']} {e['nom']} {e['matricule']}"
                                ).lower()
                            ]

                        if statut_filtre != "Tous":
                            employes_filtres = [
                                e for e in employes_filtres
                                if e["statut"] == statut_filtre
                            ]

                        st.write(
                            f"**{len(employes_filtres)} employé(s) trouvé(s)**"
                        )

                        # Affichage des employés
                        for employe in employes_filtres:

                            with st.container(border=True):

                                st.markdown(
                                    f"### {employe['prenom']} {employe['nom']}"
                                )

                                col1, col2 = st.columns(2)

                                with col1:
                                    st.write(
                                        f"**Matricule :** {employe['matricule']}"
                                    )

                                    st.write(
                                        f"**Poste :** {employe['poste']}"
                                    )

                                    st.write(
                                        f"**Département ID :** {employe['departement_id']}"
                                    )

                                with col2:
                                    st.write(
                                        f"**Email :** {employe['email']}"
                                    )

                                    st.write(
                                        f"**Date d'embauche :** {employe['date_embauche']}"
                                    )

                                    st.write(
                                        f"**Statut :** {employe['statut']}"
                                    )

                else:
                    st.error(f"Erreur API : {response.text}")

            except requests.exceptions.RequestException as e:
                st.error(
                    f"Impossible de contacter le serveur : {e}"
                )

            
        # ---------------------------------------------
        # RAPPORTS RH
        # ---------------------------------------------

        elif page == "Rapports":

            st.title("Rapports et statistiques RH")

            # Récupération des données
            try:
                rep_demandes = requests.get(
                    f"{API_URL}/demandes-absence/",
                    headers=headers,
                    timeout=10
                )

                rep_employes = requests.get(
                    f"{API_URL}/employes/",
                    headers=headers,
                    timeout=10
                )

                rep_departements = requests.get(
                    f"{API_URL}/departements/",
                    headers=headers,
                    timeout=10
                )

                rep_types = requests.get(
                    f"{API_URL}/types-absence/",
                    headers=headers,
                    timeout=10
                )

                if all(r.status_code == 200 for r in [
                    rep_demandes,
                    rep_employes,
                    rep_departements,
                    rep_types
                ]):

                    demandes = rep_demandes.json()
                    employes = rep_employes.json()
                    departements = rep_departements.json()
                    types = rep_types.json()

                    if demandes:

                        df = pd.DataFrame(demandes)

                        employes_dict = {
                            e["id"]: e for e in employes
                        }

                        departements_dict = {
                            d["id"]: d["nom"]
                            for d in departements
                        }

                        types_dict = {
                            t["id"]: t["nom"]
                            for t in types
                        }

                        df["Employé"] = df["employe_id"].map(
                            lambda x: (
                                f"{employes_dict[x]['prenom']} "
                                f"{employes_dict[x]['nom']}"
                            ) if x in employes_dict else "Inconnu"
                        )

                        df["Département"] = df["employe_id"].map(
                            lambda x: departements_dict.get(
                                employes_dict[x].get("departement_id"),
                                "Non renseigné"
                            ) if x in employes_dict else "Non renseigné"
                        )

                        df["Type d'absence"] = df["type_absence_id"].map(
                            lambda x: types_dict.get(x, "Inconnu")
                        )

                        df["Date"] = pd.to_datetime(
                            df["date_debut"], errors="coerce"
                        )

                        df["Nombre de jours"] = pd.to_numeric(
                            df["nombre_jours"], errors="coerce"
                        ).fillna(0)

                        # Filtres
                        st.subheader("Filtres")

                        col1, col2 = st.columns(2)

                        with col1:
                            statuts = ["Tous"] + sorted(
                                df["statut"].dropna().unique().tolist()
                            )
                            statut = st.selectbox(
                                "Statut",
                                statuts,
                                key="responsable_statut"
                            )

                        with col2:
                            annees = sorted(
                                df["Date"].dropna().dt.year.unique().tolist(),
                                reverse=True
                            )
                            annee = st.selectbox(
                                "Année",
                                ["Toutes"] + annees,
                                key="responsable_annee"
                            )

                        df_filtre = df.copy()

                        if statut != "Tous":
                            df_filtre = df_filtre[
                                df_filtre["statut"] == statut
                            ]

                        if annee != "Toutes":
                            df_filtre = df_filtre[
                                df_filtre["Date"].dt.year == annee
                            ]

                        # Indicateurs
                        st.divider()
                        st.subheader("Indicateurs clés")

                        col1, col2, col3, col4 = st.columns(4)

                        col1.metric("Total demandes", len(df_filtre))
                        col2.metric(
                            "En attente",
                            (df_filtre["statut"] == "en_attente").sum()
                        )
                        col3.metric(
                            "Approuvées",
                            (df_filtre["statut"] == "approuvee").sum()
                        )
                        col4.metric(
                            "Rejetées",
                            (df_filtre["statut"] == "rejetee").sum()
                        )

                        # Demandes par type
                        st.divider()
                        st.subheader("Demandes par type d'absence")

                        par_type = (
                            df_filtre.groupby("Type d'absence")
                            .size()
                            .reset_index(name="Nombre de demandes")
                        )

                        fig_type = px.pie(
                            par_type,
                            names="Type d'absence",
                            values="Nombre de demandes",
                            hole=0.4
                        )

                        st.plotly_chart(
                            fig_type,
                            use_container_width=True
                        )

                        # Évolution mensuelle
                        st.subheader("Évolution mensuelle")

                        df_mois = df_filtre.dropna(
                            subset=["Date"]
                        ).copy()

                        if not df_mois.empty:
                            df_mois["Mois"] = (
                                df_mois["Date"].dt.to_period("M").astype(str)
                            )

                            evolution = (
                                df_mois.groupby("Mois")
                                .size()
                                .reset_index(name="Nombre de demandes")
                                .sort_values("Mois")
                            )

                            fig_mois = px.line(
                                evolution,
                                x="Mois",
                                y="Nombre de demandes",
                                markers=True
                            )

                            st.plotly_chart(
                                fig_mois,
                                use_container_width=True
                            )

                        
                        
                        # Nombre d'absences par département
                        st.subheader("Nombre d'absences par département")

                        par_departement = (
                            df_filtre[df_filtre["statut"] == "approuvee"]
                            .groupby("Département")
                            .size()
                            .reset_index(name="Nombre d'absences")
                            .sort_values("Nombre d'absences", ascending=False)
                        )

                        if not par_departement.empty:

                            fig_departement = px.bar(
                                par_departement,
                                x="Département",
                                y="Nombre d'absences",
                                text="Nombre d'absences",
                                color="Département",
                                title="Répartition des absences approuvées par département"
                            )

                            fig_departement.update_layout(
                                xaxis_title="Départements",
                                yaxis_title="Nombre d'absences",
                                showlegend=False
                            )

                            st.plotly_chart(
                                fig_departement,
                                use_container_width=True
                            )

                        else:
                            st.info("Aucune absence approuvée pour cette période.")

                        # Nombre total de jours d'absence approuvés par département
                        st.subheader("Nombre de jours d'absence approuvés par département")

                        jours_par_departement = (
                            df_filtre[df_filtre["statut"] == "approuvee"]
                            .groupby("Département")["Nombre de jours"]
                            .sum()
                            .reset_index()
                            .sort_values("Nombre de jours", ascending=False)
                        )

                        if not jours_par_departement.empty:
                            fig_jours = px.bar(
                                jours_par_departement,
                                x="Département",
                                y="Nombre de jours",
                                text="Nombre de jours",
                                color="Département",
                                title="Total des jours d'absence approuvés par département"
                            )

                            fig_jours.update_layout(
                                xaxis_title="Départements",
                                yaxis_title="Nombre de jours",
                                showlegend=False
                            )

                            st.plotly_chart(fig_jours, use_container_width=True)
                        else:
                            st.info("Aucun jour d'absence approuvé pour cette période.")

                        # Jours demandés par employé
                        st.subheader("Jours demandés par employé")

                        par_employe = (
                            df_filtre.groupby("Employé")["Nombre de jours"]
                            .sum()
                            .reset_index()
                            .sort_values(
                                "Nombre de jours",
                                ascending=False
                            )
                        )

                        fig_employe = px.bar(
                            par_employe,
                            x="Employé",
                            y="Nombre de jours"
                        )

                        st.plotly_chart(
                            fig_employe,
                            use_container_width=True
                        )

                    else:
                        st.info("Aucune demande disponible.")

                else:
                    st.error("Erreur lors de la récupération des données.")

            except requests.exceptions.RequestException as e:
                st.error(f"Erreur de connexion : {e}")

        # =================================================
        # ASSISTANT ANALYSE RH
        # =================================================
        
        
        elif page == "Assistant IA RH":
            import re

            st.title("🤖 Assistant IA RH")

            st.markdown("""
            Posez vos questions sur les absences et les congés du personnel.
            HRFlow AI analyse les données et vous propose des explications
            et des recommandations.
            """)

            st.divider()

            if "historique_assistant_rh" not in st.session_state:
                st.session_state.historique_assistant_rh = []

            # Configuration des graphiques
            configurations = {
                "analyser_par_departement": {
                    "x": "total_jours",
                    "y": "departement",
                    "titre": "Jours d'absence par département",
                    "couleur": "#2563EB",
                    "axe": "Nombre de jours"
                },
                "analyser_par_type": {
                    "x": "nombre_demandes",
                    "y": "type_absence",
                    "titre": "Demandes par type d'absence",
                    "couleur": "#0D9488",
                    "axe": "Nombre de demandes"
                },
                "analyser_par_statut": {
                    "x": "nombre",
                    "y": "statut",
                    "titre": "Demandes par statut",
                    "couleur": "#7C3AED",
                    "axe": "Nombre de demandes"
                },
                "classer_employes_par_absences": {
                    "x": "total_jours",
                    "y": "nom_complet",
                    "titre": "Jours d'absence par employé",
                    "couleur": "#D97706",
                    "axe": "Nombre de jours"
                },
                "analyser_evolution_mensuelle_rh": {
                    "x": "mois",
                    "y": "nombre_demandes",
                    "titre": "Évolution mensuelle des demandes d'absence",
                    "axe_x": "Mois",
                    "axe_y": "Nombre de demandes"
                },
            }

            # Fonction unique d'affichage des graphiques
            
            def afficher_graphique(graphique, cle_unique):

                if not graphique or not graphique.get("donnees"):
                    return

                df = pd.DataFrame(graphique["donnees"])
                config = configurations.get(graphique.get("outil"))

                if not config:
                    return

                x = config["x"]
                y = config["y"]

                if x not in df.columns or y not in df.columns:
                    return

                type_graphique = graphique.get("type")

                # =========================
                # GRAPHIQUE CIRCULAIRE
                # =========================
                if type_graphique == "pie":

                    df[x] = pd.to_numeric(df[x], errors="coerce")
                    df = df.dropna(subset=[x, y])

                    if df.empty:
                        return

                    fig = px.pie(
                        df,
                        names=y,
                        values=x,
                        title=config["titre"],
                        color_discrete_sequence=[
                            "#0D9488", "#2563EB", "#F59E0B", "#7C3AED"
                        ]
                    )

                    fig.update_traces(
                        textposition="inside",
                        textinfo="percent+label"
                    )

                # =========================
                # GRAPHIQUE D'ÉVOLUTION
                # =========================
                elif type_graphique == "line":

                    df[y] = pd.to_numeric(df[y], errors="coerce")
                    df = df.dropna(subset=[x, y])
                    df = df.sort_values(x, ascending=True)

                    if df.empty:
                        return

                    fig = px.line(
                        df,
                        x=x,
                        y=y,
                        markers=True,
                        title=config["titre"],
                        labels={
                            x: config.get("axe_x", "Mois"),
                            y: config.get("axe_y", "Nombre de demandes")
                        },
                        color_discrete_sequence=["#0D9488"]
                    )

                    fig.update_traces(
                        line=dict(width=3),
                        marker=dict(size=8)
                    )

                # =========================
                # GRAPHIQUE EN BARRES
                # =========================
                else:

                    df[x] = pd.to_numeric(df[x], errors="coerce")
                    df = df.dropna(subset=[x, y])
                    df = df.sort_values(x, ascending=True)

                    if df.empty:
                        return

                    fig = px.bar(
                        df,
                        x=x,
                        y=y,
                        orientation="h",
                        title=config["titre"],
                        text=x,
                        color_discrete_sequence=[config["couleur"]]
                    )

                    fig.update_traces(
                        texttemplate="%{text:.1f}",
                        textposition="outside",
                        marker_line_width=0,
                        cliponaxis=False
                    )

                # =========================
                # MISE EN FORME COMMUNE
                # =========================
                fig.update_layout(
                    height=max(350, len(df) * 65),
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    font=dict(family="Arial", size=13, color="#1E293B"),
                    title=dict(
                        font=dict(size=19, color="#0F172A"),
                        x=0.02
                    ),
                    showlegend=False,
                    margin=dict(l=15, r=45, t=70, b=45)
                )

                if type_graphique == "line":
                    fig.update_layout(
                        xaxis=dict(
                            title=config.get("axe_x", "Mois"),
                            showgrid=True,
                            gridcolor="#E2E8F0"
                        ),
                        yaxis=dict(
                            title=config.get("axe_y", "Nombre de demandes"),
                            showgrid=True,
                            gridcolor="#E2E8F0",
                            zeroline=False
                        )
                    )
                else:
                    fig.update_layout(
                        xaxis=dict(
                            title=config.get("axe", ""),
                            showgrid=True,
                            gridcolor="#E2E8F0",
                            zeroline=False
                        ),
                        yaxis=dict(
                            title="",
                            showgrid=False
                        )
                    )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": False},
                    key=cle_unique
                )

            # Affichage unique de toute la conversation
            for index, message in enumerate(
                st.session_state.historique_assistant_rh
            ):

                with st.chat_message(message["role"]):

                    st.markdown(message["content"])

                    if message["role"] == "assistant":
                        afficher_graphique(
                            message.get("graphique"),
                            cle_unique=f"graphique_rh_{index}"
                        )

            # Zone de saisie
            question = st.chat_input(
                "Posez votre question au Responsable RH..."
            )

            if question:

                st.session_state.historique_assistant_rh.append({
                    "role": "user",
                    "content": question
                })

                with st.spinner("HRFlow AI analyse votre question..."):

                    try:
                        headers = {
                            "Authorization": f"Bearer {st.session_state.token}"
                        }

                        response = requests.post(
                            f"{API_URL}/assistant-rh/question",
                            json={"question": question},
                            headers=headers,
                            timeout=120
                        )

                        if response.status_code == 200:

                            resultat = response.json()
                            reponse = resultat["reponse"]
                            graphique = resultat.get("graphique")

                            # Suppression du graphique ASCII du texte
                            reponse = re.sub(
                                r"### Graphique.*?(?=##|\Z)",
                                "",
                                reponse,
                                flags=re.DOTALL | re.IGNORECASE
                            )

                            st.session_state.historique_assistant_rh.append({
                                "role": "assistant",
                                "content": reponse,
                                "graphique": graphique
                            })

                            # Réaffichage unique depuis l'historique
                            st.rerun()

                        else:
                            st.error(
                                f"Erreur API ({response.status_code}) : "
                                f"{response.text}"
                            )

                    except requests.exceptions.Timeout:
                        st.error("L'assistant met trop de temps à répondre.")

                    except requests.exceptions.RequestException as e:
                        st.error(f"Erreur de connexion au serveur : {e}")

      
    
    # =================================================
    # ESPACE ADMIN RH
    # =================================================

    elif role == "admin_rh":

        page = st.sidebar.radio(
            "Navigation",
            [
                "Tableau de bord",
                "Employés",
                "Départements",
                "Demandes",
                "Rapports"
            ]
        )

        st.title("Administration RH")

        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }

        # =================================================
        # 1. TABLEAU DE BORD
        # =================================================

        
        if page == "Tableau de bord":
            st.title("Tableau de bord Administrateur RH")
            st.caption("Vue générale de la gestion des ressources humaines")

            headers = {
                "Authorization": f"Bearer {st.session_state.token}"
            }

            try:
                rep_employes = requests.get(
                    f"{API_URL}/employes/",
                    headers=headers,
                    timeout=10
                )

                rep_demandes = requests.get(
                    f"{API_URL}/demandes-absence/",
                    headers=headers,
                    timeout=10
                )

                if rep_employes.status_code == 200 and rep_demandes.status_code == 200:

                    employes = rep_employes.json()
                    demandes = rep_demandes.json()

                    total_employes = len(employes)

                    employes_actifs = sum(
                        1 for e in employes if e["statut"] == "actif"
                    )

                    employes_inactifs = total_employes - employes_actifs

                    total_demandes = len(demandes)

                    en_attente = sum(
                        1 for d in demandes if d["statut"] == "en_attente"
                    )

                    approuvees = sum(
                        1 for d in demandes if d["statut"] == "approuvee"
                    )

                    rejetees = sum(
                        1 for d in demandes if d["statut"] == "rejetee"
                    )

                    st.subheader("Effectif du personnel")

                    col1, col2, col3 = st.columns(3)

                    col1.metric("Effectif total", total_employes)
                    col2.metric("Employés actifs", employes_actifs)
                    col3.metric("Employés inactifs", employes_inactifs)

                    st.divider()

                    st.subheader("Suivi des demandes d'absence")

                    col1, col2, col3, col4 = st.columns(4)

                    col1.metric("Total demandes", total_demandes)
                    col2.metric("En attente", en_attente)
                    col3.metric("Approuvées", approuvees)
                    col4.metric("Rejetées", rejetees)

                else:
                    st.error("Impossible de récupérer les données du tableau de bord.")

            except requests.exceptions.RequestException as e:
                st.error(f"Erreur de connexion à l'API : {e}")


        
        # =================================================
        # 2. GESTION DES EMPLOYES
        # =================================================

        elif page == "Employés":

            st.subheader("Gestion des employés")

            response = requests.get(
                f"{API_URL}/employes/",
                headers=headers
            )

            if response.status_code == 200:

                employes = response.json()

                # =========================================
                # AFFICHAGE DE LA LISTE DES EMPLOYES
                # =========================================

                if employes:

                    df = pd.DataFrame(employes)

                    st.metric(
                        "Nombre total d'employés",
                        len(df)
                    )

                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )

                else:

                    st.info("Aucun employé enregistré.")

                # =========================================
                # RECUPERATION DES DEPARTEMENTS
                # =========================================

                dep_response = requests.get(
                    f"{API_URL}/departements/",
                    headers=headers
                )

                if dep_response.status_code == 200:

                    departements = dep_response.json()

                    dep_options = {
                        f"{dep['nom']} (ID: {dep['id']})": dep["id"]
                        for dep in departements
                    }

                    if dep_options:

                        # =================================
                        # FORMULAIRE D'AJOUT
                        # =================================

                        st.divider()

                        st.subheader("Ajouter un nouvel employé")

                        with st.form("form_ajout_employe"):

                            matricule = st.text_input("Matricule")

                            nom = st.text_input("Nom")

                            prenom = st.text_input("Prénom")

                            email = st.text_input("Email")

                            telephone = st.text_input("Téléphone")

                            poste = st.text_input("Poste")

                            departement_choisi = st.selectbox(
                                "Département",
                                list(dep_options.keys())
                            )

                            date_embauche = st.date_input(
                                "Date d'embauche"
                            )

                            submitted = st.form_submit_button(
                                "Enregistrer l'employé"
                            )

                            if submitted:

                                if not all([
                                    matricule.strip(),
                                    nom.strip(),
                                    prenom.strip(),
                                    email.strip(),
                                    telephone.strip(),
                                    poste.strip()
                                ]):

                                    st.warning(
                                        "Veuillez remplir tous les champs."
                                    )

                                else:

                                    nouvel_employe = {
                                        "matricule": matricule.strip(),
                                        "nom": nom.strip(),
                                        "prenom": prenom.strip(),
                                        "email": email.strip(),
                                        "telephone": telephone.strip(),
                                        "date_embauche": date_embauche.isoformat(),
                                        "departement_id": dep_options[
                                            departement_choisi
                                        ],
                                        "poste": poste.strip()
                                    }

                                    ajout = requests.post(
                                        f"{API_URL}/employes/",
                                        json=nouvel_employe,
                                        headers=headers
                                    )

                                    if ajout.status_code in [200, 201]:

                                        st.success(
                                            "Employé ajouté avec succès !"
                                        )

                                        st.rerun()

                                    else:

                                        st.error(
                                            f"Erreur {ajout.status_code} : "
                                            f"{ajout.text}"
                                        )

                        
                        # =========================================
                        # CONSULTATION DES SOLDES DE CONGES
                        # =========================================

                        st.divider()
                        st.subheader("Consulter le solde de congés")

                        if employes:

                            options_soldes = {
                                f"{emp['prenom']} {emp['nom']} - {emp['matricule']}": emp
                                for emp in employes
                            }

                            employe_solde_choisi = st.selectbox(
                                "Sélectionner un employé",
                                list(options_soldes.keys()),
                                key="employe_consultation_solde"
                            )

                            employe_solde = options_soldes[employe_solde_choisi]

                            if st.button("Consulter le solde", key="btn_consulter_solde"):

                                solde_response = requests.get(
                                    f"{API_URL}/soldes-conges/",
                                    headers=headers
                                )

                                if solde_response.status_code == 200:

                                    soldes = solde_response.json()

                                    solde_employe = next(
                                        (
                                            s for s in soldes
                                            if s.get("employe_id") == employe_solde["id"]
                                            and s.get("annee") == date.today().year
                                        ),
                                        None
                                    )

                                    if solde_employe:

                                        solde_disponible = (
                                            float(solde_employe.get("solde_initial", 0))
                                            + float(solde_employe.get("jours_acquis", 0))
                                            + float(solde_employe.get("solde_reporte", 0))
                                            - float(solde_employe.get("jours_pris", 0))
                                        )

                                        col1, col2, col3 = st.columns(3)

                                        col1.metric(
                                            "Jours acquis",
                                            solde_employe.get("jours_acquis", 0)
                                        )

                                        col2.metric(
                                            "Jours pris",
                                            solde_employe.get("jours_pris", 0)
                                        )

                                        col3.metric(
                                            "Solde disponible",
                                            solde_disponible
                                        )

                                        st.write(
                                            "**Solde initial :**",
                                            solde_employe.get("solde_initial", 0)
                                        )

                                        st.write(
                                            "**Solde reporté :**",
                                            solde_employe.get("solde_reporte", 0)
                                        )

                                    else:
                                        st.info(
                                            "Aucun solde de congés enregistré pour cet employé "
                                            "pour l'année en cours."
                                        )

                                else:
                                    st.error(
                                        f"Impossible de récupérer les soldes : "
                                        f"{solde_response.status_code}"
                                    )

                        else:
                            st.info("Aucun employé disponible.")

                        # =================================
                            # FORMULAIRE DE MODIFICATION
                        # =================================

                        st.divider()

                        st.subheader("Modifier un employé")

                        if employes:

                            employe_options = {
                                f"{emp['prenom']} {emp['nom']} - {emp['matricule']}": emp
                                for emp in employes
                            }

                            employe_choisi = st.selectbox(
                                "Sélectionner l'employé à modifier",
                                list(employe_options.keys()),
                                key="employe_a_modifier"
                            )

                            employe_selectionne = employe_options[
                                employe_choisi
                            ]

                            noms_departements = list(dep_options.keys())

                            dep_actuel = employe_selectionne.get(
                                "departement_id"
                            )

                            index_dep = next(
                                (
                                    i for i, nom_dep in enumerate(noms_departements)
                                    if dep_options[nom_dep] == dep_actuel
                                ),
                                0
                            )

                            with st.form("form_modifier_employe"):

                                nouveau_nom = st.text_input(
                                    "Nom",
                                    value=employe_selectionne.get("nom", "")
                                )

                                nouveau_prenom = st.text_input(
                                    "Prénom",
                                    value=employe_selectionne.get("prenom", "")
                                )

                                nouvel_email = st.text_input(
                                    "Email",
                                    value=employe_selectionne.get("email", "")
                                )

                                nouveau_telephone = st.text_input(
                                    "Téléphone",
                                    value=employe_selectionne.get("telephone") or ""
                                )

                                nouveau_poste = st.text_input(
                                    "Poste",
                                    value=employe_selectionne.get("poste", "")
                                )

                                nouveau_departement = st.selectbox(
                                    "Département",
                                    noms_departements,
                                    index=index_dep
                                )

                                modifier = st.form_submit_button(
                                    "Enregistrer les modifications"
                                )

                                if modifier:

                                    donnees_modifiees = {
                                        "nom": nouveau_nom.strip(),
                                        "prenom": nouveau_prenom.strip(),
                                        "email": nouvel_email.strip(),
                                        "telephone": nouveau_telephone.strip(),
                                        "poste": nouveau_poste.strip(),
                                        "departement_id": dep_options[
                                            nouveau_departement
                                        ]
                                    }

                                    if not all([
                                        donnees_modifiees["nom"],
                                        donnees_modifiees["prenom"],
                                        donnees_modifiees["email"],
                                        donnees_modifiees["telephone"],
                                        donnees_modifiees["poste"]
                                    ]):

                                        st.warning(
                                            "Veuillez remplir tous les champs."
                                        )

                                    else:

                                        modification = requests.patch(
                                            f"{API_URL}/employes/{employe_selectionne['id']}",
                                            json=donnees_modifiees,
                                            headers=headers
                                        )

                                        if modification.status_code == 200:

                                            st.success(
                                                "Informations modifiées avec succès !"
                                            )

                                            st.rerun()

                                        else:

                                            st.error(
                                                f"Erreur {modification.status_code} : "
                                                f"{modification.text}"
                                            )

                        else:

                            st.info(
                                "Ajoutez d'abord un employé pour pouvoir "
                                "modifier ses informations."
                            )
                        
                        # =================================
                        # DESACTIVER UN EMPLOYE
                        # =================================

                        st.divider()

                        st.subheader("Désactiver un employé")

                        employes_actifs = [
                            emp for emp in employes
                            if emp.get("statut") == "actif"
                        ]

                        if employes_actifs:

                            options_desactivation = {
                                f"{emp['prenom']} {emp['nom']} - {emp['matricule']}": emp
                                for emp in employes_actifs
                            }

                            employe_a_desactiver = st.selectbox(
                                "Sélectionner l'employé à désactiver",
                                list(options_desactivation.keys()),
                                key="employe_a_desactiver"
                            )

                            employe_selectionne_desactivation = (
                                options_desactivation[employe_a_desactiver]
                            )

                            confirmer = st.checkbox(
                                "Je confirme vouloir désactiver cet employé.",
                                key="confirmation_desactivation"
                            )

                            if st.button(
                                "Désactiver l'employé",
                                type="secondary"
                            ):

                                if confirmer:

                                    desactivation = requests.patch(
                                        f"{API_URL}/employes/{employe_selectionne_desactivation['id']}/desactiver",
                                        headers=headers
                                    )

                                    if desactivation.status_code == 200:

                                        st.success(
                                            "Employé désactivé avec succès !"
                                        )

                                        st.rerun()

                                    else:

                                        st.error(
                                            f"Erreur {desactivation.status_code} : "
                                            f"{desactivation.text}"
                                        )

                                else:

                                    st.warning(
                                        "Veuillez confirmer la désactivation."
                                    )

                        else:

                            st.info(
                                "Aucun employé actif à désactiver."
                            )

                        
                        # =================================
                        # REACTIVER UN EMPLOYE
                        # =================================

                        st.divider()

                        st.subheader("Réactiver un employé")

                        employes_inactifs = [
                            emp for emp in employes
                            if emp.get("statut") == "inactif"
                        ]

                        if employes_inactifs:

                            options_reactivation = {
                                f"{emp['prenom']} {emp['nom']} - {emp['matricule']}": emp
                                for emp in employes_inactifs
                            }

                            employe_a_reactiver = st.selectbox(
                                "Sélectionner l'employé à réactiver",
                                list(options_reactivation.keys()),
                                key="employe_a_reactiver"
                            )

                            employe_selectionne_reactivation = (
                                options_reactivation[employe_a_reactiver]
                            )

                            confirmer_reactivation = st.checkbox(
                                "Je confirme vouloir réactiver cet employé.",
                                key="confirmation_reactivation"
                            )

                            if st.button("Réactiver l'employé"):

                                if confirmer_reactivation:

                                    reactivation = requests.patch(
                                        f"{API_URL}/employes/{employe_selectionne_reactivation['id']}/reactiver",
                                        headers=headers
                                    )

                                    if reactivation.status_code == 200:

                                        st.success(
                                            "Employé réactivé avec succès !"
                                        )

                                        st.rerun()

                                    else:

                                        st.error(
                                            f"Erreur {reactivation.status_code} : "
                                            f"{reactivation.text}"
                                        )

                                else:

                                    st.warning(
                                        "Veuillez confirmer la réactivation."
                                    )

                        else:

                            st.info(
                                "Aucun employé inactif à réactiver."
                            )
    
                    else:

                        st.warning(
                            "Aucun département disponible. "
                            "Veuillez créer un département."
                        )

                else:

                    st.error(
                        "Impossible de récupérer les départements."
                    )

            else:

                st.error(
                    f"Erreur lors du chargement des employés : "
                    f"{response.status_code}"
                )

        # =================================================
        # 3. GESTION DES DEPARTEMENTS
        # =================================================

        
        elif page == "Départements":
            st.title("Gestion des départements")

            headers = {
                "Authorization": f"Bearer {st.session_state.token}"
            }

            # Récupération des départements
            response = requests.get(
                f"{API_URL}/departements/",
                headers=headers
            )

            if response.status_code == 200:
                departements = response.json()

                st.subheader("Liste des départements")

                if departements:
                    df = pd.DataFrame(departements)
                    st.dataframe(df, use_container_width=True)
                    st.metric("Nombre de départements", len(departements))

                    # Modification
                    st.divider()
                    st.subheader("Modifier un département")

                    options = {
                        f"{d['nom']} (ID : {d['id']})": d
                        for d in departements
                    }

                    choix = st.selectbox(
                        "Choisir un département",
                        list(options.keys()),
                        key="choix_departement_modif"
                    )

                    departement = options[choix]

                    with st.form("form_modification_departement"):
                        nouveau_nom = st.text_input(
                            "Nom",
                            value=departement["nom"]
                        )

                        nouvelle_description = st.text_area(
                            "Description",
                            value=departement.get("description") or ""
                        )

                        modifier = st.form_submit_button("Enregistrer les modifications")

                        if modifier:
                            if not nouveau_nom.strip():
                                st.warning("Le nom est obligatoire.")
                            else:
                                data = {
                                    "nom": nouveau_nom,
                                    "description": nouvelle_description
                                }

                                r = requests.patch(
                                    f"{API_URL}/departements/{departement['id']}",
                                    json=data,
                                    headers=headers
                                )

                                if r.status_code == 200:
                                    st.success("Département modifié avec succès.")
                                    st.rerun()
                                else:
                                    st.error(f"Erreur : {r.text}")

                    # Suppression
                    st.divider()
                    st.subheader("Supprimer un département")

                    choix_suppression = st.selectbox(
                        "Département à supprimer",
                        list(options.keys()),
                        key="choix_departement_suppression"
                    )

                    departement_suppression = options[choix_suppression]

                    confirmation = st.checkbox(
                        "Je confirme vouloir supprimer ce département.",
                        key="confirmation_suppression_departement"
                    )

                    if st.button("Supprimer le département"):
                        if confirmation:
                            r = requests.delete(
                                f"{API_URL}/departements/{departement_suppression['id']}",
                                headers=headers
                            )

                            if r.status_code == 200:
                                st.success("Département supprimé avec succès.")
                                st.rerun()
                            else:
                                st.error(f"Suppression impossible : {r.text}")
                        else:
                            st.warning("Veuillez confirmer la suppression.")

                else:
                    st.info("Aucun département enregistré.")

            else:
                st.error(f"Erreur de récupération : {response.text}")

            # Ajout
            st.divider()
            st.subheader("Ajouter un département")

            with st.form("form_ajout_departement"):
                nom = st.text_input("Nom du département")
                description = st.text_area("Description")

                submitted = st.form_submit_button("Ajouter")

                if submitted:
                    if not nom.strip():
                        st.warning("Le nom du département est obligatoire.")
                    else:
                        data = {
                            "nom": nom,
                            "description": description
                        }

                        r = requests.post(
                            f"{API_URL}/departements/",
                            json=data,
                            headers=headers
                        )

                        if r.status_code in [200, 201]:
                            st.success("Département ajouté avec succès.")
                            st.rerun()
                        else:
                            st.error(f"Erreur : {r.text}")


        # =================================================
        # 4. GESTION DES DEMANDES
        # =================================================

        
        elif page == "Demandes":
            st.title("Gestion des demandes d'absence")

            headers = {
                "Authorization": f"Bearer {st.session_state.token}"
            }

            # Récupération des demandes
            response = requests.get(
                f"{API_URL}/demandes-absence/",
                headers=headers
            )

            if response.status_code == 200:
                demandes = response.json()

                if demandes:
                    # Récupération des employés
                    rep_employes = requests.get(
                        f"{API_URL}/employes/",
                        headers=headers
                    )

                    # Récupération des types d'absence
                    rep_types = requests.get(
                        f"{API_URL}/types-absence/",
                        headers=headers
                    )

                    employes = rep_employes.json() if rep_employes.status_code == 200 else []
                    types = rep_types.json() if rep_types.status_code == 200 else []

                    employes_dict = {
                        e["id"]: f"{e['prenom']} {e['nom']}"
                        for e in employes
                    }

                    types_dict = {
                        t["id"]: t["nom"]
                        for t in types
                    }

                    # Préparation des données
                    lignes = []

                    for d in demandes:
                        lignes.append({
                            "ID": d["id"],
                            "Employé": employes_dict.get(d["employe_id"], "Inconnu"),
                            "Type d'absence": types_dict.get(d["type_absence_id"], "Inconnu"),
                            "Date début": d["date_debut"],
                            "Date fin": d["date_fin"],
                            "Nombre de jours": d["nombre_jours"],
                            "Motif": d["motif"],
                            "Statut": d["statut"],
                            "Date de soumission": d["created_at"]
                        })

                    df = pd.DataFrame(lignes)

                    # Indicateurs
                    col1, col2, col3, col4 = st.columns(4)

                    col1.metric("Total demandes", len(df))
                    col2.metric("En attente", (df["Statut"] == "en_attente").sum())
                    col3.metric("Approuvées", (df["Statut"] == "approuvee").sum())
                    col4.metric("Rejetées", (df["Statut"] == "rejetee").sum())

                    st.divider()

                    # Filtre par statut
                    st.subheader("Liste des demandes")

                    statuts = ["Tous"] + sorted(df["Statut"].dropna().unique().tolist())

                    statut_selectionne = st.selectbox(
                        "Filtrer par statut",
                        statuts
                    )

                    if statut_selectionne != "Tous":
                        df = df[df["Statut"] == statut_selectionne]

                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    st.divider()
                    st.subheader("Consulter les détails d'une demande")

                    demandes_dict = {
                        f"Demande #{d['id']} - {employes_dict.get(d['employe_id'], 'Inconnu')}": d
                        for d in demandes
                    }

                    choix_demande = st.selectbox(
                        "Sélectionner une demande",
                        list(demandes_dict.keys()),
                        key="details_demande"
                    )

                    demande = demandes_dict[choix_demande]

                    nom_employe = employes_dict.get(
                        demande["employe_id"], "Inconnu"
                    )

                    st.markdown(f"**Demande n° :** {demande['id']}")
                    st.markdown(f"**Employé :** {nom_employe}")
                    st.markdown(
                        f"**Type d'absence :** "
                        f"{types_dict.get(demande['type_absence_id'], 'Inconnu')}"
                    )
                    st.markdown(f"**Date de début :** {demande['date_debut']}")
                    st.markdown(f"**Date de fin :** {demande['date_fin']}")
                    st.markdown(f"**Nombre de jours :** {demande['nombre_jours']}")
                    st.markdown(f"**Motif :** {demande['motif']}")
                    st.markdown(f"**Statut :** {demande['statut']}")
                    st.markdown(f"**Date de soumission :** {demande['created_at']}")

                else:
                    st.info("Aucune demande d'absence enregistrée.")

            else:
                st.error(f"Erreur lors de la récupération : {response.text}")


        # =================================================
        # 5. RAPPORTS RH
        # =================================================

        
        elif page == "Rapports":
            st.title("Rapports et statistiques RH")

            headers = {
                "Authorization": f"Bearer {st.session_state.token}"
            }

            # Récupération des données
            rep_demandes = requests.get(
                f"{API_URL}/demandes-absence/",
                headers=headers
            )

            rep_employes = requests.get(
                f"{API_URL}/employes/",
                headers=headers
            )

            rep_departements = requests.get(
                f"{API_URL}/departements/",
                headers=headers
            )

            rep_types = requests.get(
                f"{API_URL}/types-absence/",
                headers=headers
            )

            if all(r.status_code == 200 for r in [
                rep_demandes, rep_employes,
                rep_departements, rep_types
            ]):

                demandes = rep_demandes.json()
                employes = rep_employes.json()
                departements = rep_departements.json()
                types = rep_types.json()

                if demandes:
                    df = pd.DataFrame(demandes)

                    employes_dict = {
                        e["id"]: e for e in employes
                    }

                    departements_dict = {
                        d["id"]: d["nom"] for d in departements
                    }

                    types_dict = {
                        t["id"]: t["nom"] for t in types
                    }

                    df["Employé"] = df["employe_id"].map(
                        lambda x: (
                            f"{employes_dict[x]['prenom']} "
                            f"{employes_dict[x]['nom']}"
                        ) if x in employes_dict else "Inconnu"
                    )

                    df["Département"] = df["employe_id"].map(
                        lambda x: departements_dict.get(
                            employes_dict[x].get("departement_id"),
                            "Non renseigné"
                        ) if x in employes_dict else "Non renseigné"
                    )

                    df["Type d'absence"] = df["type_absence_id"].map(
                        lambda x: types_dict.get(x, "Inconnu")
                    )

                    df["Date"] = pd.to_datetime(
                        df["date_debut"], errors="coerce"
                    )

                    df["Nombre de jours"] = pd.to_numeric(
                        df["nombre_jours"], errors="coerce"
                    ).fillna(0)

                    # Filtres
                    st.subheader("Filtres")

                    col1, col2 = st.columns(2)

                    with col1:
                        statuts = ["Tous"] + sorted(
                            df["statut"].dropna().unique().tolist()
                        )
                        statut = st.selectbox("Statut", statuts)

                    with col2:
                        annees = sorted(
                            df["Date"].dropna().dt.year.unique().tolist(),
                            reverse=True
                        )
                        annee = st.selectbox("Année", ["Toutes"] + annees)

                    df_filtre = df.copy()

                    if statut != "Tous":
                        df_filtre = df_filtre[
                            df_filtre["statut"] == statut
                        ]

                    if annee != "Toutes":
                        df_filtre = df_filtre[
                            df_filtre["Date"].dt.year == annee
                        ]

                    st.divider()

                    # Indicateurs
                    st.subheader("Indicateurs clés")

                    col1, col2, col3, col4 = st.columns(4)

                    col1.metric("Total demandes", len(df_filtre))

                    col2.metric(
                        "En attente",
                        (df_filtre["statut"] == "en_attente").sum()
                    )

                    col3.metric(
                        "Approuvées",
                        (df_filtre["statut"] == "approuvee").sum()
                    )

                    col4.metric(
                        "Rejetées",
                        (df_filtre["statut"] == "rejetee").sum()
                    )

                    st.divider()

                    # Répartition par type
                    st.subheader("Demandes par type d'absence")

                    par_type = (
                        df_filtre.groupby("Type d'absence")
                        .size()
                        .reset_index(name="Nombre de demandes")
                    )

                    fig_type = px.pie(
                        par_type,
                        names="Type d'absence",
                        values="Nombre de demandes",
                        hole=0.4
                    )

                    st.plotly_chart(fig_type, use_container_width=True)

                    # Évolution mensuelle
                    st.subheader("Évolution mensuelle des demandes")

                    df_mois = df_filtre.dropna(subset=["Date"]).copy()

                    if not df_mois.empty:
                        df_mois["Mois"] = (
                            df_mois["Date"].dt.to_period("M").astype(str)
                        )

                        evolution = (
                            df_mois.groupby("Mois")
                            .size()
                            .reset_index(name="Nombre de demandes")
                            .sort_values("Mois")
                        )

                        fig_mois = px.line(
                            evolution,
                            x="Mois",
                            y="Nombre de demandes",
                            markers=True,
                            title="Évolution des demandes par mois"
                        )

                        st.plotly_chart(
                            fig_mois,
                            use_container_width=True
                        )

                    
                    # Nombre d'absences par département
                    st.subheader("Nombre d'absences par département")

                    par_departement = (
                        df_filtre[df_filtre["statut"] == "approuvee"]
                        .groupby("Département")
                        .size()
                        .reset_index(name="Nombre d'absences")
                        .sort_values("Nombre d'absences", ascending=False)
                    )

                    if not par_departement.empty:

                        fig_departement = px.bar(
                            par_departement,
                            x="Département",
                            y="Nombre d'absences",
                            text="Nombre d'absences",
                            color="Département",
                            title="Répartition des absences approuvées par département"
                        )

                        fig_departement.update_layout(
                            xaxis_title="Départements",
                            yaxis_title="Nombre d'absences",
                            showlegend=False
                        )

                        st.plotly_chart(
                            fig_departement,
                            use_container_width=True
                        )

                    else:
                        st.info("Aucune absence approuvée pour cette période.")


                    # Jours d'absence par employé
                    st.subheader("Nombre de jours demandés par employé")

                    par_employe = (
                        df_filtre.groupby("Employé")["Nombre de jours"]
                        .sum()
                        .reset_index()
                        .sort_values("Nombre de jours", ascending=False)
                    )

                    fig_employe = px.bar(
                        par_employe,
                        x="Employé",
                        y="Nombre de jours",
                        title="Jours d'absence demandés par employé"
                    )

                    st.plotly_chart(
                        fig_employe,
                        use_container_width=True
                    )

                else:
                    st.info("Aucune demande disponible pour générer les rapports.")

            else:
                st.error("Impossible de récupérer les données nécessaires aux rapports.")



    # =================================================
    # DÉCONNEXION
    # =================================================

    if st.sidebar.button("Se déconnecter"):

        st.session_state.token = None
        st.session_state.utilisateur = None

        st.rerun()
