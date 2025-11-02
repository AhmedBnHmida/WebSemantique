import os
import shutil

# Supprimer tous les __pycache__
dirs_to_remove = [
    'backend/__pycache__',
    'backend/modules/__pycache__'
]

for dir_path in dirs_to_remove:
    if os.path.exists(dir_path):
        print(f"Suppression de {dir_path}...")
        shutil.rmtree(dir_path)
        print(f"  ✅ {dir_path} supprimé")
    else:
        print(f"  ⏭️  {dir_path} n'existe pas")

print("\nNettoyage terminé!")

