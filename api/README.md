# TRAVEL ORDER RESOLVER API
A tool leveraging Natural Language Processing (NLP) to process French text or audio inputs, identify travel-related sentences, extract departure and destination cities, and calculate the optimal SNCF train route.

## 🛠 Tech Stack
- **Python** (Language)
- **FastAPI** (Web Framework)
- **CamemBERT** (NER Model for Travel Details Extraction)
- **DistilBERT** (Text Classification for Travel Intent Detection)
- **SpeechRecognition** (Audio-to-Text Conversion)
- **Tqdm** (Progress Bar)
- **SNCF Route Finder** (Algorithm for train route calculation)

<br />

## ⚙️ Setup Environment Development

### Clone the Repository
First, clone the repository:
```bash
git clone git@github.com:Leoglme/nlp_travel_order_resolver.git
cd nlp_travel_order_resolver
```

### Install Dependencies
Make sure Python 3.12 (or higher) is installed. Then install all the necessary dependencies:
```bash
pip install -r requirements.txt
```

#### Requirements (`requirements.txt`):
```
fastapi
transformers
torch
SpeechRecognition
tqdm
uvicorn
python-multipart
```

### Launch the API Server
Run the server with the following command:
```bash
python run_server.py
```

Or use Uvicorn for live reloading directly:

```bash
uvicorn api.app:app --reload --log-level info
```


### API Endpoints

#### 1. **Convert Audio to Text**
This endpoint takes an audio file as input and returns the text transcription.

- **URL**: `/api/audio-to-text`
- **Method**: `POST`
- **Request**:
    - `file`: An audio file (wav, mp3, etc.)
- **Response**:
    ```json
    {
      "sentence": "je veux aller de Paris à Lyon"
    }
    ```
- **cURL**:
    ```bash
    curl -X POST "http://127.0.0.1:8000/api/audio-to-text" \
         -H "accept: application/json" \
         -H "Content-Type: multipart/form-data" \
         -F "file=@/path/to/your/audio/file.wav"
    ```

#### 2. **Validate Travel Intent**
This endpoint takes a sentence as input and verifies if it is written in French and if it expresses a travel intent.

- **URL**: `/api/validate-travel-intent`
- **Method**: `POST`
- **Request**:
    - `sentence`: A sentence to be analyzed.
- **Response**:
    ```json
    {
      "is_valid": true,
      "reason": "Trip-related sentence detected."
    }
    ```
- **cURL**:
    ```bash
    curl -X POST "http://127.0.0.1:8000/api/validate-travel-intent" \
         -H "accept: application/json" \
         -H "Content-Type: application/json" \
         -d '{"sentence": "je veux voyager de Paris à Lyon"}'
    ```

#### 3. **Find SNCF Route**
This endpoint extracts departure and destination cities from the sentence and returns the optimal SNCF train route between them.

- **URL**: `/api/sncf/find-route`
- **Method**: `POST`
- **Request**:
    - `sentence`: A sentence containing departure and destination cities.
- **Response**:
    ```json
    {
      "departure": "Paris",
      "destination": "Lyon",
      "route": ["Paris Gare de Lyon", "Lyon Part-Dieu"]
    }
    ```
- **cURL**:
    ```bash
    curl -X POST "http://127.0.0.1:8000/api/sncf/find-route" \
         -H "accept: application/json" \
         -H "Content-Type: application/json" \
         -d '{"sentence": "Je pars de Paris pour aller à Lyon"}'
    ```

<br />

## 🔄 Development Cycle

### Run the Project
To start the API, use:
```bash
python run_server.py
```

### Manage Dependencies
If there are issues with dependencies, you can remove and reinstall them:
```bash
pip freeze > requirements.txt
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Debugging
Make sure logging is enabled by default for debugging purposes.