# Exemple de Traitement Complet d'une Phrase

## Phrase d'Exemple
**Phrase d'entrée** : "Je voudrais aller de Rennes à Biarritz"

Ce document montre comment cette phrase est traitée étape par étape à travers le pipeline de l'application, depuis la détection de la langue jusqu'à l'optimisation du trajet.

### Étape 1 : Détection de la Langue
**Classe utilisée** : `LanguageIdentification`
- **Objectif** : Vérifier que la phrase est en français avant de procéder.
- **Résultat** :
  - Langue détectée : Français (`__label__fr`)
  - Confiance : 98.76%
- **Sortie** : Phrase validée pour les étapes suivantes.

### Étape 2 : Classification de l'Intention
**Classe utilisée** : `TravelIntentClassifierModel`
- **Objectif** : Déterminer si la phrase contient une intention de voyage.
- **Modèle utilisé** : DistilBERT fine-tuné
- **Résultat** :
  - Intention détectée : **Itinéraire**
  - Prédiction : `1` (phrase liée à un itinéraire)
- **Sortie** : La phrase est confirmée comme étant une demande d'itinéraire, donc on continue le traitement.

### Étape 3 : Extraction de l'Origine et de la Destination
**Classe utilisée** : `CamembertNERModel`
- **Objectif** : Identifier les villes de départ et de destination.
- **Modèle utilisé** : CamemBERT fine-tuné pour la reconnaissance d'entités
- **Résultat** :
  - **Ville de départ** : Rennes
  - **Ville de destination** : Biarritz
- **Sortie** : Les villes de départ et d'arrivée sont extraites avec succès pour l'étape suivante.

### Étape 4 : Optimisation du Trajet
**Classe utilisée** : `SNCFRouteFinder`
- **Objectif** : Trouver le trajet optimal entre Rennes et Biarritz en utilisant les données de la SNCF.
- **Algorithme utilisé** : Dijkstra pour l'optimisation de chemin
- **Résultat** :
  - **Trajet optimal trouvé** :
    - Départ : Rennes
    - Arrêts intermédiaires : Bordeaux
    - Arrivée : Biarritz
  - **Durée totale estimée** : 6h40
- **Sortie** : Trajet optimisé, incluant les informations de temps de voyage et les arrêts intermédiaires.

---

### Résumé du Traitement
1. **Phrase d'entrée** : "Je voudrais aller de Rennes à Biarritz"
2. **Langue détectée** : Français (validation réussie)
3. **Intention détectée** : Demande d'itinéraire (validation réussie)
4. **Extraction des villes** : Rennes (départ), Biarritz (destination)
5. **Optimisation de l'itinéraire** : Trajet optimal passant par Bordeaux, avec une durée de 6h40