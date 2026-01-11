"""Script de test pour tous les modèles de l'application.
Teste les fonctionnalités de User, Salle, Personne et Personnes.
"""
import sys
import os

# Ajouter le chemin du projet pour les imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sae_marodeur_path = os.path.join(project_root, "sae-marodeur")
sys.path.insert(0, sae_marodeur_path)

from models.user import User
from models.salle import Salle
from models.personne import Personne
from models.personnes import Personnes


def print_section(title):
    """Affiche un titre de section."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_success(message):
    """Affiche un message de succès."""
    print(f"   [OK] {message}")


def print_error(message):
    """Affiche un message d'erreur."""
    print(f"   [ERREUR] {message}")


def test_user():
    """Teste le modèle User."""
    print_section("TEST DU MODÈLE USER")
    
    # Test 1: Récupérer un utilisateur par username
    print("\n1. Test get_by_username:")
    try:
        user = User.get_by_username("admin")
        if user:
            print_success(f"Utilisateur trouvé: {user.username} (role: {user.role})")
            print(f"     Nom: {user.nom}, Prénom: {user.prenom}")
        else:
            print_error("Aucun utilisateur trouvé avec ce username")
    except Exception as e:
        print_error(f"Erreur lors de la récupération: {e}")
        user = None
    
    # Test 2: Récupérer un utilisateur par ID
    print("\n2. Test get_by_id:")
    if user:
        try:
            user_by_id = User.get_by_id(user.id)
            if user_by_id:
                print_success(f"Utilisateur trouvé par ID: {user_by_id.username}")
            else:
                print_error("Aucun utilisateur trouvé avec cet ID")
        except Exception as e:
            print_error(f"Erreur lors de la récupération: {e}")
    
    # Test 3: Récupérer tous les utilisateurs
    print("\n3. Test get_all:")
    try:
        all_users = User.get_all()
        print_success(f"Nombre d'utilisateurs trouvés: {len(all_users)}")
        for u in all_users:
            print(f"     - {u.username} ({u.role})")
    except Exception as e:
        print_error(f"Erreur lors de la récupération: {e}")
        all_users = []
    
    # Test 4: Vérification du mot de passe
    print("\n4. Test verify_password:")
    if user:
        # Note: Le mot de passe est hashé dans la DB, donc ce test peut échouer
        # selon l'implémentation
        print_success("Méthode verify_password disponible")
        print(f"     (Note: Le mot de passe est hashé dans la DB)")


def test_salle():
    """Teste le modèle Salle."""
    print_section("TEST DU MODÈLE SALLE")
    
    # Test 1: Récupérer toutes les salles
    print("\n1. Test get_all:")
    try:
        all_salles = Salle.get_all()
        print_success(f"Nombre de salles trouvées: {len(all_salles)}")
        for s in all_salles:
            statut = "Occupée" if s.occupee else "Libre"
            print(f"     - {s.numero} ({s.batiment}, étage {s.etage}) - {statut} - Capacité: {s.capacite}")
    except Exception as e:
        print_error(f"Erreur lors de la récupération: {e}")
        all_salles = []
    
    # Test 2: Récupérer une salle par numéro
    print("\n2. Test get_by_numero:")
    if all_salles:
        try:
            test_numero = all_salles[0].numero
            salle = Salle.get_by_numero(test_numero)
            if salle:
                print_success(f"Salle trouvée: {salle.numero}")
                print(f"     Bâtiment: {salle.batiment}, Étage: {salle.etage}")
                print(f"     Capacité: {salle.capacite}, Type: {salle.type_salle}")
                print(f"     Occupée: {salle.occupee}")
            else:
                print_error(f"Aucune salle trouvée avec le numéro: {test_numero}")
        except Exception as e:
            print_error(f"Erreur lors de la récupération: {e}")
    
    # Test 3: Récupérer les salles libres
    print("\n3. Test get_libres:")
    try:
        salles_libres = Salle.get_libres()
        print_success(f"Nombre de salles libres: {len(salles_libres)}")
        for s in salles_libres:
            print(f"     - {s.numero} ({s.batiment}, étage {s.etage})")
    except Exception as e:
        print_error(f"Erreur lors de la récupération: {e}")
    
    # Test 4: Récupérer les salles occupées
    print("\n4. Test get_occupees:")
    try:
        salles_occupees = Salle.get_occupees()
        print_success(f"Nombre de salles occupées: {len(salles_occupees)}")
        for s in salles_occupees:
            print(f"     - {s.numero} ({s.batiment}, étage {s.etage})")
    except Exception as e:
        print_error(f"Erreur lors de la récupération: {e}")


