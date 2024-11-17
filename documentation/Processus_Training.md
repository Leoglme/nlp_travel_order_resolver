# Processus de Formation des Modèles

### 1. **Description des Jeux de Données Utilisés**

#### Jeu de Données de Classification d'Intention
- **Fichier** : `datasets/travel_intent_dataset.csv`
- **Format** : Ce jeu de données contient deux colonnes :
  - `text` : phrases en français indiquant des intentions diverses, dont certaines sont liées à des itinéraires.
  - `label` : une étiquette binaire (`1` pour une intention liée à un itinéraire, `0` pour une intention non liée).
- **Exemple** :
  - `text` : "Elle cherche un itinéraire jusqu'à Nice à Paris"
  - `label` : `1`
  
Ce jeu de données est utilisé pour entraîner le modèle `TravelIntentClassifierModel`, chargé de classifier les phrases en fonction de leur intention (itinéraire ou non).

#### Jeu de Données de Reconnaissance d'Entités Nommées (NER)
- **Fichier** : `datasets/camembert_ner_dataset.csv`
- **Format** : Trois colonnes :
  - `text` : phrases en français décrivant des trajets.
  - `departure` et `destination` : les villes de départ et d'arrivée extraites de chaque phrase.
- **Exemple** :
  - `text` : "Je veux aller de Biarritz à Marseille"
  - `departure` : `Biarritz`
  - `destination` : `Marseille`
  
Ce jeu de données est utilisé pour entraîner le modèle `CamembertNERModel`, spécialisé dans la reconnaissance d'entités nommées, afin d'extraire les villes de départ et d'arrivée dans les phrases.

### 2. **Paramètres Utilisés pour l’Entraînement**

#### Modèle de Détection de Langue (LanguageIdentification - FastText)
- **Classe** : `LanguageIdentification`
- **Modèle** : `FastText` pré-entraîné pour la détection de langue (`lid.176.bin`)
- **Seuil de Confiance Minimum** : 70%
  
Ce modèle de détection de langue est utilisé pour s'assurer que les phrases sont en français avant de les traiter pour l’analyse d’intention ou d’itinéraire. `FastText` est efficace pour la classification rapide de langues et permet d'obtenir une haute précision en vérifiant si le texte est en français.

#### Modèle de Classification d'Intention (TravelIntentClassifierModel - DistilBERT Fine-tuning)
- **Classe** : `TravelIntentClassifierModel`
- **Modèle** : `distilbert-base-uncased`, un modèle léger de la famille BERT.
- **Paramètres d’entraînement** :
  - **Taille du batch** : 16
  - **Nombre d'étiquettes de sortie** : 2 (binaire pour "itinéraire" et "non-itinéraire")
  - **Nombre d'époques** : 20
  - **Taux d’apprentissage** : 2e-5
  - **Répertoire de sortie** : `./model_output/travel_intent_classifier`
  - **Log** : répertoire de journalisation `./logs/travel_intent_classifier`

Ce modèle est entraîné pour classifier les phrases en fonction de leur intention, en utilisant le jeu de données de classification d'intention. DistilBERT a été choisi pour sa rapidité et son efficacité, tout en conservant des performances proches de BERT pour des tâches de classification simples.

#### Modèle de Reconnaissance d'Entités Nommées (CamembertNERModel - CamemBERT Fine-tuning)
- **Classe** : `CamembertNERModel`
- **Modèle** : `camembert-base`, un modèle pré-entraîné pour le français.
- **Paramètres d’entraînement** :
  - **Taille du batch** : 4
  - **Nombre d'époques** : 20
  - **Taux d’apprentissage** : 2e-5
  - **Nombre d’étiquettes** : 5 (B-DEP, I-DEP pour départ, B-ARR, I-ARR pour arrivée, O pour autres mots)
  - **Répertoire de sortie** : `./model_output/camembert_ner`
  - **Log** : répertoire de journalisation `./logs/camembert_ner`

Ce modèle NER est affiné pour reconnaître les villes de départ et d'arrivée dans des phrases en français. CamemBERT a été choisi pour sa spécialisation en traitement du français, ce qui améliore la précision pour la tâche NER.

### 3. **Préparation et Nettoyage des Données**

#### Modèle de Classification d'Intention (`TravelIntentClassifierModel`)
- **Tokenisation** : Les phrases sont tokenisées avec `DistilBertTokenizerFast`, en utilisant un padding et une troncation pour garantir une longueur constante des séquences.
- **Préparation des Données** : Le jeu de données CSV est chargé et divisé en ensembles d’entraînement et de test. Chaque phrase est ensuite transformée en tokens et labels correspondants.
- **Évaluation des Performances** : Les performances du modèle sont mesurées par des métriques standard telles que la précision, le rappel, le F1-score et l'exactitude.

#### Modèle de Reconnaissance d'Entités Nommées (`CamembertNERModel`)
- **Alignement des Étiquettes** : Les phrases sont tokenisées avec `CamembertTokenizerFast`, et les entités de départ et d'arrivée sont alignées avec les tokens générés.
- **Assignation des Étiquettes** : Un système de tags (B-DEP, I-DEP, B-ARR, I-ARR, O) est appliqué, identifiant les entités `departure` et `destination` dans chaque phrase. Les tokens non pertinents reçoivent un tag `O`.
- **Évaluation des Performances** : Utilisation de `seqeval` pour calculer les métriques (précision, rappel, F1-score et exactitude) sur les entités reconnues.

### 4. **Optimisation et Ajustements**

- **LanguageIdentification** : Un seuil de confiance de 70% a été choisi pour garantir que seuls les textes en français passent aux étapes de classification d’intention et d’extraction d’entités.
- **TravelIntentClassifierModel** : Des ajustements mineurs ont été faits, tels que la régularisation via le `weight_decay` pour éviter le surapprentissage.
- **CamembertNERModel** : Une réduction de la taille du batch (4) a été nécessaire pour gérer la complexité des séquences en français et leur alignement.
- **Problèmes rencontrés** :
  - **Désalignement des entités** : Des ajustements sur les étiquettes de NER ont permis de mieux aligner les tokens sur les entités pour le modèle NER.
  - **Optimisation du taux d'apprentissage** : Des expérimentations ont montré qu’un taux de 2e-5 était idéal pour éviter le surapprentissage et maximiser les performances.

### 5. **Résumé des Résultats**

Les modèles, après entraînement, permettent de :
- **LanguageIdentification** : détecter si les phrases sont en français avec une haute confiance avant de passer aux étapes de classification.
- **TravelIntentClassifierModel** : classifier les phrases en intentions liées aux trajets avec une haute précision.
- **CamembertNERModel** : extraire les villes de départ et de destination avec des performances stables.