import os
import json
import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import timm
from pathlib import Path
from PIL import Image
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
import albumentations as A
from albumentations.pytorch import ToTensorV2
from app.schemas import APIResponse 

# 1. 환경 설정 ----------------------------------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# 2. 경로 관리 함수 -----------------------------------------------
def get_project_root() -> Path:
    """프로젝트 루트 경로 계산"""
    current_file = Path(__file__).resolve()
    return current_file.parent.parent.parent  # src/app/api/predict.py → 프로젝트 루트

def get_model_path(model_name: str) -> str:
    """모델 파일 절대 경로 생성"""
    model_dir = get_project_root() / "app" / "models"
    model_path = model_dir / model_name
    
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    return str(model_path)

# 3. 라벨 매핑 ----------------------------------------------------
binary_label_map = {0: "무증상", 1: "유증상"}
disease_label_map = {
    0: "구진_플라크",
    1: "비듬_각질_상피성잔고리",
    2: "태선화_과다색소침착",
    3: "농포_여드름",
    4: "미란_궤양",
    5: "결절_종괴"
}

# 4. 모델 아키텍처 ------------------------------------------------
class DualInputConvNeXt(nn.Module):
    def __init__(self, model_name='convnext_base', num_classes=6):
        super().__init__()
        self.backbone = timm.create_model(model_name, pretrained=False, num_classes=0)
        features = self.backbone.num_features
        
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Dropout(0.4),
            nn.Linear(features*2, features),
            nn.GELU(),
            nn.BatchNorm1d(features),
            nn.Dropout(0.3),
            nn.Linear(features, features//2),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(features//2, num_classes)
        )

    def forward(self, x_full, x_roi):
        f_full = self.backbone.forward_features(x_full)
        f_roi = self.backbone.forward_features(x_roi)
        
        if f_full.dim() == 4:
            f_full = F.adaptive_avg_pool2d(f_full, 1)
        if f_roi.dim() == 4:
            f_roi = F.adaptive_avg_pool2d(f_roi, 1)
            
        combined = torch.cat([f_full, f_roi], dim=1)
        return self.classifier(combined)

# 5. ROI 추출기 ---------------------------------------------------
class ROIExtractor:
    def __init__(self, min_roi_size=64):
        self.min_roi_size = min_roi_size

    def _auto_detect(self, image: np.ndarray) -> tuple:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (5,5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        max_area = 0
        best_rect = (0,0,image.shape[1],image.shape[0])
        
        for cnt in contours:
            x,y,w,h = cv2.boundingRect(cnt)
            area = w * h
            if area > max_area and w > self.min_roi_size and h > self.min_roi_size:
                max_area = area
                best_rect = (x,y,x+w,y+h)
                
        return best_rect

    def extract(self, image: Image.Image) -> Image.Image:
        np_image = np.array(image)
        x1,y1,x2,y2 = self._auto_detect(np_image)
        return image.crop((x1,y1,x2,y2))

# 6. 전처리 파이프라인 --------------------------------------------
def create_transform(size=320):
    return A.Compose([
        A.Resize(height=size, width=size),
        A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ToTensorV2()
    ])

# 7. 모델 로더 ----------------------------------------------------
class SkinModel:
    def __init__(self, model_path, num_classes):
        self.model = DualInputConvNeXt(num_classes=num_classes).to(device)
        self.transform = create_transform()
        self.roi_extractor = ROIExtractor()
        
        state = torch.load(model_path, map_location=device)
        state_dict = state.get("model_state_dict", state)
        state_dict = {k.replace("module.", ""): v for k, v in state_dict.items()}
        self.model.load_state_dict(state_dict, strict=False)
        self.model.eval()

    def predict(self, image_file):
        try:
            image = Image.open(image_file).convert("RGB")
            roi_image = self.roi_extractor.extract(image)
            
            input_full = self.transform(image=np.array(image))['image'].unsqueeze(0).to(device)
            input_roi = self.transform(image=np.array(roi_image))['image'].unsqueeze(0).to(device)
            
            with torch.no_grad():
                outputs = self.model(input_full, input_roi)
                probabilities = F.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
            
            return predicted.item(), confidence.item()
        except Exception as e:
            raise RuntimeError(f"Prediction failed: {str(e)}")

# 8. API 초기화 ---------------------------------------------------
router = APIRouter()

try:
    binary_model = SkinModel(get_model_path("binary_best.pth"), num_classes=2)
    disease_model = SkinModel(get_model_path("disease_best.pth"), num_classes=6)
except Exception as e:
    raise RuntimeError(f"Model loading failed: {str(e)}")

# 9. 계층적 예측 --------------------------------------------------
def hierarchical_predict(image_file):
    try:
        binary_pred, binary_conf = binary_model.predict(image_file)
        if binary_pred == 0:
            return {"label": binary_label_map[binary_pred], "probability": binary_conf}
        else:
            disease_pred, disease_conf = disease_model.predict(image_file)
            return {"label": disease_label_map[disease_pred], "probability": disease_conf}
    except Exception as e:
        raise RuntimeError(f"Hierarchical prediction failed: {str(e)}")

# 10. API 엔드포인트 -----------------------------------------------
@router.post("/predict", response_model=APIResponse)
async def predict(file: UploadFile = File(...)):
    try:
        # 이미지 유효성 검사
        if not file.content_type.startswith('image/'):
            return APIResponse(
                success=False,
                message="이미지 파일만 업로드 가능합니다",
                data=None
            )

        # 예측 로직 (가정)
        result = hierarchical_predict(file.file)
        
        return APIResponse(
            success=True,
            message="AI 진단이 완료되었습니다",
            data={
                "filename": file.filename,
                "diagnosis": result["label"],
                "confidence": round(result["probability"], 4),
                "details": "추가 설명 필드"  # 실제 구현시 상세 설명 추가
            }
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"진단 처리 중 오류 발생: {str(e)}",
            data=None
        )