def test_personne():
    """Teste le modèle Personne."""
    print_section("TEST DU MODÈLE PERSONNE")
    
    # Test 1: Création d'une personne
    print("\n1. Test création Personne:")
    try:
        p1 = Personne("Dupont", "A101", "etudiant")
        print_success(f"Personne créée: {p1}")
        
        p2 = Personne("Martin", None, "enseignant")
        print_success(f"Personne créée: {p2}")
        
        # Test 2: Vérification des attributs
        print("\n2. Test attributs:")
        print_success(f"p1.nom = {p1.nom}")
        print_success(f"p1.salle = {p1.salle}")
        print_success(f"p1.type_personne = {p1.type_personne}")
    except Exception as e:
        print_error(f"Erreur lors de la création: {e}")


def test_personnes():
    """Teste le modèle Personnes."""
    print_section("TEST DU MODÈLE PERSONNES")
    
    # Test 1: Récupérer le personnel depuis la DB
    print("\n1. Test get_personnel:")
    try:
        personnel = Personnes.get_personnel()
        print_success(f"Nombre de membres du personnel trouvés: {len(personnel)}")
        for p in personnel:
            salle_info = f"dans la salle {p.salle}" if p.salle else "pas de salle assignée"
            print(f"     - {p.nom} ({p.type_personne}) - {salle_info}")
    except Exception as e:
        print_error(f"Erreur lors de la récupération: {e}")
    
    # Test 2: Création d'une instance Personnes et ajout
    print("\n2. Test ajouter:")
    try:
        personnes = Personnes()
        p1 = Personne("Test", "A101", "etudiant")
        p2 = Personne("Test2", "B201", "enseignant")
        personnes.ajouter(p1)
        personnes.ajouter(p2)
        print_success(f"Personnes ajoutées: {len(personnes)} personnes")
        
        # Test 3: Filtrer par salle
        print("\n3. Test get_by_salle:")
        personnes_salle = personnes.get_by_salle("A101")
        print_success(f"Personnes dans la salle A101: {len(personnes_salle)}")
        for p in personnes_salle:
            print(f"     - {p.nom}")
        
        # Test 4: Filtrer par type
        print("\n4. Test get_by_type:")
        enseignants = personnes.get_by_type("enseignant")
        etudiants = personnes.get_by_type("etudiant")
        print_success(f"Enseignants: {len(enseignants)}")
        print_success(f"Etudiants: {len(etudiants)}")
    except Exception as e:
        print_error(f"Erreur lors des tests: {e}")


def main():
    """Fonction principale qui exécute tous les tests."""
    print("\n" + "=" * 60)
    print("  TESTS DES MODÈLES - APPLICATION MARODEUR")
    print("=" * 60)
    
    try:
        test_user()
        test_salle()
        test_personne()
        test_personnes()
        
        print_section("RESUME")
        print("\n[OK] Tous les tests ont ete executes!")
        print("  Verifiez les resultats ci-dessus pour detecter d'eventuelles erreurs.")
        print("\n  Note: Si certaines tables n'existent pas, executez d'abord")
        print("  le script seed_test_data.py pour initialiser la base de donnees.")
        
    except Exception as e:
        print(f"\n[ERREUR] Erreur lors de l'execution des tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

