# HRFlow AI – Intelligent HR Absence & Leave Management

**HRFlow AI** est une application intelligente de gestion des ressources humaines permettant de centraliser le suivi des employés, des demandes d'absence et des congés, tout en intégrant un agent d'intelligence artificielle capable d'analyser les données RH et de répondre aux questions formulées en langage naturel.

Le projet associe le développement d'une application métier, la gestion des données et l'intégration d'un agent IA outillé afin de faciliter le suivi administratif et d'accompagner la prise de décision des responsables RH.

---

## Présentation du projet

La gestion des absences et des congés nécessite un suivi rigoureux des demandes, des validations et des soldes disponibles.

HRFlow AI propose une solution permettant de :

- Centraliser les informations relatives aux employés et aux départements.
- Gérer les demandes d'absence et de congés.
- Organiser le processus de validation par les responsables RH.
- Suivre les soldes de congés et leur acquisition.
- Consulter les historiques et les notifications.
- Analyser les indicateurs RH à travers des tableaux de bord.
- Interroger les données RH en langage naturel grâce à un assistant IA.

## Fonctionnalités principales

### 1. Gestion des ressources humaines
- Gestion des employés.
- Gestion des départements.
- Gestion des comptes utilisateurs.
- Gestion des rôles et des accès.
- Activation et désactivation des comptes employés.

### 2. Gestion des absences et des congés
- Soumission des demandes d'absence.
- Consultation et suivi des demandes.
- Validation ou rejet des demandes par les responsables autorisés.
- Gestion des différents types d'absence.
- Suivi des soldes de congés.
- Acquisition périodique des droits à congé.
- Historique des opérations et notifications.

### 3. Tableaux de bord et analyses RH
- Analyse des absences par département.
- Analyse des demandes par type d'absence.
- Répartition des demandes selon leur statut.
- Classement des employés selon leurs absences.
- Analyse de l'évolution mensuelle des demandes.

### 4. Assistant IA RH – HRFlow AI

L'application intègre un agent IA développé avec **LangGraph** et **Groq**.

Cet agent permet aux responsables RH de poser des questions en langage naturel et d'obtenir des analyses basées sur les données disponibles dans PostgreSQL.

Exemples de questions :

- Quels départements enregistrent le plus de jours d'absence ?
- Quelle est la répartition des demandes par type d'absence ?
- Combien de demandes sont en attente de validation ?
- Quels employés enregistrent le plus de jours d'absence ?
- Comment évolue le nombre de demandes d'absence mois par mois ?

L'agent s'appuie sur des outils Python spécialisés (*Tools*) pour interroger les données et produire des résultats exploitables. Les réponses peuvent être accompagnées de visualisations adaptées.

**Important :** l'agent IA intervient comme un outil d'assistance à l'analyse et à la décision. Les décisions définitives concernant les demandes d'absence restent sous la responsabilité des personnes habilitées.

---

## Architecture technique

HRFlow AI repose sur une architecture composée de plusieurs couches :

| Couche | Technologies | Responsabilité |
|---|---|---|
| Frontend | Streamlit | Interface utilisateur |
| Backend | FastAPI | API REST et logique métier |
| Base de données | PostgreSQL | Stockage des données RH |
| ORM | SQLAlchemy | Interaction avec la base de données |
| Authentification | JWT | Authentification et contrôle d'accès |
| Agent IA | LangGraph | Orchestration de l'agent |
| Modèle de langage | Groq | Compréhension et génération des réponses |
| Visualisation | Plotly | Graphiques et analyses |

### Architecture de l'agent IA

Le fonctionnement de l'assistant repose sur le principe du *Tool Calling* :

1. L'utilisateur formule une question en langage naturel.
2. L'agent IA interprète la demande.
3. LangGraph orchestre l'exécution et la sélection des outils disponibles.
4. Les outils Python exécutent les analyses nécessaires sur PostgreSQL.
5. L'agent exploite les résultats pour construire une réponse.
6. Streamlit affiche la réponse et, lorsque cela est pertinent, le graphique correspondant.

---

## Technologies utilisées

- **Langage :** Python
- **Backend :** FastAPI
- **Frontend :** Streamlit
- **Base de données :** PostgreSQL
- **ORM :** SQLAlchemy
- **Authentification :** JSON Web Token (JWT)
- **Intelligence artificielle :** LangGraph, LangChain, Groq
- **Visualisation :** Plotly
- **Gestion de versions :** Git et GitHub

---

## Installation et exécution

### 1. Cloner le dépôt

```bash
git clone https://github.com/BoladeMmd/HRFlow-AI.git
cd HRFlow-AI
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
```

Activation sous Windows :

```bash
venv\Scripts\activate
```

Activation sous Linux/macOS :

```bash
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Créer un fichier `.env` à partir de `.env.example`, puis renseigner les paramètres nécessaires :

```env
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/hrflow_ai
GROQ_API_KEY=YOUR_GROQ_API_KEY
GROQ_MODEL=openai/gpt-oss-120b
SECRET_KEY=YOUR_SECRET_KEY
```

Ne jamais publier le fichier `.env` ou les véritables clés et mots de passe sur GitHub.

### 5. Préparer PostgreSQL

Créer la base de données `hrflow_ai`, puis appliquer le schéma et les éventuelles migrations correspondant à la version du projet.

### 6. Lancer le backend

Depuis le dossier `backend` :

```bash
uvicorn app.main:app --reload
```

Documentation interactive de l'API :

http://127.0.0.1:8000/docs

### 7. Lancer le frontend

Dans un autre terminal, depuis le dossier contenant `app.py` :

```bash
streamlit run app.py
```

L'interface sera accessible à l'adresse indiquée dans le terminal Streamlit.

**NB:** Veuillez consulter le fichier docs/captures pour voir quelques captures présentant la plateforme 

---

## Sécurité et gestion des accès

L'application prévoit plusieurs profils utilisateurs :

- **Administrateur RH :** administration des ressources et des comptes.
- **Responsable :** suivi des demandes, validations et analyses RH.
- **Employé :** accès à ses informations, demandes et notifications.

L'accès aux fonctionnalités est contrôlé selon les rôles. Les données RH étant sensibles, toute utilisation en environnement réel nécessite des mesures complémentaires de sécurité, de confidentialité, de sauvegarde et de contrôle des accès.

---

## Perspectives d'évolution

Plusieurs améliorations peuvent être envisagées :

- Mise en place d'une chaîne CI/CD pour automatiser les tests et les déploiements.
- Conteneurisation avec Docker et Docker Compose.
- Développement d'un système de rapports RH automatisés.
- Ajout de nouvelles capacités d'analyse prédictive.
- Intégration de notifications par e-mail.
- Extension des capacités de l'agent IA à d'autres processus RH.
- Renforcement de la supervision et de la traçabilité.

---

## Auteur

**Projet réalisé par Boladé MAMADOU , Ingenieur data & IA .**

**Domaines mobilisés :**
- Data Engineering
- Développement d'API et d'applications métier
- Bases de données relationnelles
- Intelligence artificielle générative
- Agents IA et automatisation

---

## Licence

Projet développé à des fins pédagogiques et de portfolio. Les conditions de réutilisation et de distribution peuvent être précisées dans un fichier `LICENSE`.

---

**HRFlow AI – Making HR Management Smarter with Data & AI.**
