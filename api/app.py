import sys
import os
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.camembert_ner_model import CamemBERTNERModel
from models.travel_intent_classifier_model import TravelIntentClassifierModel
from services.sncf.sncf_route_finder import SNCFRouteFinder
from services.voice_to_text_converter import VoiceToTextConverter
from services.language_detection import LanguageIdentification

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentenceRequest(BaseModel):
    sentence: str


class AudioRequest(BaseModel):
    file: UploadFile


class ValidationResponse(BaseModel):
    is_valid: bool
    reason: str


class RouteResponse(BaseModel):
    departure: str
    destination: str
    route: list[str]


# 2. Route to convert audio file to text
@app.post("/api/audio-to-text", response_model=SentenceRequest)
async def audio_to_text_route(file: UploadFile = File(...)):
    logger.info(f"Processing file: {file.filename}")
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an audio file.")

    if file.size > 10 * 1024 * 1024:  # 10 MB
        raise HTTPException(status_code=400, detail="File size exceeds 10MB.")

    try:
        voice_to_text_converter = VoiceToTextConverter()
        text_from_audio = voice_to_text_converter.convert_from_audio_file(file.file)
        logger.info(f"Converted audio to text: {text_from_audio}")
        return {"sentence": text_from_audio}
    except Exception as e:
        logger.error(f"Error processing audio file: {e}")
        raise HTTPException(status_code=500, detail="Audio processing failed: {}".format(str(e)))


# 3. Route to validate the text (check French and travel intention)
@app.post("/api/validate-travel-intent", response_model=ValidationResponse)
async def validate_travel_intent(request: SentenceRequest):
    logger.info(f"Validating sentence: {request.sentence}")
    lang_identifier = LanguageIdentification()
    lang, confidence = lang_identifier.stat_print(request.sentence)
    if lang[0] != "__label__fr":
        logger.info(f"Non-French text detected, language is {lang[0]} with confidence {confidence} %")
        raise HTTPException(status_code=422, detail=f"Non-French text detected, language is {lang[0]} with confidence {confidence[0]} %")

    # Model for verify valid sentence (subject is Ok)
    trip_intent_classifier_model = TravelIntentClassifierModel()

    # Verify if the sentence is a trip-related sentence
    prediction = trip_intent_classifier_model.predict(request.sentence)
    if prediction == 1:
        logger.info(f"Trip-related sentence detected: {request.sentence}")
        return ValidationResponse(is_valid=True, reason="Trip-related sentence detected.")
    else:
        logger.info(f"Non-trip-related sentence detected: {request.sentence}")
        raise HTTPException(status_code=422, detail="Non-trip-related sentence detected.")


# 4. Route to extract cities and find the SNCF route
@app.post("/api/sncf/find-route", response_model=RouteResponse)
async def find_route_sncf(request: SentenceRequest):
    # Initialize the CamemBERTNERModel
    logger.info(f"Extracting trip details from: {request.sentence}")
    camembert_ner_model = CamemBERTNERModel()
    camembert_ner_model.load_model()
    departure, destination = camembert_ner_model.extract_trip_details(request.sentence)

    if not departure or not destination:
        logger.error("Failed to extract departure or destination.")
        raise HTTPException(status_code=400,
                            detail="Unable to extract both departure and destination from the sentence.")

    sncf_route_finder = SNCFRouteFinder()
    route = sncf_route_finder.find_shortest_route(departure, destination)
    if route:
        logger.info(f"Route found from {departure} to {destination}: {route}")
        return RouteResponse(departure=departure, destination=destination, route=route)
    else:
        logger.error(f"No route found from {departure} to {destination}")
        raise HTTPException(status_code=404, detail=f"No route found from {departure} to {destination}.")
