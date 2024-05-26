from fastapi import FastAPI, Form, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException
import os
import json
from uuid import UUID

app = FastAPI()

# Directory for uploaded files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Directory for problem files
PROBLEMS_DIR = "problems"

# Templates directory
templates = Jinja2Templates(directory="templates")

# Load questions from JSON files
questions = {}

for filename in os.listdir(PROBLEMS_DIR):
    if filename.endswith(".json"):
        filepath = os.path.join(PROBLEMS_DIR, filename)
        with open(filepath, 'r') as file:
            data = json.load(file)
            questions[data["pagekey"]] = data["question"]

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "pages": questions.items()})

@app.get("/page/{page_id}", response_class=HTMLResponse)
async def read_page(request: Request, page_id: UUID):
    question = questions.get(str(page_id))
    if question:
        return templates.TemplateResponse("page.html", {"request": request, "page_id": page_id, "question": question})
    else:
        raise HTTPException(status_code=404, detail="Page not found")

@app.post("/page/{page_id}", response_class=HTMLResponse)
async def submit_page(request: Request, page_id: UUID, text: str = Form(...)):
    question = questions.get(str(page_id))
    if question:
        return templates.TemplateResponse("page.html", {"request": request, "page_id": page_id, "question": question, "text": text})
    else:
        raise HTTPException(status_code=404, detail="Page not found")

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        file_location = f"{UPLOAD_DIR}/{file.filename}"
        with open(file_location, 'wb') as f:
            f.write(contents)
    except Exception as e:
        return {"message": f"There was an error uploading the file: {str(e)}"}
    finally:
        await file.close()

    return {"message": f"Successfully uploaded {file.filename}"}

# Static files for uploads
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Run the app with: uvicorn main:app --reload
