"""Script pour remplir la base SQLite avec un jeu de données de test.
Modifié pour être compatible avec la classe Database thread-safe.
"""

import argparse
from datetime import datetime, timedelta
import sqlite3
import os

from database import Database

def seed(db_path: str = "marodeur.db", force: bool = False, reset_ids: bool = False):
    print(f"Utilisation de la base: {db_path}")

    """
    Main function to fill the database.
    
    :param db_path: Path to the database file.
    :param force: If True, deletes the old database file first.
    :param reset_ids: If True, restarts ID counters at 1.
    """
    if force and os.path.exists(db_path):
        print("--force: suppression de la base existante...")
        try:
            os.remove(db_path)
        except Exception as e:
            print(f"Erreur suppression fichier: {e}")
  
    db = Database(db_path)
    
    conn = db.get_connection()
    cur = conn.cursor()

    def _reset_sqlite_sequence(table_name: str, force_reset: bool = False):
        """
        Resets the AUTOINCREMENT counter for a specific table.
    
        If force_reset is True, the counter starts back at 1.
        Otherwise, it adjusts to the current maximum ID in the table.
        """
        try:
            cur.execute(f"SELECT MAX(id) FROM {table_name}")
            max_id = cur.fetchone()[0]
            if force_reset:
                cur.execute("DELETE FROM sqlite_sequence WHERE name = ?", (table_name,))
                print(f"  (forced) reset de la séquence pour {table_name}")
            else:
                if max_id is None:
                    cur.execute("DELETE FROM sqlite_sequence WHERE name = ?", (table_name,))
                else:
                    cur.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = ?", (max_id, table_name))
                    if cur.rowcount == 0:
                        cur.execute("INSERT OR IGNORE INTO sqlite_sequence (name, seq) VALUES (?, ?)", (table_name, max_id))
        except Exception as e:
            print(f"  Impossible de reset la séquence pour {table_name}: {e}")

    try:
        salles = [
            ("01", "A", "1", 30, "TP"),
            ("04", "A", "1", 25, "CM"),
            ("200", "B", "2", 40, "Amphi"),
            ("14", "C", "3", 20, "TD"),
            ("1000", "D", "4", 15, "Bureau")
        ]

        cur.execute("SELECT numero FROM salles")
        existing_salles = {r[0] for r in cur.fetchall()}

        for numero, batiment, etage, capacite, type_salle in salles:
            if force or numero not in existing_salles:
                cur.execute(
                    "INSERT OR IGNORE INTO salles (numero, batiment, etage, capacite, type_salle) VALUES (?, ?, ?, ?, ?)",
                    (numero, batiment, etage, capacite, type_salle)
                )
                print(f"  Ajout salle {numero}")

        conn.commit()

        personnes = [
            ("DeWilde", "Matheo", "etudiant", "E001", "mateo.dewilde@etu.univ-poitiers.fr"),
            ("Bouguereau", "Andre", "etudiant", "E002", "andre.bouguereau@etu.univ-poitiers.fr"),
            ("Couderc", "Sebastien", "enseignant", "T001", "sebastien.couderc@etu.univ-poitiers.fr"),
            ("Bruneau", "Theo", "etudiant", "E003", "theo.bruneau@etu.univ-poitiers.fr"),
            ("Verdon", "Vincent", "enseignant", "T002", "vincent.verdon@etu.univ-poitiers.fr"),
            ("Ewen", "Pietrzak", "etudiant", "E004", "ewen.pietrzak@etu.univ-poitiers.fr"),
            ("Foumboulou", "Nancy", "etudiant", "E005", "nancy.foumboulou@etu.univ-poitiers.fr"),
            ("Camarda", "Florent", "enseignant", "T003", "florent.camarda@etu.univ-poitiers.fr"),
        ]

        person_codes = [p[3] for p in personnes]
        if person_codes:
            placeholders = ",".join("?" for _ in person_codes)
            cur.execute(f"SELECT id FROM personnes WHERE code_up_planning IN ({placeholders})", person_codes)
            existing_ids = [r[0] for r in cur.fetchall()]
            if existing_ids:
                pid_placeholders = ",".join("?" for _ in existing_ids)
                cur.execute(f"DELETE FROM presences WHERE personne_id IN ({pid_placeholders})", existing_ids)
                cur.execute(f"DELETE FROM personnes WHERE id IN ({pid_placeholders})", existing_ids)
                print(f"  Suppression des anciennes personnes de test ({len(existing_ids)})")

                _reset_sqlite_sequence('personnes', force_reset=reset_ids)
                _reset_sqlite_sequence('presences', force_reset=reset_ids)

        for nom, prenom, ptype, code, email in personnes:
            cur.execute(
                "INSERT OR IGNORE INTO personnes (nom, prenom, type, code_up_planning, email) VALUES (?, ?, ?, ?, ?)",
                (nom, prenom, ptype, code, email)
            )
            print(f"  Ajout personne {nom} {prenom}")

        conn.commit()

        now = datetime.now()
        cur.execute(f"SELECT id FROM personnes WHERE code_up_planning IN ({','.join('?'*len(person_codes))})", person_codes)
        personne_ids = [r[0] for r in cur.fetchall()]
        
        cur.execute("SELECT id FROM salles WHERE numero IN ('A101','A102','B201')")
        salle_ids = [r[0] for r in cur.fetchall()]

        presences = []
        if len(personne_ids) >= 2 and len(salle_ids) >= 1:
            presences.append((personne_ids[0], salle_ids[0], now - timedelta(minutes=30), now + timedelta(hours=1)))
            presences.append((personne_ids[1], salle_ids[0], now - timedelta(minutes=10), None))

        for p_id, s_id, d_deb, d_fin in presences:
            cur.execute("INSERT INTO presences (personne_id, salle_id, date_debut, date_fin) VALUES (?, ?, ?, ?)",
                        (p_id, s_id, d_deb, d_fin))
        
        conn.commit()

        users = [
            ("secretaire", "secret", "secretaire", "Secretaire", "Test"),
            ("tech", "techpass", "administration", "Technicien", "Test"),
            ("directeur", "direct", "directeur_etudes", "Directeur", "Test")
        ]

        for username, password, role, nom, prenom in users:
            uid = db.create_user(username, password, role, nom, prenom)
            if uid: print(f"  Utilisateur créé: {username}")

        print("\n=== RÉSUMÉ DU JEU DE TEST ===")
        for table in ['salles', 'personnes', 'presences', 'users']:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            print(f"{table.capitalize()}: {cur.fetchone()[0]}")

    finally:
        cur.close()
        conn.close()
        db.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='marodeur.db')
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--reset-ids', action='store_true')
    args = parser.parse_args()
    seed(args.db, args.force, reset_ids=args.reset_ids)
