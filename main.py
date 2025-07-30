from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from apis.router import api_router

app = FastAPI(
    title="FastAPI Example",
    description="A simple FastAPI example",
    version="1.0.0",
    docs_url="/docs"
)

# 정적 파일 서빙 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router, prefix="/api", tags=["api"])



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0" ,port=8000, reload=True)
