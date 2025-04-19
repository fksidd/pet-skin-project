from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.model.inference import SkinDiseaseModel

router = APIRouter()
model = SkinDiseaseModel("app/best_model.pth")

@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        label, confidence = model.predict(file.file)
        return JSONResponse({
            "filename": file.filename,
            "label": label,
            "probability": confidence
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))