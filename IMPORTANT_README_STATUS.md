# Problème avec les statuts des assignements

## État actuel :
- Les 7 assignements ont leur statut correctement défini dans `data/eco-ontology.rdf` :
  - RNewAssignment1 : approuvé
  - RNewAssignment2 : rejeté
  - RAssignment3 : approuvé  
  - RAssignment4 : approuvé
  - RAssignment5 : rejeté
  - RAssignment6 : rejeté
  - RAssignment7 : approuvé

- Le code Python dans `backend/modules/gemini_sparql_service.py` est correct (utilise CONTAINS pour filtrer les statuts).

## Problème :
Les propriétés `status` ne sont pas chargées dans Fuseki même après avoir ajouté `rdf:datatype="http://www.w3.org/2001/XMLSchema#string"`.

## Solution temporaire :
Ajouter manuellement les statuts via l'interface Fuseki (http://localhost:3030) avec cette requête UPDATE :

```sparql
PREFIX webprotege: <http://webprotege.stanford.edu/>
INSERT DATA {
    <http://webprotege.stanford.edu/RNewAssignment1> webprotege:RDT3XEARggTy1BIBKDXXrmx "approuvé" .
    <http://webprotege.stanford.edu/RNewAssignment2> webprotege:RDT3XEARggTy1BIBKDXXrmx "rejeté" .
    <http://webprotege.stanford.edu/RAssignment3> webprotege:RDT3XEARggTy1BIBKDXXrmx "approuvé" .
    <http://webprotege.stanford.edu/RAssignment4> webprotege:RDT3XEARggTy1BIBKDXXrmx "approuvé" .
    <http://webprotege.stanford.edu/RAssignment5> webprotege:RDT3XEARggTy1BIBKDXXrmx "rejeté" .
    <http://webprotege.stanford.edu/RAssignment6> webprotege:RDT3XEARggTy1BIBKDXXrmx "rejeté" .
    <http://webprotege.stanford.edu/RAssignment7> webprotege:RDT3XEARggTy1BIBKDXXrmx "approuvé" .
}
```

## À faire :
1. Redémarrer Fuseki complètement
2. Recharger les données
3. Vérifier que les statuts sont présents

