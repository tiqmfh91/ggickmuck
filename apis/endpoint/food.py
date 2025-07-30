from PIL import Image
from fastapi import APIRouter, File, UploadFile 
from fastapi.responses import HTMLResponse, JSONResponse
import numpy as np
from pydantic import BaseModel
from apis.model.labelingModel import get_mobilenet_classes
from database import engineconn
from apis.model import foodModel
import uuid
from datetime import datetime
from tensorflow.keras.models import load_model
import io
from ultralytics import YOLO
import cv2


router = APIRouter()

engine = engineconn()
session = engine.sessionmaker()



@router.get("/info", response_model=foodModel.ApiResponse)
def selectAllFoodInfo():
    try:
        food_info = session.query(foodModel.Food).all()
        print("info 호출됨")
        # SQLAlchemy 객체를 Pydantic 모델로 변환
        food_responses = [foodModel.FoodInfoResponse.from_orm(food) for food in food_info]
        
        session.close()
        
        return foodModel.ApiResponse(
            success_code="200",
            message="음식 정보 조회 성공",
            data=food_responses
        )
    except Exception as e:
        session.close()
        return foodModel.ApiResponse(
            success_code="500",
            message=f"음식 정보 조회 실패: {str(e)}",
            data=None
        )


@router.get("/infoByDelYn", response_model=foodModel.ApiResponse)
def selectActiveFoodInfo():
    try:
        food_info = session.query(foodModel.Food).filter(foodModel.Food.fi_delYn == 'N').all()
        
        # SQLAlchemy 객체를 Pydantic 모델로 변환
        food_responses = [foodModel.FoodInfoResponse.from_orm(food) for food in food_info]
        
        session.close()
        
        return foodModel.ApiResponse(
            success_code="200",
            message="활성 음식 정보 조회 성공",
            data=food_responses
        )
    except Exception as e:
        session.close()
        return foodModel.ApiResponse(
            success_code="500",
            message=f"활성 음식 정보 조회 실패: {str(e)}",
            data=None
        )


#이미지를 받아와서 모델에 보내는 부분!
@router.post("/classifyFoodImage", response_model=foodModel.ApiResponse)
async def classifyFoodImage(image: UploadFile):
    

    filename = str(uuid.uuid1()).replace("-", "")
    SAVE_PATH = "static/images/" + filename + ".jpg"
    
    # 이미지 파일 읽기
    image_bytes = await image.read()

    # with open(SAVE_PATH, "wb") as buffer:
    #     buffer.write(image_bytes)

    TARGET_CLASSES = get_mobilenet_classes("MOBILENET_1")
    

    # 어떻게 모델을 사용할 것인지 결정이되야한다
    # 만약에 욜로 모델을 사용 다중객체를 하게된다면 일단저장 후 크롭이미지 생성후 저장하는 프로세스 작업해야함
    # 그게 아니라면 아래 소스그대로 쓰면될것이다
    classification_success = "N"  # 실제 분류 결과에 따라 Y/N
    accuracy = 0.95  # 실제 모델에서 나온 정확도 값
    predicted_index = 0  # 실제 모델에서 예측한 인덱스 값
    confidence = 0

    # YOLO모델을 사용하여 추론을 해오고 추론해온 것 기준으로 이미지 크롭한 리스트를 만든다
    model = load_model("model/ultra_small_food_classifier_v2.keras")
    try:
        image_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        #이미지 들어온거확인
        # 이미지를 파일로 저장
        temp_filename = str(uuid.uuid1()).replace("-", "")
        temp_save_path = f"static/images/{temp_filename}_original.jpg"
        image_pil.save(temp_save_path)
        print(f"원본 이미지 저장됨: {temp_save_path}")
        
        image_pil = image_pil.resize((224, 224))
        img_array = np.array(image_pil) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        predictions = model.predict(img_array)
        predicted_index = int(np.argmax(predictions[0]))
        confidence = float(np.max(predictions[0]))

        print(f"Classified {TARGET_CLASSES[predicted_index]} with confidence {confidence:.2f} label_index {predicted_index}")

        classification_success = "Y" if confidence > 0.7 else "N"

       
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
    # foodImage 테이블에 데이터 insert 상위의 원본 이미지를 저장을 먼처한다
    # 그후에 YOLO로 탐지한 객체들을 크롭화된 이미지들을 foodDetectedImage 해당 테이블에 
    # 상위 테이블 인덱스를 가져와 배열 저장한다.
    try:
        # 현재 날짜시간을 16자리 형태로 생성 (YYYYMMDDHHMMSSFF)
        current_dt = datetime.now().strftime("%Y%m%d%H%M%S%f")[:16]
        
        # FoodImage 객체 생성
        food_image = foodModel.FoodImage(
            fim_image_path=SAVE_PATH,
            fim_image_susses_yn=classification_success,
            fim_image_classified_accuracy=accuracy,
            fim_insert_dt=current_dt
        )

        # 데이터베이스에 추가 및 커밋
        #session.add(food_image)
        #session.commit()

        food_info = session.query(foodModel.Food).filter(foodModel.Food.fi_delYn == 'N').all()
        

        detectedMapping_objects = []

        #idx = [21,17,49,54,23]

        for food in food_info:
            if food.fi_name == TARGET_CLASSES[predicted_index]:
                detectedMapping_objects.append({
                    "fi_id": food.fi_id,
                    "fi_name": food.fi_name,
                    "fi_category": food.fi_category,
                    "fi_category1": food.fi_category1,
                    "fi_onetime_offer": food.fi_onetime_offer,
                    "fi_calorie": food.fi_calorie,
                    "fi_protein": food.fi_protein,
                    "fi_fat": food.fi_fat,
                    "fi_carbohydrate": food.fi_carbohydrate,
                    "fi_totalSugar": food.fi_totalSugar,
                    "fi_totalDietaryFiber": food.fi_totalDietaryFiber,
                    "fi_giRate": food.fi_giRate,
                    "fi_delYn": food.fi_delYn
                })

        return foodModel.ApiResponse(
            success_code="200",
            message="이미지 업로드 및 분류 완료",
            classificationResults=detectedMapping_objects
        )
        
    except Exception as e:
        session.rollback()
        return foodModel.ApiResponse(
                success_code="500",
                message="이미지 업로드 및 분류 실패",
                classificationResults=None
            )
    
    finally:
        session.close()


   #이미지를 받아와서 모델에 보내는 부분!
