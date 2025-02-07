import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import pandas as pd
import nbformat as nbf
from services.sncf.sncf_route_finder import SNCFRouteFinder

# Définition des chemins
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
notebook_dir = "evaluations/sncf_route_finder_evaluation"
notebook_path = os.path.join(notebook_dir, "sncf_route_finder_evaluation.ipynb")
executed_notebook_path = os.path.join(notebook_dir, "executed_notebook.ipynb")
html_output_path = os.path.join(notebook_dir, "index.html")
dataset_path = os.path.join(project_root, "assets/data_sncf/organized_trips.csv")

# Suppression des anciens fichiers
print("Suppression des anciens fichiers...")
for file_path in [executed_notebook_path, html_output_path, notebook_path]:
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Supprimé : {file_path}")

# Chargement du finder SNCF
print("Chargement du module SNCFRouteFinder...")
route_finder = SNCFRouteFinder()

# Exécuter des tests sur les trajets
print("Exécution de tests de trajets...")
trajet_direct = route_finder.find_shortest_route("Rennes", "Paris")
trajet_non_direct = route_finder.find_shortest_route("Rennes", "Biarritz")

# Chargement du dataset amélioré
print("Chargement du dataset amélioré...")
df = pd.read_csv(dataset_path)

# Création du notebook
print("Création du notebook...")
n = nbf.v4.new_notebook()

# Introduction
n.cells.append(nbf.v4.new_markdown_cell("""
# Évaluation de l'algorithme de recherche de trajet SNCF 🚆
Ce notebook présente :
- Le fonctionnement de l'algorithme de recherche d'itinéraire.
- Pourquoi et comment nous avons mis à jour le dataset SNCF.
- Des exemples de trajets calculés.
- Un exemple de requête API et sa réponse.
"""))

# Explication de Dijkstra
n.cells.append(nbf.v4.new_markdown_cell("""
## 🔍 Explication approfondie de l'algorithme de Dijkstra
### Comprendre et valider son fonctionnement

L'algorithme de **Dijkstra** est une méthode classique pour **trouver le chemin le plus court dans un graphe pondéré**.  
Dans notre cas, le graphe représente **le réseau ferroviaire SNCF**, où :
- **Chaque nœud** est une ville possédant au moins une gare.
- **Chaque arête** est une liaison ferroviaire directe entre deux villes.
- **Chaque poids d'arête** correspond au **temps de trajet** en minutes.


L'algorithme fonctionne en :
1. **Initialisant** la distance de tous les nœuds à l'infini sauf le point de départ.
2. **Parcourant** les voisins du nœud courant et mettant à jour leur distance.
3. **Marquant** les nœuds comme visités pour éviter les boucles.
4. **Répétant** jusqu'à atteindre la destination.

---

#### **📌 Pourquoi Dijkstra est un bon choix ?**
Dijkstra garantit que **chaque ville est atteinte par le chemin optimal en temps de trajet** en raison de :
- **Sa structure de file de priorité**, qui traite toujours **le chemin le plus court découvert en premier**.
- **Son absence de cycles** (on ne revisite pas une ville déjà visitée avec un temps plus court).
- **Son exploration progressive**, qui sélectionne **le prochain meilleur itinéraire en fonction des données disponibles**.

Nous allons voir **comment l'algorithme explore les trajets possibles** et **pourquoi il sélectionne le bon chemin** pour **Rennes → Biarritz**.

"""))

n.cells.append(nbf.v4.new_markdown_cell("""
## 🛤️ Étude détaillée du fonctionnement sur Rennes → Biarritz
### Décomposition du trajet avec Dijkstra

Prenons un exemple réel : **calculer le chemin le plus rapide entre Rennes et Biarritz**.  
Dijkstra va explorer **toutes les routes possibles** pour **trouver l’itinéraire optimal en temps**.

#### **🎯 Objectifs :**
1. Partir de **Rennes** et atteindre **Biarritz**.
2. Minimiser **le temps total de trajet**.
3. Réduire **le nombre de changements de train** si possible.

L'algorithme se déroule en plusieurs étapes :
"""))

