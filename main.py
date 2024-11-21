import os
import uuid
import asyncio
from typing import Annotated

from fastapi import (FastAPI,
                     UploadFile,
                     File,
                     BackgroundTasks,
                     HTTPException)


app = FastAPI()

DATA_FOLDER = ".\data"
os.makedirs(DATA_FOLDER, exist_ok=True)


async def process_file(filename: str, filecontent: Annotated[bytes, File()]):
    print(f"Обробка файлу: {filename}, розмір: {len(filecontent)} байт.")
    await asyncio.sleep(5) 

    file_path = os.path.join(DATA_FOLDER, filename)
    with open(file_path, "wb") as save_file:
        save_file.write(filecontent)

    print(f"Файл {filename} оброблено та збережено за адресою {file_path}")


@app.post("/upload/", status_code=202, summary = "Завантаження файлу")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):

    if not file.filename.endswith((".txt", ".csv", ".json")):
        raise HTTPException(status_code=400, detail="Невірний формат файлу. Доступні формати: .txt, .csv, .json")

    unique_filename = f"{uuid.uuid4()}_{file.filename}"

    background_tasks.add_task(process_file, filename=unique_filename, filecontent=await file.read())

    return {
        "message": f"Файл {file.filename} завантажено та обробляється у фоні.",
        "task_id": unique_filename.split("_")[0], 
        "status": "Прийнято",
    }


@app.get("/")
async def read_root():
    return {"message": "Система обробки файлів готова"}
