# 📌 **Analyse et justification des choix de modèles**  

## 🛤️ Introduction  
Dans ce projet, nous avons dû faire des choix cruciaux concernant les modèles NLP utilisés pour accomplir deux tâches principales :  

1. **Reconnaissance d'entités nommées (NER)** pour extraire les villes de départ et d'arrivée dans une phrase.  
2. **Classification d'intention** pour déterminer si une phrase fait référence à un trajet ou non.  
3. **Détection de la langue** pour filtrer les requêtes avant traitement.  

L'objectif était de trouver le bon équilibre entre **précision, rapidité, et efficacité** tout en s'assurant que les modèles soient bien adaptés aux données en français. 🔥  

---

## 🔍 **Comparaison des modèles pour la NER (Reconnaissance d'entités nommées)**  

La reconnaissance d'entités nommées (NER) est un défi important en NLP, surtout lorsqu’il s'agit d'identifier des **villes dans des phrases naturelles**. Nous avons comparé plusieurs approches avant de choisir **CamemBERT** comme solution optimale.  

### 📊 **Comparaison des modèles pour la NER**  

| Modèle          | Langue | Performance sur le français | Adaptabilité aux tâches NER | Temps d'inférence | Besoin de fine-tuning |
|----------------|--------|----------------------------|----------------------------|-------------------|----------------------|
| **SpaCy (fr_core_news_md)** | 🇫🇷 Français | Moyenne (pré-entraîné) | Faible | ⚡ Très rapide | ❌ Non fine-tunable facilement |
| **DistilBERT** | 🌍 Multilingue | Bonne | Moyenne | ⚡ Rapide | ✅ Fine-tunable |
| **CamemBERT** | 🇫🇷 Français | **Excellente** | **Très élevée** | 🐢 Plus lent | ✅ Fine-tunable |
| **Flair (NER-fr)** | 🇫🇷 Français | Très bonne | Bonne | ⚡ Rapide | ✅ Fine-tunable |

### 🏆 **Pourquoi avons-nous choisi CamemBERT ?**  
✅ **Spécifiquement conçu pour le français** : Contrairement à DistilBERT, CamemBERT a été **pré-entraîné sur des corpus massifs en français**, ce qui le rend bien plus précis dans la reconnaissance des entités en français.  
✅ **Meilleure précision sur les villes** : Lors des tests, CamemBERT a mieux différencié les villes du reste du texte.  
✅ **Fine-tuning efficace** : Il est bien optimisé pour des tâches NER complexes et offre une précision nettement supérieure après entraînement.  

Cependant, **son principal inconvénient** est son **temps d’inférence plus lent**, mais dans notre cas, la précision était le critère le plus important.  

---

## 🔎 **Comparaison des modèles pour la classification d'intention (TravelIntentClassifier)**  

La classification d’intention consiste à déterminer si une phrase parle d’un **trajet** ou non. Pour cela, nous avons comparé plusieurs approches.  

### 📊 **Comparaison des modèles pour la classification d'intention**  

| Modèle          | Langue | Précision moyenne | Rapidité d'inférence | Besoin de fine-tuning | Explicabilité |
|----------------|--------|-------------------|----------------------|----------------------|--------------|
| **Logistic Regression (TF-IDF)** | 🌍 Multilingue | 85-90% | ⚡ Très rapide | ❌ Pas de fine-tuning | ✅ Très explicable |
| **SpaCy TextCat** | 🇫🇷 Français | 89-92% | ⚡ Très rapide | ❌ Pré-entraîné uniquement | ✅ Facile à expliquer |
| **FastText** | 🌍 Multilingue | **95-97%** | ⚡⚡ Ultra-rapide | ✅ Option de fine-tuning | ✅ Explicite |
| **DistilBERT** | 🌍 Multilingue | **98.3%** ✅ | 🐢 Plus lent | ✅ Fine-tunable | ❌ Boîte noire |

