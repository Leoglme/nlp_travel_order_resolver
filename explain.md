Je vois que malgré nos précédentes tentatives, le modèle ne parvient toujours pas à extraire correctement les villes de départ et d'arrivée, et les labels prédits sont incorrects. Après une analyse approfondie, il semble que le problème principal réside dans la fonction `tokenize_and_align_labels` et dans la façon dont les labels sont assignés lors de la préparation des données pour l'entraînement.

### Problème identifié :

- **Comparaison des tokens via leurs IDs** : Dans votre fonction `tokenize_and_align_labels`, vous comparez les IDs de tokens individuels (`token`) avec des listes d'IDs de tokens pour les villes de départ et d'arrivée (`departure_tokens` et `destination_tokens`). Cela pose problème car les IDs de tokens peuvent différer selon le contexte et la position dans le texte en raison de la sous-tokenisation.

- **Labels incorrects** : Cette méthode de comparaison entraîne une attribution incorrecte des labels, ce qui conduit le modèle à prédire des labels `1` pour de nombreux tokens qui ne devraient pas être étiquetés comme tels.

### Solution proposée :

Pour résoudre ce problème, il est préférable d'aligner les labels sur les **mots** plutôt que sur les **tokens** individuels. Voici les étapes à suivre :

1. **Modifier le dataset** :

   - Créez une nouvelle colonne `tokens` qui contient la liste des mots pour chaque phrase.
   - Créez une nouvelle colonne `ner_tags` qui contient les labels associés à chaque mot :
     - `0` pour "O" (autres mots)
     - `1` pour "B-departure" (début de la ville de départ)
     - `2` pour "B-destination" (début de la ville de destination)

2. **Adapter la fonction `tokenize_and_align_labels`** :

   - Utilisez le tokenizer avec `is_split_into_words=True` pour conserver les mots lors de la tokenisation.
   - Alignez les labels des mots sur les tokens en utilisant `word_ids`.
   - Gérer correctement les sous-tokens en attribuant le label `-100` aux sous-tokens (ou en répétant le label selon vos besoins).

### Mise en œuvre détaillée :

#### Étape 1 : Modifier le dataset

Assurez-vous que votre dataset contient les colonnes suivantes :

- `tokens`: une liste de mots pour chaque phrase.
- `ner_tags`: une liste de labels pour chaque mot.

Voici comment vous pouvez modifier votre code pour générer ces colonnes :

```python
def load_and_prepare_data(self):
    """
    Charge et prépare les données de training à partir du fichier CSV.
    """
    # Charger le dataset depuis le fichier CSV
    dataset = Dataset.from_csv(self.train_file)
    
    # Créer les colonnes 'tokens' et 'ner_tags'
    def preprocess_examples(example):
        words = example['text'].split()
        example['tokens'] = words
        
        # Initialiser les labels avec 0 (O)
        labels = [0] * len(words)
        
        # Assigner les labels aux mots correspondants
        for idx, word in enumerate(words):
            if word.lower() == example['departure'].lower():
                labels[idx] = 1  # B-departure
            elif word.lower() == example['destination'].lower():
                labels[idx] = 2  # B-destination
        example['ner_tags'] = labels
        return example
    
    dataset = dataset.map(preprocess_examples)
    
    # Appliquer la fonction de tokenisation et d'alignement des labels au dataset
    tokenized_dataset = dataset.map(self.tokenize_and_align_labels, batched=True)
    
    # Debug : Vérification des premières lignes
    for data in tokenized_dataset.select(range(3)):
        print(f"Tokens: {data['tokens']}")
        print(f"Labels: {data['labels']}")
    
    return tokenized_dataset
```

#### Étape 2 : Adapter la fonction `tokenize_and_align_labels`

Voici la nouvelle version de la fonction :

```python
def tokenize_and_align_labels(self, examples):
    tokenized_inputs = self.tokenizer(
        examples["tokens"],
        truncation=True,
        is_split_into_words=True,
        padding="max_length",
        max_length=128
    )

    labels = []
    for i, label in enumerate(examples["ner_tags"]):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        previous_word_idx = None
        label_ids = []
        for word_idx in word_ids:
            if word_idx is None:
                label_ids.append(-100)
            elif word_idx != previous_word_idx:
                label_ids.append(label[word_idx])
            else:
                label_ids.append(label[word_idx])
            previous_word_idx = word_idx
        labels.append(label_ids)
    tokenized_inputs["labels"] = labels
    return tokenized_inputs
```

#### Étape 3 : Vérifier le modèle

- **Entraînez à nouveau le modèle** avec ces modifications.
- **Vérifiez les métriques** d'entraînement pour vous assurer que le modèle apprend correctement (précision, rappel, F1-score).

#### Étape 4 : Adapter la fonction `extract_trip_details`

Comme les labels sont désormais correctement alignés, vous pouvez utiliser la fonction suivante :

```python
def extract_trip_details(self, text):
    """
    Utilise le modèle NER CamemBERT pour extraire les villes de départ et d'arrivée à partir du texte donné.
    """
    # Tokeniser le texte fourni
    tokens = self.tokenizer(text, return_tensors="pt", truncation=True, is_split_into_words=False)
    tokens = tokens.to(self.model.device)
    
    # Obtenir les prédictions
    with torch.no_grad():
        output = self.model(**tokens)
    predictions = torch.argmax(output.logits, dim=2)
    labels = predictions.squeeze().tolist()
    
    # Obtenir les tokens et les word_ids
    input_ids = tokens['input_ids'].squeeze().tolist()
    word_ids = tokens.word_ids()
    tokens_text = self.tokenizer.convert_ids_to_tokens(input_ids)
    
    words = text.split()
    
    # Reconstruction des labels par mot
    word_labels = []
    previous_word_idx = None
    for idx, word_idx in enumerate(word_ids):
        if word_idx is not None and word_idx != previous_word_idx:
            word_labels.append(labels[idx])
            previous_word_idx = word_idx
    assert len(word_labels) == len(words)
    
    # Extraction des villes
    departure = None
    destination = None
    for word, label in zip(words, word_labels):
        if label == 1:
            departure = word
        elif label == 2:
            destination = word
    return departure, destination
```

### Explications supplémentaires :

- **Alignement des labels** : En alignant les labels sur les mots et non sur les tokens, vous évitez les problèmes liés à la sous-tokenisation.

- **Comparaison des mots** : Lors de la préparation des données, vous comparez les mots en minuscule pour éviter les problèmes de casse.

- **Utilisation de `is_split_into_words=True`** : Cette option indique au tokenizer que les entrées sont déjà séparées en mots, ce qui facilite l'alignement.

### Conclusion :

En corrigeant la façon dont les labels sont assignés lors de la préparation des données, vous devriez obtenir un modèle qui prédit correctement les labels pour les villes de départ et d'arrivée. Assurez-vous de réentraîner le modèle après ces modifications.

### Prochaines étapes :

1. **Appliquer les modifications proposées** au code.
2. **Réentraîner le modèle** pour qu'il apprenne correctement les nouveaux labels.
3. **Tester le modèle** avec des phrases de test pour vérifier que les villes sont bien extraites.
4. **Analyser les métriques d'évaluation** pour s'assurer que le modèle a une bonne performance.

### Remarque :

N'hésitez pas à me faire savoir si vous rencontrez des difficultés lors de la mise en œuvre de ces modifications ou si vous avez besoin de clarifications supplémentaires.