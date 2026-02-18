from fastapi import FastAPI, Query, HTTPException, Header
from typing import Optional
import re

app = FastAPI()

# Regex per validare il formato E.164
E164_REGEX = re.compile(r"^\+[1-9]\d{1,14}$")

@app.get("/api/v1/contacts/lookup")
def lookup_contact(
    phoneNumber: str = Query(..., description="Numero in formato E.164"),
    requestId: str = Query(..., description="ID conversazione e timestamp"),
    x_api_key: Optional[str] = Header(None) 
):
    # 1. Errore 401: UNAUTHORIZED
    if x_api_key != "secret-key":
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")

    phone = phoneNumber.strip()
    
    # Validazione formato (is_valid)
    if not E164_REGEX.match(phone):
        # 2. Errore 400: INVALID_PHONE_FORMAT
        raise HTTPException(status_code=400, detail="INVALID_PHONE_FORMAT")

    # 3. Simulazione Errori 500/503 per test
    if phone.endswith("500"):
        raise HTTPException(status_code=500, detail="INTERNAL_ERROR")
    if phone.endswith("503"):
        raise HTTPException(status_code=503, detail="SERVICE_UNAVAILABLE")

    # --- SIMULAZIONE NOT FOUND ---
    # Se il numero termina con "000", simuliamo che il contatto non esista nel CRM
    if phone.endswith("000"):
        return {
            "totalSize": 0,
            "requestId": requestId,
            "done": True,
            "contactFound": False,
            "records": []
        }

    # --- CASO SUCCESSO (Contact Found) ---
    return {
        "totalSize": 1,
        "requestId": requestId,
        "done": True,
        "contactFound": True,
        "records": [
            {
                "id": "CRM-778899",
                "type": "retail" if phone.startswith("+39") else "legal",
                "firstName": "Mario",
                "lastName": "Rossi",
                "email": "mario.rossi@example.com",
                "JMBG": "1234567890123",
                "IntesaMobi_status": "Active",
                "ConsentID_status": "Enabled",
                "AML_status": "Clear",
                "Rating_status": "Low",
                "ClientClassification": "Individual",
                "NativeBranch": "Milan_01",
                "NativeRM": "Manager_Alpha",
                "LegalName": "",
                "MB": "",
                "segment": "magnifica" if phone.endswith("0") else "premium",
                "RM": "Direct Channel",
                "TIN": "IT12345678901",
                "AuthMethod": "SMS_OTP"
            }
        ]
    }

@app.get("/")
def health():
    return {"status": "up"}