### 🏆 **Pourquoi avons-nous choisi DistilBERT ?**  
✅ **Excellente précision (98.3%)** sur notre dataset d’entraînement et de test.  
✅ **Modèle léger et optimisé** : DistilBERT offre 97% des performances de BERT tout en étant **40% plus petit**.  
✅ **Capacité à capturer des nuances complexes** : Contrairement aux modèles statistiques comme TF-IDF, DistilBERT comprend mieux le contexte des phrases.  

🚀 **Résultats du modèle** après fine-tuning sur notre dataset :  

- **Accuracy** : `98.33%`  
- **Precision** : `98.33%`  
- **Recall** : `98.33%`  
- **F1-Score** : `98.30%`  

Cependant, **le principal inconvénient** de DistilBERT est son **temps d’inférence plus long** par rapport à FastText.  

---

## 🌎 **Comparaison des modèles pour la détection de langue**  

Pour détecter la langue des phrases entrantes et éviter des erreurs d’analyse, nous avons comparé plusieurs solutions.  

### 📊 **Comparaison des modèles pour la détection de langue**  

| Modèle          | Langues supportées | Précision | Rapidité | Entraînement nécessaire ? | Explicabilité |
|----------------|-------------------|----------|---------|-----------------|--------------|
| **FastText (lid.176.bin)** | 🌍 176 langues | **99%** ✅ | ⚡⚡⚡ Ultra-rapide | ❌ Déjà pré-entraîné | ✅ Explicable |
| **LangDetect (Python)** | 🌍 55 langues | 85-90% ❌ | ⚡ Rapide | ❌ Déjà pré-entraîné | ✅ Explicable |
| **Google Translate API** | 🌍 Toutes les langues | **99%** ✅ | ⚡⚡ Rapide | ❌ Service payant | ❌ Boîte noire |
| **CLD2 (Chrome)** | 🌍 80+ langues | 90-95% ❌ | ⚡ Très rapide | ❌ Déjà pré-entraîné | ✅ Explicable |

### 🏆 **Pourquoi avons-nous choisi FastText ?**  
✅ **Déjà pré-entraîné sur 176 langues**, ce qui le rend **très performant sur le français et les langues similaires**.  
✅ **Ultra-rapide** : Il peut traiter des milliers de phrases en quelques millisecondes.  
✅ **Précision élevée (>99%)** sur des tests avec des phrases en français, anglais, espagnol et allemand.  
✅ **Aucune nécessité d'entraînement** : Contrairement à d'autres modèles, il fonctionne immédiatement.  

---

## 🚀 **Axes d'amélioration et perspectives**  

Bien que nos choix de modèles soient adaptés à notre cas d'usage, plusieurs améliorations sont envisageables :  

### 🎯 **1. Optimisation des performances**  
- Utiliser **quantization** sur CamemBERT et DistilBERT pour **réduire leur taille et accélérer l'inférence**.  
- Tester des alternatives comme **TinyBERT** ou **Albert** pour une classification plus rapide.  

### 🤖 **2. Amélioration du dataset**  
- Ajouter plus de phrases ambiguës pour **renforcer la robustesse du modèle de classification d'intention**.  
- Générer des **données augmentées** pour améliorer la reconnaissance des entités (synonymes, fautes de frappe).  

### 🌍 **3. Prise en charge du multilingue**  
- Fine-tuner un modèle **XLM-RoBERTa** au lieu de CamemBERT pour prendre en charge d'autres langues européennes.  
- Ajouter un pipeline automatique avec **FastText → DistilBERT / CamemBERT** pour détecter et traiter plusieurs langues.  

---

## 🎯 **Conclusion**  

Nous avons fait des choix basés sur **la précision, l'efficacité et la rapidité** des modèles pour nos trois tâches principales :  
✅ **CamemBERT** pour la reconnaissance d'entités nommées (NER).  
✅ **DistilBERT** pour la classification d'intention.  
✅ **FastText** pour la détection de langue.  

Ces choix permettent **un équilibre optimal entre précision et rapidité**, tout en garantissant une **robustesse sur des phrases naturelles en français**. 💡