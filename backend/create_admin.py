from getpass import getpass

from sqlalchemy import select

from app.database import SessionLocal
from app.models.utilisateur import Utilisateur
from app.security import hash_password


def creer_admin():
    db = SessionLocal()

    try:
        username = input("Nom d'utilisateur admin : ").strip()

        if not username:
            print("Le nom d'utilisateur est obligatoire.")
            return

        existant = db.scalar(
            select(Utilisateur).where(
                Utilisateur.username == username
            )
        )

        if existant:
            print("Ce nom d'utilisateur existe déjà.")
            return

        password = getpass("Mot de passe : ")
        confirmation = getpass("Confirmer le mot de passe : ")

        if len(password) < 12:
            print("Le mot de passe doit contenir au moins 12 caractères.")
            return

        if password != confirmation:
            print("Les mots de passe ne correspondent pas.")
            return

        admin = Utilisateur(
            employe_id=None,
            username=username,
            password_hash=hash_password(password),
            role="admin_rh",
            actif=True
        )

        db.add(admin)
        db.commit()

        print("Compte administrateur créé avec succès.")

    except Exception as erreur:
        db.rollback()
        print("Erreur :", erreur)

    finally:
        db.close()


if __name__ == "__main__":
    creer_admin()

