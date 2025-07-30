# Dockerfile
# python 3.10 버전 이미지를 base로 사용
FROM python:3.12.9 
#app 디렉토리 생성
RUN mkdir -p /app
# 컨테이너 내에서의 작업 디렉토리를 /app으로 설정
WORKDIR /app 
# 호스트의 현재 디렉토리(.)를 /app에 복사
COPY . /app
# requirements.txt에 명시된 패키지들을 설치
RUN pip install -r requirements.txt 
# 컨테이너가 시작될 때 main.py를 실행하여 FastAPI 애플리케이션을 구동
CMD [ "python", "main.py" ]  