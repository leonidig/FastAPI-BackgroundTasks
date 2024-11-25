import os
import asyncio
from uuid import uuid4

from fastapi import (
    APIRouter,
    BackgroundTasks,
    UploadFile,
    HTTPException,
    Depends
)

from sqlalchemy import select, update
from ..db import get_session, File


api_router = APIRouter(prefix="/api", tags=["головний роутер для додатку"])

DATA_FOLDER = "./files_data"
os.makedirs(DATA_FOLDER, exist_ok=True)


@api_router.get("/")
async def index():
    return {"message": "Привіт з ФастАПІ з бекграунд-таскс"}


async def file_load_progress(file_id: str, session = Depends(get_session)):
    selected_file = session.scalar(select(File).where(File.id == file_id))
    if not selected_file:
        raise HTTPException(status_code=404, detail="Файл не знайден")

    for chunk in range(11):
        upd = update(File).where(File.id == file_id).values(
            progress = chunk * 10
        )
        session.execute(upd)
        session.commit() 
        print(f"Оброблено {chunk * 10}%")
        await asyncio.sleep(1)

    return {"message": "прогрес оновлено"}
    

async def process_file(filename: str, filecontent: bytes):
    print(f"Обробка файлу: {filename}, розмір: {len(filecontent)} байт.")
    await asyncio.sleep(5)

    file_path = os.path.join(DATA_FOLDER, filename)
    with open(file_path, "wb") as save_file:
        save_file.write(filecontent)

    print(f"Файл {filename} оброблено та збережено за адресою {file_path}")


@api_router.post("/upload/", status_code=202, summary="Завантаження файлу")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    session = Depends(get_session),
):
    if not file.filename.endswith((".txt", ".csv", ".json")):
        raise HTTPException(
            status_code=400, detail="Невірний формат файлу. Доступні формати: .txt, .csv, .json"
        )
    unique_filename = f"{uuid4()}_{file.filename}"
    file_content = await file.read()

    background_tasks.add_task(process_file, filename=unique_filename, filecontent=file_content)
    new_file = File(
        id=unique_filename.split("_")[0],
        filename=file.filename,
        progress=0  
    )
    session.add(new_file)

    background_tasks.add_task(file_load_progress, file_id=new_file.id, session=session)

    return {
        "message": f"Файл {file.filename} завантажено та обробляється у фоні.",
        "task_id": new_file.id,
        "status": "Прийнято"
    }