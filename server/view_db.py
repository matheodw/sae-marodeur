"""Script pour visualiser rapidement la base de données."""
import sys
import os

# Configuration du chemin pour l'import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database

# 1. Initialiser l'objet Database
db = Database("marodeur.db")

# 2. Utiliser get_connection() pour obtenir une connexion ponctuelle
conn = db.get_connection()
cursor = conn.cursor()

print("\n=== CONTENU DE LA BASE DE DONNÉES ===\n")

try:
    # Lister toutes les tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    # sqlite3.Row permet d'accéder aux données par index ou par nom, 
    # mais ici on récupère juste le nom de la table.
    tables = cursor.fetchall()

    for table_row in tables:
        table_name = table_row[0]
        print(f"\n Table: {table_name}")
        print("-" * 50)
        
        # Récupérer les données
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # Récupérer les noms des colonnes via PRAGMA
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        if rows:
            print(" | ".join(columns))
            print("-" * 50)
            
            # Afficher les données
            for row in rows:
                # Comme nous utilisons row_factory = sqlite3.Row, 
                # on transforme en liste pour l'affichage
                print(" | ".join(str(val) if val is not None else "NULL" for val in list(row)))
        else:
            print("(vide)")
        
        print()

finally:
    # 3. Fermer proprement le curseur et la connexion
    cursor.close()
    conn.close()
    print("Visualisation terminée, base déconnectée.")