#!/bin/bash
# Script pour sauvegarder et pousser vers la branche firas

echo "=== Ajout des fichiers modifiés ==="
git add data/eco-ontology.rdf backend/modules/gemini_sparql_service.py backend/modules/assignments.py backend/modules/volunteers.py backend/modules/reservations.py backend/modules/certifications.py

echo ""
echo "=== Création/switch vers la branche firas ==="
git checkout -b firas 2>/dev/null || git checkout firas

echo ""
echo "=== Commit des changements ==="
git commit -m "Fix volunteers queries and add status properties to assignments

- Fix volunteer experience display (reorder columns)
- Fix volunteer skills query (remove FILTER outside WHERE)
- Change assignment status values from 'approuvé'/'rejeté' to 'approved'/'rejected' to fix Fuseki encoding issue
- Add status properties: 4 approved, 3 rejected assignments
- Update SPARQL filters to handle both French and English status values"

echo ""
echo "=== Push vers la branche firas ==="
git push -u origin firas

echo ""
echo "✅ Travail sauvegardé et pushé vers la branche firas!"

