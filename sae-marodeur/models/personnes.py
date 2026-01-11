import sqlite3
from datetime import datetime
from typing import List

from .personne import Personne


class Personnes:
    def __init__(self, personnes=None):
        self.liste = personnes if personnes is not None else []

    # ----------------------------
    # MÉTHODES INTERNES
    # ----------------------------

    @staticmethod
    def _connect():
        """Connexion simple à la base de données"""
        conn = sqlite3.connect("marodeur.db")
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _from_row(row) -> Personne:
        """Transforme une ligne SQL en objet Personne"""
        nom_complet = f"{row['nom']} {row['prenom']}"
        return Personne(
            nom=nom_complet,
            salle=row["salle"],
            type_personne=row["type"]
        )

    # ----------------------------
    # ACCÈS BASE DE DONNÉES
    # ----------------------------

    @classmethod
    def get_personnel(cls) -> List[Personne]:
        """Récupère les enseignants actuellement présents"""
        now = datetime.now()

        with cls._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.nom, p.prenom, p.type, s.numero AS salle
                FROM personnes p
                LEFT JOIN presences pres ON p.id = pres.personne_id
                    AND pres.date_debut <= ?
                    AND (pres.date_fin IS NULL OR pres.date_fin >= ?)
                LEFT JOIN salles s ON pres.salle_id = s.id
                WHERE p.type = 'enseignant'
                ORDER BY p.nom, p.prenom
            """, (now, now))

            return [cls._from_row(row) for row in cursor.fetchall()]

    # ----------------------------
    # GESTION DE LISTE
    # ----------------------------

    def ajouter(self, personne: Personne):
        if isinstance(personne, Personne):
            self.liste.append(personne)

    def get_by_salle(self, salle):
        return [p for p in self.liste if p.salle == salle]

    def get_by_type(self, type_personne):
        return [p for p in self.liste if p.type_personne == type_personne]

    def __len__(self):
        return len(self.liste)

    def __repr__(self):
        return f"Personnes({len(self.liste)} personnes)"