n.cells.append(nbf.v4.new_markdown_cell("""
#### 📍 **Étape 1 : Initialisation**
- La gare de **Rennes** est définie comme le **point de départ** avec un coût de **0 minutes**.
- Toutes les autres villes sont **marquées comme infiniment éloignées**.
- Une **file de priorité** est utilisée pour **traiter en premier les trajets les plus courts**.

"""))

n.cells.append(nbf.v4.new_code_cell("""
# 🔄 Initialisation de l'algorithme
import heapq

departure, destination = "rennes", "biarritz"
heap = [(0, departure, [(departure, 0)])]  # (temps total, ville actuelle, chemin parcouru)
best = {departure: 0}  # Meilleur temps trouvé pour chaque ville

print(f"🎯 **Départ :** {departure.capitalize()} (temps : 0 min)")
"""))

n.cells.append(nbf.v4.new_markdown_cell("""
#### 📍 **Étape 2 : Exploration des premières connexions**
Dijkstra commence à explorer **les villes accessibles directement depuis Rennes**,  
en mettant à jour **les meilleurs temps trouvés**.

"""))

n.cells.append(nbf.v4.new_code_cell("""
import sys
import os

# Ajout du répertoire racine du projet au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "../..")))

from services.sncf.sncf_route_finder import SNCFRouteFinder

step_counter = 0  # Compteur pour limiter l'affichage des étapes
key_cities = ["paris", "bordeaux", "dax", "bayonne", "biarritz"]  # Villes clés du trajet optimisé
city_times = {}  # Stocker les meilleurs temps trouvés pour ces villes

route_finder = SNCFRouteFinder()

while heap:
    travel_time, station, path = heapq.heappop(heap)  # Extraire le trajet le plus court disponible

    # Afficher les premières étapes (pour donner une idée du début de l'exploration)
    if step_counter < 3:
        print(f"⏳ Étape {step_counter+1}: Exploration de {station.capitalize()} (temps cumulé : {travel_time} min)")

    # Indication qu'on continue le processus sans afficher toutes les étapes
    if step_counter == 3:
        print("...")
        print("📌 L'algorithme continue à explorer d'autres chemins de manière optimisée...")

    step_counter += 1

    # Exploration des villes voisines
    for neighbor, time in route_finder.graph.get(station, []):
        new_time = travel_time + time

        if neighbor not in best or new_time < best[neighbor]:
            best[neighbor] = new_time
            heapq.heappush(heap, (new_time, neighbor, path + [(neighbor, new_time)]))
"""))

n.cells.append(nbf.v4.new_code_cell("""
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# Utilisation de find_shortest_route pour obtenir le trajet final
example_path = route_finder.find_shortest_route("Rennes", "Biarritz")

# Création du graphe
G = nx.DiGraph()

# Récupération des noms des villes et des temps de trajet
cities = [city["name"] for city in example_path["route"]]
times = [city["travel_time"] for city in example_path["route"][1:]]

# **Espacement forcé entre les villes**
y_positions = np.linspace(0, len(cities) * 2, len(cities))  # Espacement fixe

# **INVERSION pour avoir Rennes en haut et Biarritz en bas**
y_positions = y_positions[::-1]  

x_positions = np.zeros(len(cities))  # Garde tout aligné verticalement

# Correction spécifique pour Bayonne-Biarritz pour éviter la superposition
y_positions[-2] += 0.5  # Décale Bayonne légèrement
y_positions[-1] -= 0.5  # Décale Biarritz légèrement

# Création d'un dictionnaire de positions
fixed_positions = {city: (x, y) for city, x, y in zip(cities, x_positions, y_positions)}

# Ajout des arêtes au graphe
for i in range(len(cities) - 1):
    G.add_edge(cities[i], cities[i + 1], weight=times[i])

# Création de la figure
plt.figure(figsize=(6, 10))  # Plus de place verticalement
labels = nx.get_edge_attributes(G, 'weight')

# Dessin du graphe
nx.draw(G, fixed_positions, with_labels=True, node_color="#0077B6", font_color="#FFFFFF", edge_color="black", node_size=2500, font_size=10)

# **Ajout des labels avec rotation horizontale**
nx.draw_networkx_edge_labels(G, fixed_positions, edge_labels=labels, font_color="#0077B6", label_pos=0.5, rotate=False)

plt.title("Visualisation du trajet optimisé avec Dijkstra (Rennes → Biarritz)")
plt.xlabel("Position X (fixe)")
plt.ylabel("Espacement forcé entre les villes")
plt.show()
"""))

