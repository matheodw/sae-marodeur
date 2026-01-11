"""Supprime des personnes et leurs présences par id.

Usage:
    python delete_persons_by_id.py 9 10
    python delete_persons_by_id.py --db path/to/marodeur.db 9 10
"""
import argparse
import sqlite3
import sys

parser = argparse.ArgumentParser(description="Supprime des personnes (et leurs présences) par id")
parser.add_argument('--db', default='marodeur.db', help='Chemin vers la base SQLite')
parser.add_argument('ids', nargs='+', type=int, help='IDs des personnes à supprimer')
args = parser.parse_args()

conn = sqlite3.connect(args.db)
cur = conn.cursor()
ids = args.ids
if not ids:
    print("Aucun id fourni")
    sys.exit(1)

placeholders = ','.join('?' for _ in ids)
try:
    cur.execute(f"SELECT id, nom, prenom FROM personnes WHERE id IN ({placeholders})", ids)
    found = cur.fetchall()
    if not found:
        print(f"Aucune personne trouvée pour les ids: {ids}")
    else:
        print("Personnes trouvées:")
        for r in found:
            print(f" - id={r[0]}: {r[1]} {r[2]}")

        # Supprimer présences puis personnes
        cur.execute(f"DELETE FROM presences WHERE personne_id IN ({placeholders})", ids)
        cur.execute(f"DELETE FROM personnes WHERE id IN ({placeholders})", ids)
        conn.commit()
        print(f"Supprimé personnes et présences pour ids: {ids}")

    # Vérification
    cur.execute(f"SELECT id, nom, prenom FROM personnes WHERE id IN ({placeholders})", ids)
    remaining = cur.fetchall()
    print("Vérification (doit être vide):", remaining)

except Exception as e:
    print("Erreur:", e)
finally:
    conn.close()
