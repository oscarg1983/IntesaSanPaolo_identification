from fastapi import FastAPI, HTTPException, Query
import re

app = FastAPI()

# Regex per validare il formato E.164 (es. +393471234567)
E164_REGEX = re.compile(r"^\+[1-9]\d{1,14}$")

@app.get("/lookup")
def lookup(phone_number: str = Query(..., description="Numero in formato E.164")):
    clean_number = phone_number.strip()

    if not E164_REGEX.match(clean_number):
        raise HTTPException(status_code=400, detail="Formato non valido. Usa E.164 (es. +39...)")

    # Esempio di logica per restituire parametri diversi
    is_italy = clean_number.startswith("+39")
    
    return {
        "status": "success",
        "phone": clean_number,
        "customer_id": f"ID-{clean_number[-7:]}",
        "segment": "Premium" if is_italy else "Standard",
        "language": "it-IT" if is_italy else "en-US",
        "authorized": True
    }

@app.get("/")
def home():
    return {"message": "API is running"}