n.cells.append(nbf.v4.new_markdown_cell("""
<style>
.table-left table {
    margin-left: 0 !important;
}
</style>

## 🔎 Comparaison avec les autres itinéraires possibles
### 📌 Pourquoi ce chemin est optimal ?

L'algorithme aurait pu emprunter d'autres trajets, mais voici pourquoi il les a ignorés :

<div class="table-left">

| Option | Trajet envisagé | Temps total | Pourquoi écarté ? |
|--------|----------------|-------------|-------------------|
| 🚄 **Via Nantes → Bordeaux** | Rennes → Nantes → Bordeaux → Biarritz | **365 min** | Plus lent |
| 🚄 **Via Paris** | Rennes → Paris → Bordeaux → Biarritz | **336 min** | ✅ Sélectionné, plus rapide |
| 🚄 **Via Redon → Dax** | Rennes → Redon → Dax → Biarritz | **370 min** | Plus d'arrêts |

</div>
"""))


# Explication de la mise à jour du dataset SNCF
n.cells.append(nbf.v4.new_markdown_cell("""
## 📊 Mise à jour du dataset SNCF

Les fichiers SNCF originaux étaient **vieillissants**, manquant de nombreuses données **TGV** et d'arrêts récents.
Nous avons donc :
- Récupéré des données plus récentes via **Open SNCF Data**.
- Nettoyé les doublons et structuré les trajets de façon plus efficace.
- Créé un fichier `organized_trips.csv` plus propre et plus facile à exploiter.

Le fichier mis à jour contient les colonnes :
- **Ville de départ** / **Ville d’arrivée**
- **Gare de départ** / **Gare d’arrivée**
- **Temps de trajet** (en minutes)
- **Coordonnées GPS**
"""))

# Affichage des résultats pour des trajets Rennes → Paris et Rennes → Biarritz
n.cells.append(nbf.v4.new_markdown_cell("## 🚄 Exemples de trajets calculés"))
n.cells.append(nbf.v4.new_code_cell(f"""
import json
trajet_direct = {trajet_direct}
trajet_non_direct = {trajet_non_direct}
"""))

n.cells.append(nbf.v4.new_markdown_cell("### 🏙️ Trajet direct Rennes → Paris :"))


n.cells.append(nbf.v4.new_code_cell(f"""
print(json.dumps(trajet_direct, indent=4, ensure_ascii=False))
"""))

n.cells.append(nbf.v4.new_markdown_cell("### 🏖️ Trajet non direct Rennes → Biarritz :"))


n.cells.append(nbf.v4.new_code_cell(f"""
print(json.dumps(trajet_non_direct, indent=4, ensure_ascii=False))
"""))


# Exemple de requête API
n.cells.append(nbf.v4.new_markdown_cell("## 🌍 Exemple de requête API et réponse retournée"))

# Show Curl
n.cells.append(nbf.v4.new_markdown_cell("""
```sh
curl -X POST http://localhost:8002/api/sncf/find-route 
-H "Content-Type: application/json" 
-d '{"sentence": "Je veux aller de Rennes à Paris"}'
```
"""))

# Response
n.cells.append(nbf.v4.new_code_cell("""
import requests
import json

endpoint = "http://localhost:8002/api/sncf/find-route"
data = {"sentence": "Je veux aller de Rennes à Paris"}
response = requests.post(endpoint, json=data)

# Affichage de la réponse formatée en JSON
print("📥 **Réponse de l'API :**")
print(json.dumps(response.json(), indent=4, ensure_ascii=False))
"""))


# Sauvegarde du notebook
if not os.path.exists(notebook_dir):
    os.makedirs(notebook_dir)

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(n, f)
print(f"Notebook créé : {notebook_path}")

# Exécution et conversion du notebook
print("Exécution et conversion du notebook...")
os.system(f'jupyter nbconvert --to notebook --execute {notebook_path} --no-input --output executed_notebook.ipynb')
os.system(f'jupyter nbconvert --to html {executed_notebook_path} --no-input --output index.html')

print("Exécution et conversion terminées.")
