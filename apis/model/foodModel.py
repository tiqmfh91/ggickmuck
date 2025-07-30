from sqlalchemy import Column, TEXT, INT, BIGINT, DOUBLE, CHAR
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import List, Optional

Base = declarative_base()

class Food(Base):  
    __tablename__ = 'foodInfo'
    fi_id = Column(BIGINT, primary_key=True, autoincrement=True)
    fi_name = Column(TEXT, nullable=True)
    fi_category = Column(TEXT, nullable=True)
    fi_category1 = Column(TEXT, nullable=True)
    fi_onetime_offer = Column(BIGINT, nullable=True)
    fi_calorie = Column(DOUBLE, nullable=True)
    fi_protein = Column(DOUBLE, nullable=True)
    fi_fat = Column(DOUBLE, nullable=True)
    fi_carbohydrate = Column(DOUBLE, nullable=True)
    fi_totalSugar = Column(DOUBLE, nullable=True)
    fi_totalDietaryFiber = Column(DOUBLE, nullable=True)
    fi_giRate = Column(BIGINT, nullable=True)
    fi_delYn = Column(CHAR(1), nullable=True, default='N')

class FoodImage(Base):  
    __tablename__ = 'foodImage'
    fim_id = Column(BIGINT, primary_key=True, autoincrement=True)
    fim_image_path = Column(TEXT)
    fim_image_susses_yn = Column(CHAR(1))
    fim_image_classified_accuracy = Column(DOUBLE, nullable=True)
    fim_insert_dt = Column(TEXT, nullable=True)

# Response용 Pydantic 모델들
class FoodInfoResponse(BaseModel):
    """음식 정보 응답용 모델"""
    fi_id: int
    fi_name: Optional[str] = None
    fi_category: Optional[str] = None
    fi_category1: Optional[str] = None
    fi_onetime_offer: Optional[int] = None
    fi_calorie: Optional[float] = None
    fi_protein: Optional[float] = None
    fi_fat: Optional[float] = None
    fi_carbohydrate: Optional[float] = None
    fi_totalSugar: Optional[float] = None
    fi_totalDietaryFiber: Optional[float] = None
    fi_giRate: Optional[int] = None
    fi_delYn: Optional[str] = None
    fi_image_url: Optional[str] = None

    class Config:
        from_attributes = True

class ApiResponse(BaseModel):
    """공통 API 응답 모델"""
    success_code: str  # 성공 코드 (예: "200", "SUCCESS", etc.)
    message: str       # 응답 메시지
    classificationResults: Optional[List[FoodInfoResponse]] = None  # 음식 정보 리스트
    
    class Config:
        from_attributes = True

class SingleFoodApiResponse(BaseModel):
    """단일 음식 정보 API 응답 모델"""
    success_code: str
    message: str
    data: Optional[FoodInfoResponse] = None
    
    class Config:
        from_attributes = True

class foodDetectedImage(Base):
    __tablename__ = 'foodDetectedImage'
    fdi_id = Column(BIGINT, primary_key=True, autoincrement=True)
    fdi_image_path = Column(TEXT, nullable=False)
    fdi_image_susses_yn = Column(CHAR(1), nullable=True)
    fdi_image_classified_accuracy = Column(DOUBLE, nullable=True)
    fdi_image_class_idx = Column(INT, nullable=True)
    fim_id = Column(BIGINT, nullable=False)
    fdi_insert_dt = Column(TEXT, nullable=True)
    