import sys
import os
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.services.audio_service import AudioService
from models.camembert_ner_model import CamemBERTNERModel
from models.travel_intent_classifier_model import TravelIntentClassifierModel
from services.sncf.sncf_route_finder import SNCFRouteFinder
from services.voice_to_text_converter import VoiceToTextConverter
from services.language_detection import LanguageIdentification

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentenceRequest(BaseModel):
    sentence: str


class AudioRequest(BaseModel):
    file: UploadFile


class ValidationResponse(BaseModel):
    is_valid: bool
    is_trip_related: bool
    is_correct_language: bool
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
        # Convert to WAV using AudioService
        wav_file = AudioService.convert_to_wav(file.file)

        voice_to_text_converter = VoiceToTextConverter()
        text_from_audio = voice_to_text_converter.convert_from_audio_file(wav_file)
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

    is_correct_language = lang[0] == "__label__fr"

    trip_intent_classifier_model = TravelIntentClassifierModel()
    is_trip_related = trip_intent_classifier_model.predict(request.sentence) == 1

    if not is_correct_language:
        logger.info(f"Non-French text detected, language is {lang[0]} with confidence {confidence} %")
        return ValidationResponse(is_valid=False, reason="Non-French text detected.", is_correct_language=False,
                                  is_trip_related=is_trip_related)

    if not is_trip_related:
        logger.info(f"Non-trip-related sentence detected: {request.sentence}")
        return ValidationResponse(is_valid=False, reason="Non-trip-related sentence detected.", is_correct_language=True,
                                  is_trip_related=False)

    logger.info(f"Trip-related sentence detected: {request.sentence}")
    return ValidationResponse(is_valid=True, reason="Trip-related sentence detected.", is_correct_language=True,
                              is_trip_related=True)


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
