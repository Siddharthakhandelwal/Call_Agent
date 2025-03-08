from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

# Import the function from your original file
from general.main import make_vapi_call
from Doctor.main import doctor_call
from Realstate.main import state

app = FastAPI(title="VAPI Call API", description="API for making automated voice calls")

# Add CORS middleware to allow cr oss-orig in requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Define request model
class CallRequest(BaseModel):
    name: str
    number: str
    mail: Optional[str] = None


# Define response models
class CallResponse(BaseModel):
    id: Optional[str] = None
    status: Optional[str] = None
    customer: Optional[dict] = None
    created_at: Optional[str] = None
    error: Optional[str] = None
@app.get("/")
async def health_check():
    return {"status": "root"}
# Create API endpoints
@app.post("/make-call", response_model=CallResponse)
async def api_make_call(call_request: CallRequest = Body(...)):
    """
    Make an outbound phone call using VAPI.ai
    
    - **name**: Name of the person to call
    - **number**: Phone number to call (with country code)

    """
    try:
        result = make_vapi_call(call_request.name, call_request.number,call_request.mail)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}


@app.post("/doctor", response_model=CallResponse)
async def api_make_call(call_request: CallRequest = Body(...)):
    """
    Make an outbound phone call using VAPI.ai
    
    - **name**: Name of the person to call
    - **number**: Phone number to call (with country code)

    """
    try:
        result = doctor_call(call_request.name, call_request.number,call_request.mail)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/state", response_model=CallResponse)
async def api_make_call(call_request: CallRequest = Body(...)):
    """
    Make an outbound phone call using VAPI.ai
    
    - **name**: Name of the person to call
    - **number**: Phone number to call (with country code)

    """
    try:
        result = state(call_request.name, call_request.number,call_request.mail)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
