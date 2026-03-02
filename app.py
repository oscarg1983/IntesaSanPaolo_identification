from fastapi import FastAPI, Query, HTTPException, Header, Request
from typing import Optional
import re
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# Regex per validare il formato E.164 (esistente)
E164_REGEX = re.compile(r"^\+[1-9]\d{1,14}$")

# Pydantic Model per CustomerAuthLevelResponse (come prima)
class CustomerAuthLevelResponse(BaseModel):
    authLevels: str  # Enum: STRONG, PENDING, SOFT, CLOSED, EXPIRED, REJECTED, FAILED
    timestamp: int   # Unix timestamp int64

# Wrapper per match esatto struttura richiesta
class ValidateCallWrapper(BaseModel):
    CustomerAuthLevelResponse: CustomerAuthLevelResponse

# Endpoint esistente (invariato)
@app.get("/api/v1/contacts/lookup")
def lookup_contact(
    request: Request,
    phoneNumber: str = Query(..., description="E.164"),
    type: str = Query(..., description="Retail/Legal"),
    requestId: str = Query(..., description="ID")
):
    print("--- DEBUG HEADERS ---")
    for header_name, header_value in request.headers.items():
        print(f"{header_name}: {header_value}")
    
    x_api_key = request.headers.get("x-api-key") 
    print(f"Header ricevuto: {x_api_key}") 
    
    if x_api_key != "secret-key":
        print(f"ERRORE: x-api-key ricevuto è {x_api_key}")
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")

    phone = phoneNumber.strip()
    
    if not E164_REGEX.match(phone):
        raise HTTPException(status_code=400, detail="INVALID_PHONE_FORMAT")

    if phone.endswith("500"):
        raise HTTPException(status_code=500, detail="INTERNAL_ERROR")
    if phone.endswith("503"):
        raise HTTPException(status_code=503, detail="SERVICE_UNAVAILABLE")

    if phone.endswith("000"):
        return {
            "totalSize": 0,
            "requestId": requestId,
            "done": True,
            "contactFound": False,
            "records": []
        }
    if phone == "+393666742139":
        return {
            "totalSize": 2,
            "requestId": requestId,
            "done": True,
            "contactFound": True,
            "records": [
                {
                    "id": "123456789",
                    "type": "retail",
                    "firstName": "Mario",
                    "lastName": "Rossi",
                    "email": "mario.rossi@example.com",
                    "JMBG": "123456789",
                    "IntesaMobi_status": "Active",
                    "ConsentID_status": "Enabled",
                    "AML_status": "Clear",
                    "Rating_status": "Low",
                    "ClientClassification": "Individual",
                    "NativeBranch": "Milan_01",
                    "NativeRM": "Manager_Alpha",
                    "LegalName": "",
                    "CorpId": "",
                    "CIF": "",
                    "MB": "",
                    "segment": "magnifica",
                    "RM": "",
                    "TIN": "",
                    "AuthMethod": "SMS_OTP"
                },
                {
                    "id": "234567890",
                    "type": "retail",
                    "firstName": "Giovanni",
                    "lastName": "Verdi",
                    "email": "giovanni.verdi@example.com",
                    "JMBG": "234567890",
                    "IntesaMobi_status": "Active",
                    "ConsentID_status": "Enabled",
                    "AML_status": "Clear",
                    "Rating_status": "Low",
                    "ClientClassification": "Individual",
                    "NativeBranch": "Milan_02",
                    "NativeRM": "Manager_Beta",
                    "LegalName": "",
                    "CorpId": "",
                    "CIF": "",
                    "MB": "",
                    "segment": "magnifica",
                    "RM": "",
                    "TIN": "",
                    "AuthMethod": "WithKey"
                }
            ]
        }
        
    return {
        "totalSize": 1,
        "requestId": requestId,
        "done": True,
        "contactFound": True,
        "records": [
            {
                "id": "123456789",
                "type": "retail",
                "firstName": "Mario",
                "lastName": "Rossi",
                "email": "mario.rossi@example.com",
                "JMBG": "123456789",
                "IntesaMobi_status": "Active",
                "ConsentID_status": "Enabled",
                "AML_status": "Clear",
                "Rating_status": "Low",
                "ClientClassification": "Individual",
                "NativeBranch": "Milan_01",
                "NativeRM": "Manager_Alpha",
                "LegalName": "",
                "CorpId": "",
                "CIF": "",
                "MB": "",
                "segment": "magnifica",
                "RM": "",
                "TIN": "",
                "AuthMethod": "SMS_OTP"
            }
        ]
    }

# NUOVO ENDPOINT con CLASS + WRAPPER (formato originale preferito)
@app.post("/api/v1/validateCall", response_model=ValidateCallWrapper)
def validate_call(
    request: Request,
    userId: str = Query(..., description="User ID", example="12345"),
    token: str = Query(..., description="Auth token", example="abc123xyz"),
    timestamp: Optional[str] = Header(None, description="Unix timestamp", example="1768905669"),
    channel: Optional[str] = Header(None, description="Channel", example="APPLICATION_DIGICAL_MOBILE"),
    sessionId: Optional[str] = Header(None, description="Session ID", example="f2afed31-0cd1-11f1-ae25-df4dd6a2ece2"),
    locale: Optional[str] = Header(None, description="Locale", example="en")
):
    # DEBUG headers
    print("--- DEBUG HEADERS validateCall ---")
    for header_name, header_value in request.headers.items():
        print(f"{header_name}: {header_value}")
    
    print(f"userId: {userId}, token: {token}")
    print(f"Headers - timestamp: {timestamp}, channel: {channel}, sessionId: {sessionId}, locale: {locale}")
    
    # Autenticazione
    x_api_key = request.headers.get("x-api-key")
    if x_api_key != "secret-key":
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")
    
    if not userId or not token:
        raise HTTPException(status_code=400, detail="Missing userId or token")
    
    # LOGICA BUSINESS per authLevels
    if "expired" in token.lower():
        auth_level = "EXPIRED"
    elif "reject" in token.lower():
        auth_level = "REJECTED"
    elif "pending" in token.lower():
        auth_level = "PENDING"
    elif userId == "12345" and token == "abc123xyz":
        auth_level = "STRONG"
    else:
        auth_level = "SOFT"
    
    # Timestamp corrente (int64 ms)
    current_timestamp = int(datetime.now().timestamp() * 1000)
    
    # Response con CLASS + WRAPPER (validazione automatica)
    inner_response = CustomerAuthLevelResponse(
        authLevels=auth_level,
        timestamp=current_timestamp
    )
    
    return ValidateCallWrapper(CustomerAuthLevelResponse=inner_response)

@app.get("/")
def health():
    return {"status": "up"}
