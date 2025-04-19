import torch
from PIL import Image
from torchvision import transforms
import timm
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

label_map = {
    0: "무증상",
    1: "비듬_각질",
    2: "농포_여드름",
    3: "결절_종괴",
    4: "감염성피부염",
    5: "비감염성피부염"
}

class SkinDiseaseModel:
    def __init__(self, model_path: str):
        self.model = timm.create_model("inception_v4", num_classes=6, pretrained=False)
        state_dict = torch.load(model_path, map_location="cpu")
        self.model.load_state_dict(state_dict)
        self.model.eval()
        self.transform = transforms.Compose([
            transforms.Resize(299),
            transforms.CenterCrop(299),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def predict(self, image_file):
        image = Image.open(image_file).convert("RGB")
        input_tensor = self.transform(image).unsqueeze(0)
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
        return label_map[predicted.item()], confidence.item()

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