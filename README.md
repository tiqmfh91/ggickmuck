# 🍽️ Food Classification API

AI 기반 음식 분류 및 영양 정보 제공 API입니다. YOLO 객체 탐지와 MobileNet 분류 모델을 활용한 파이프라인으로 구성되어 있습니다.

## 🚀 주요 기능

- **음식 객체 탐지**: YOLOv8 모델을 사용한 실시간 음식 객체 탐지
- **음식 분류**: MobileNet 모델을 통한 정확한 음식 분류 (500+ 종류)
- **영양 정보**: 분류된 음식의 상세 영양 정보 제공
- **GI 지수 정렬**: 혈당 지수 기준으로 음식 정보 정렬
- **이미지 처리**: 원본 이미지 저장 및 크롭된 이미지 관리

## 🏗️ 시스템 아키텍처

```
이미지 업로드 → YOLO 객체 탐지 → 이미지 크롭 → MobileNet 분류 → 영양 정보 매핑 → 결과 반환
```

## 📦 설치 및 실행

### 1. 요구사항 설치

```bash
pip install -r requirements.txt
```

### 2. 모델 파일 준비

다음 모델 파일들을 `model/` 디렉터리에 배치하세요:
- `yolov8m.pt` - YOLO 객체 탐지 모델
- `food_classifier_90_percent.keras` - MobileNet 분류 모델
- `ultra_small_food_classifier.keras` - 경량화 분류 모델

### 3. 정적 파일 디렉터리 생성

```bash
mkdir static/images
mkdir static/crop
mkdir static/temp
```

### 4. 데이터베이스 설정

`database.py`에서 MySQL 연결 정보를 설정하세요.

### 5. 서버 실행

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📋 API 엔드포인트

### 🔍 음식 정보 조회

#### 전체 음식 정보 조회
```http
GET /food/info
```

#### 활성 음식 정보 조회
```http
GET /food/infoByDelYn
```

### 🖼️ 음식 이미지 분류

#### 단일 모델 분류 (MobileNet만 사용)
```http
POST /food/classifyFoodImage
Content-Type: multipart/form-data

image: [이미지 파일]
```

#### 파이프라인 분류 (YOLO + MobileNet)
```http
POST /food/classifyFoodImageByYolo
Content-Type: multipart/form-data

image: [이미지 파일]
```

## 📊 응답 형식

### 성공 응답
```json
{
  "success_code": "200",
  "message": "이미지 업로드 및 분류 완료",
  "classificationResults": [
    {
      "fi_id": 1,
      "fi_name": "고등어구이",
      "fi_category": "생선류",
      "fi_category1": "구이",
      "fi_onetime_offer": "100g",
      "fi_calorie": 190.5,
      "fi_protein": 25.2,
      "fi_fat": 8.1,
      "fi_carbohydrate": 0.0,
      "fi_totalSugar": 0.0,
      "fi_totalDietaryFiber": 0.0,
      "fi_giRate": 0,
      "fi_delYn": "N",
      "fi_image_url": "static/crop/12345_crop_0.jpg"
    }
  ]
}
```

### 오류 응답
```json
{
  "success_code": "500",
  "message": "이미지 업로드 및 분류 실패",
  "classificationResults": null
}
```

## 🤖 지원 음식 종류

### YOLO 탐지 가능 음식 (37종)
- 감자튀김, 고등어구이, 군만두, 김밥, 김치찌개 등...

### MobileNet 분류 가능 음식 (500+ 종)
- 한식, 중식, 일식, 양식 등 다양한 음식 종류 지원

## 🛠️ 기술 스택

- **Framework**: FastAPI
- **AI Models**: 
  - YOLOv8 (Ultralytics)
  - MobileNet (TensorFlow/Keras)
- **Database**: MySQL + SQLAlchemy
- **Image Processing**: OpenCV, PIL
- **Server**: Uvicorn

## 📁 프로젝트 구조

```
c:\ggickmuck\
├── apis/
│   ├── endpoint/
│   │   └── food.py          # 음식 관련 API 엔드포인트
│   └── model/
│       ├── foodModel.py     # 데이터베이스 모델
│       └── labelingModel.py # 라벨링 관련 모델
├── model/                   # AI 모델 파일들
├── static/                  # 정적 파일 저장소
│   ├── images/             # 원본 이미지
│   ├── crop/               # 크롭된 이미지
│   └── temp/               # 임시 파일
├── database.py             # 데이터베이스 연결
├── main.py                 # FastAPI 애플리케이션
└── requirements.txt        # 의존성 패키지
```

## 🔧 설정

### 환경 변수
`.env` 파일을 생성하여 필요한 환경 변수를 설정하세요:
```
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database
```

## 🚦 사용 예시

### Python 클라이언트 예시
```python
import requests

# 이미지 파일 업로드 및 분류
with open('food_image.jpg', 'rb') as f:
    files = {'image': f}
    response = requests.post('http://localhost:8000/food/classifyFoodImageByYolo', files=files)
    result = response.json()
    print(result)
```

### cURL 예시
```bash
curl -X POST "http://localhost:8000/food/classifyFoodImageByYolo" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "image=@food_image.jpg"
```

## 📈 성능 최적화

- **모델 최적화**: 경량화된 MobileNet 모델 사용
- **이미지 전처리**: 효율적인 리사이징 및 정규화
- **데이터베이스**: 인덱싱을 통한 빠른 조회
- **GI 지수 정렬**: 건강한 음식 우선 표시

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 📞 문의

프로젝트와 관련된 문의사항이 있으시면 Issues 탭을 이용해 주세요.