@router.post("/classifyFoodImageByYolo" , response_model=foodModel.ApiResponse)
async def classifyFoodImageByYolo(image: UploadFile):
    print("classifyFoodImageByYolo 호출됨")
    filename = str(uuid.uuid1()).replace("-", "")
    SAVE_PATH = "static/images/" + filename + ".jpg"
    
    # 이미지 파일 읽기
    image_bytes = await image.read()
    
    # 원본 이미지 저장
    #with open(SAVE_PATH, "wb") as buffer:
       # buffer.write(image_bytes)

    # 이미지 크롭 전에 원본이미지 저장
    # FoodImage 객체 생성
    current_dt = datetime.now().strftime("%Y%m%d%H%M%S%f")[:16]
    food_image = foodModel.FoodImage(
        fim_image_path=SAVE_PATH,
        fim_image_susses_yn='N',
        fim_insert_dt=current_dt
    )
    
    # 데이터베이스에 추가 및 커밋
    #session.add(food_image)
    #session.commit()
    print("classifyFoodImageByYolo 원본 이미지 저장 완료")
    
    TARGET_CLASSES = get_mobilenet_classes("MOBILENET_1")
    print(len(TARGET_CLASSES))
    classification_success = "N"
    detected_objects = []
    cropped_images = []
    print("classifyFoodImageByYolo yolo 모델로 객체 탐지 시작")
    try:
        # YOLO 모델 로드 (음식 객체 탐지용)
        yolo_model = YOLO("model/yolov8m.pt")  # YOLO 모델 경로
        
        # 이미지를 OpenCV 형태로 변환
        nparr = np.frombuffer(image_bytes, np.uint8)
        cv_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # YOLO로 객체 탐지
        results = yolo_model(cv_image)
        
        # 탐지된 객체들 처리
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # 바운딩 박스 좌표 추출
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    
                   
                    # 이미지 크롭
                    cropped_image = cv_image[y1:y2, x1:x2]
                    
                    # 크롭된 이미지를 분류 모델에 입력할 형태로 변환
                    cropped_pil = Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
                    cropped_pil = cropped_pil.resize((224, 224))
                    cropped_array = np.array(cropped_pil) / 255.0
                    cropped_array = np.expand_dims(cropped_array, axis=0)
                    
                     # 탐지된 객체 정보 저장
                    detected_objects.append({
                        "image_array": cropped_array,
                        "class_id": class_id,
                        "yolo_confidence": confidence,
                        "bbox": [x1, y1, x2, y2]
                    })
                    print(f"Detected {class_id}  with confidence {confidence:.2f} at [{x1}, {y1}, {x2}, {y2}]")
        print("classifyFoodImageByYolo yolo 모델로 객체 탐지 완료")

        TARGET_CLASSES1 = get_mobilenet_classes("MOBILENET_1")
        # 분류 모델 로드
        classification_model = load_model("model/ultra_small_food_classifier_v2.keras")
        # 각 크롭된 이미지에 대해 분류 수행

        print("classifyFoodImageByYolo MobileNet 모델로 분류 시작")
        classification_results = []
        for idx, crop_data in enumerate(detected_objects):

            #if crop_data["yolo_confidence"] < 0.7:
            # YOLO 탐지 정확도가 낮은 경우, MobileNet으로 재분류
            predictions = classification_model.predict(crop_data["image_array"])
            predicted_index = int(np.argmax(predictions[0]))
            class_confidence = float(np.max(predictions[0]))
            print(f"MOBILENET Classified {TARGET_CLASSES1[predicted_index]} with confidence {class_confidence:.2f} label_index {predicted_index}")
                
            # 크롭된 이미지 저장
            crop_filename = f"{filename}_crop_{idx}.jpg"
            crop_save_path = f"static/crop/{crop_filename}"
            
            # 크롭된 이미지를 BGR로 다시 변환하여 저장
            x1, y1, x2, y2 = crop_data["bbox"]
            cropped_bgr = cv_image[y1:y2, x1:x2]
            cv2.imwrite(crop_save_path, cropped_bgr)

            if crop_data["yolo_confidence"] > 0.7:
                classification_success = "Y"

            # 크롭된 이미지 한번더 판단하여 디비에저장
            food_detected_image = foodModel.foodDetectedImage(
                fdi_image_path=crop_save_path,
                fdi_image_susses_yn=classification_success,
                fdi_image_classified_accuracy=class_confidence,
                fdi_image_class_idx=predicted_index,
                fim_id=food_image.fim_id,  # foodImage의 ID를 참조
                fdi_insert_dt=current_dt
            )
            #session.add(food_detected_image)
            #session.commit()

            classification_results.append({
                "class_id": predicted_index,
                "fi_name": TARGET_CLASSES1[predicted_index],
                "classification_confidence": class_confidence,
                "image_path": crop_save_path
            })
        print("classifyFoodImageByYolo MobileNet 모델로 분류 종료")
        
        print("-"* 50)

        print("classifyFoodImageByYolo DB음식 정보와 매핑 시작")
        # 음식 정보 조회 후에 탐지한 객체와 매핑하여 정보 저장
        food_info = session.query(foodModel.Food).filter(foodModel.Food.fi_delYn == 'N').all()
        detectedMapping_objects = []

        detected_objects = [{
                        "image_path": 'static/crop/dd62b2ae6cfd11f09b7e089798a2c230_crop_1.jpg',
                        "class_id": 20,
                        "fi_name" : "배추김치",
                        "yolo_confidence": 0.8
                    },{
                        "image_path": 'static/crop/gogocrop.png',
                        "class_id": 1,
                        "fi_name" : "고등어구이",
                        "yolo_confidence": 0.8
                    },
                    {
                        "image_path": 'static/crop/kimbib.png',
                        "class_id": 45,
                        "fi_name" : "김밥",
                        "yolo_confidence": 0.8
                    },{
                        "image_path": 'static/crop/dd62b2ae6cfd11f09b7e089798a2c230_crop_2.jpg',
                        "class_id": 0,
                        "fi_name" : "감자튀김",
                        "yolo_confidence": 0.8
                    }]

        # 탐지된 객체와 음식 정보 매핑
        # 처음 yolo로 탐지한 객체들을 기준으로 매핑하되 정확도부분이 낮은것은
        # 다시 mobileNet으로 판단하여 매핑한다
        # TODO 나중에 detected_objects를  classification_results로 수정해야된다 모델이 적용됬을때의 의미다
        for item in detected_objects:
            target_food_info = next((food for food in food_info if food.fi_name == item["fi_name"]), None)
            if target_food_info : 
                detectedMapping_objects.append({
                    "fi_id": target_food_info.fi_id,
                    "fi_name": target_food_info.fi_name,
                    "fi_category": target_food_info.fi_category,
                    "fi_category1": target_food_info.fi_category1,
                    "fi_onetime_offer": target_food_info.fi_onetime_offer,
                    "fi_calorie": target_food_info.fi_calorie,
                    "fi_protein": target_food_info.fi_protein,
                    "fi_fat": target_food_info.fi_fat,
                    "fi_carbohydrate": target_food_info.fi_carbohydrate,
                    "fi_totalSugar": target_food_info.fi_totalSugar,
                    "fi_totalDietaryFiber": target_food_info.fi_totalDietaryFiber,
                    "fi_giRate": target_food_info.fi_giRate,
                    "fi_delYn": target_food_info.fi_delYn,
                    "fi_image_url" : item["image_path"]
                })

        return foodModel.ApiResponse(
            success_code="200",
            message="이미지 업로드 및 분류 완료",
            classificationResults=detectedMapping_objects
        )


    except Exception as e:
        session.rollback()
        return foodModel.ApiResponse(
                success_code="500",
                message="이미지 업로드 및 분류 실패",
                classificationResults=None
            )
 
    finally:
        session.close()

        

    

