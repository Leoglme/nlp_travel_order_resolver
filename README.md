# Travel Order Resolver
### Projet de Traitement d'Itinéraires en Langue Naturelle

## Description

Ce projet est une application de traitement du langage naturel (NLP) destinée à interpréter et traiter des demandes d'itinéraires en français. Le programme permet de détecter des intentions de voyage, d'extraire les villes de départ et d'arrivée, et d'optimiser le trajet en s'appuyant sur des données de réseau de transport SNCF. Les principales fonctionnalités incluent la reconnaissance vocale, la détection de la langue, la classification d'intention, l'extraction d'entités nommées et la recherche de trajet optimal.

## Fonctionnalités

- **Reconnaissance Vocale** : Conversion de la voix en texte pour les entrées audio.
- **Détection de la Langue** : Vérifie que la demande est en français avant de la traiter.
- **Classification de l'Intention** : Identifie les intentions de voyage.
- **Extraction de Villes** : Identifie les villes de départ et de destination dans le texte.
- **Optimisation de l'Itinéraire** : Trouve le meilleur trajet entre les villes de départ et de destination en utilisant les données SNCF.

## Prérequis

Avant de commencer, assurez-vous d'avoir les éléments suivants installés :

- Python 3 ou supérieur
- Pip pour gérer les paquets Python
- Virtualenv (optionnel mais recommandé pour gérer l'environnement de développement)

## Installation

Clonez le dépôt, puis installez les dépendances nécessaires.

```bash
git clone https://github.com/Leoglme/nlp_travel_order_resolver
cd nlp_travel_order_resolver
```

Créez un environnement virtuel (optionnel mais recommandé) :

```bash
python -m venv env
source env/bin/activate  # Pour Linux/macOS
# ou
env\Scripts\activate.bat  # Pour Windows
```

Ensuite, installez les dépendances requises :

```bash
pip install -r requirements.txt
```

## Utilisation

L'application peut être utilisée via le terminal ou en exposant des endpoints d'API REST.

### Utilisation depuis le Terminal

Lancez l'application en exécutant `main.py` et en fournissant des entrées texte ou audio.

```bash
python main.py
```

- **Texte** : Saisissez directement la demande au format texte, comme "Je veux aller de Rennes à Biarritz".
- **Audio** : Fournissez un fichier audio ou utilisez le microphone pour enregistrer une demande.

Exemples de commandes :

- Entrée de texte (modifiez `text_from_microphone` directement dans le code pour utiliser du texte en dur).
- Utilisation du microphone pour capturer une phrase parlée.

### Utilisation de l'API REST

L'API est construite avec FastAPI et offre plusieurs endpoints pour interagir avec le modèle via des requêtes HTTP.

1. **Démarrez le serveur API** :

   ```bash
   uvicorn api.app:app --reload
   ```

2. **Endpoints principaux** :

   - `POST /api/audio-to-text` : Convertit un fichier audio en texte.
     - **Paramètres** : Un fichier audio (`.wav`, `.mp3`).
     - **Exemple** :

       ```bash
       curl -X POST "http://127.0.0.1:8000/api/audio-to-text" -F "file=@path/to/your/audiofile.wav"
       ```

   - `POST /api/validate-travel-intent` : Valide si la phrase est en français et contient une intention d'itinéraire.
     - **Paramètres** : JSON avec une clé `sentence`.
     - **Exemple** :

       ```bash
       curl -X POST "http://127.0.0.1:8000/api/validate-travel-intent" -H "Content-Type: application/json" -d '{"sentence": "Je veux aller de Rennes à Biarritz"}'
       ```

   - `POST /api/sncf/find-route` : Extrait les villes de départ et de destination et fournit l'itinéraire optimal.
     - **Paramètres** : JSON avec une clé `sentence`.
     - **Exemple** :

       ```bash
       curl -X POST "http://127.0.0.1:8000/api/sncf/find-route" -H "Content-Type: application/json" -d '{"sentence": "Je veux aller de Rennes à Biarritz"}'
       ```

### Fonctionnement du Traitement d'une Demande

Exemple de traitement complet pour la phrase : "Je voudrais aller de Rennes à Biarritz".

1. **Détection de Langue** : Vérifie que la phrase est en français (avec FastText).
2. **Classification d'Intention** : Identifie l'intention de voyage (avec `TravelIntentClassifierModel` fine-tuné sur DistilBERT).
3. **Extraction de Villes** : Extrait les villes de départ et d'arrivée, ici Rennes et Biarritz (avec `CamembertNERModel`).
4. **Optimisation de l'Itinéraire** : Fournit le meilleur trajet via Dijkstra en utilisant les données SNCF, avec Bordeaux comme arrêt intermédiaire et une estimation de la durée totale du trajet.

## Structure du Projet

- **main.py** : Point d'entrée pour exécuter l'application depuis le terminal.
- **api/app.py** : Définit les endpoints REST de l'API avec FastAPI.
- **models/** : Contient les modèles NLP, y compris `TravelIntentClassifierModel` et `CamembertNERModel`.
- **services/** : Implémente les services de traitement, notamment la reconnaissance vocale, la détection de langue, et l'optimisation d'itinéraire.
- **datasets/** : Contient les jeux de données utilisés pour entraîner les modèles.
- **assets/** : Contient les données additionnelles, comme les modèles de détection de langue FastText.
- **logs/** : Contient les fichiers de log générés lors de l'entraînement.

## Entraînement des Modèles

Pour réentraîner les modèles, vérifiez que vous disposez des fichiers de jeu de données dans `datasets/`. Vous pouvez alors lancer l'entraînement en modifiant les scripts des modèles dans `models/` :

- **Classification d'Intention** : `TravelIntentClassifierModel` entraîne un modèle DistilBERT pour classifier les intentions.
- **Extraction de Villes** : `CamembertNERModel` entraîne un modèle CamemBERT pour la reconnaissance des villes de départ et d'arrivée.

Chaque modèle est entraîné avec des paramètres spécifiques (taux d’apprentissage, nombre d’époques) pour garantir la précision.

## Documentation
Pour mieux comprendre le fonctionnement de l'application, vous pouvez consulter la documentation détaillée dans le dossier `documentation/`.


## Contribuer

Les contributions sont les bienvenues ! Pour contribuer :

1. **Fork** le dépôt.
2. **Clone** le dépôt forké localement.
3. Créez une **branche** pour vos modifications (`git checkout -b feature/nom-de-fonctionnalité`).
4. **Commit** vos modifications (`git commit -m 'Ajout d'une fonctionnalité'`).
5. **Push** sur la branche (`git push origin feature/nom-de-fonctionnalité`).
6. Ouvrez une **Pull Request** pour revue.

## Licence

Ce projet est sous licence MIT.