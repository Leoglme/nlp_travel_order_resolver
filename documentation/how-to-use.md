<div align="center" style="margin-top: 24px">
  <img src="https://dibodev-files.s3.eu-west-3.amazonaws.com/epitrip-logo.svg" alt="Logo" width="140" />
</div>

# Comment fonctionne l'application ? 🚆

### Découvrez comment utiliser notre application pour rechercher un itinéraire en quelques secondes.

Notre application vous permet de rechercher un trajet de manière simple et intuitive. Il vous suffit d'écrire ou de dicter une phrase indiquant votre itinéraire, et nous nous occupons du reste ! ✨  

## 🎤 Saisie de l'itinéraire  

Sur la page d'accueil, vous trouverez un champ de texte avec le message :  

> **"Quel trajet voulez-vous faire ?"**  

Vous avez deux possibilités pour renseigner votre trajet :  

1. **Écrire directement** votre phrase dans le champ texte.  
2. **Utiliser la dictée vocale** 🎙️ en appuyant sur le bouton vert avec un micro.  

Exemples de phrases valides :  
- *"Je pars de Rennes pour aller à Biarritz."*  
- *"Trouve-moi un train de Bordeaux à Paris."*  

![Capture de la page d'accueil](https://dibodev-files.s3.eu-west-3.amazonaws.com/home-work.gif)

---

## 🚀 Recherche de l'itinéraire  

Une fois la phrase entrée, il suffit d'appuyer sur le bouton **"GO"** ✅.  

L'application va alors :  
1. Vérifier si la phrase parle bien d'un trajet 🏷️.  
2. Extraire la ville de départ et la ville d'arrivée 📍.  
3. Trouver le meilleur trajet possible en utilisant les données de la SNCF.  

Vous serez ensuite redirigé vers la page des résultats.

---

## 🗺️ Affichage de l'itinéraire  

Sur la page `/map?q=je+pars+de+Rennes+pour+aller+à+Biarritz`, vous verrez :  

- **À gauche :** Le résumé de votre itinéraire, incluant :  
  - 🚉 **Départ → Arrivée**  
  - ⏳ **Durée totale du trajet**  
  - 📌 **Liste des arrêts avec leurs durées respectives**  

- **À droite :** Une carte interactive 🗺️ affichant le trajet en temps réel avec un marqueur pour chaque arrêt. Vous pouvez zoomer, déplacer la carte et cliquer sur un arrêt pour voir son nom et le temps depuis la gare précédente.

![Capture de la page trajet](https://dibodev-files.s3.eu-west-3.amazonaws.com/map.png)

---

## 🎯 Exemple d'itinéraire Rennes → Biarritz  

| 🛤️ Gare        | ⏳ Durée depuis la précédente |
|---------------|-------------------------|
| **Rennes**      | Départ |
| **Bruz**       | 6 min |
| **Guichen**    | 4 min |
| **Guipry-Messac** | 8 min |
| **Langon**     | 7 min |
| **Cérons**     | 7 min |
| **Beautiran**  | 7 min |
| **Bordeaux**   | 1h 8m |
| **Dax**        | 28 min |
| **Bayonne**    | 25 min |
| **Biarritz**   | Arrivée |

💡 *Chaque arrêt est marqué sur la carte, et un clic affiche son nom et la durée de voyage depuis la gare précédente.*

---

## 🔥 Pourquoi utiliser cette application ?  

✅ **Simple et rapide** : Tapez ou dictez votre trajet en langage naturel.  
✅ **Intelligent** : L'IA comprend votre phrase et trouve automatiquement le bon itinéraire.  
✅ **Interactif** : Visualisez le trajet sur une carte avec des détails précis.  

