from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import PlainTextResponse
from PIL import Image
from io import BytesIO
import pytesseract
import requests
from PyPDF2 import PdfReader

app = FastAPI()

def image_ocr_from_link(image_url, file_name):
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    ocr_text = pytesseract.image_to_string(image)
    save_ocr_text(ocr_text, file_name)
    return file_name

def image_ocr_from_file(file, file_name):
    image = Image.open(BytesIO(file))
    ocr_text = pytesseract.image_to_string(image)
    save_ocr_text(ocr_text, file_name)
    return file_name

def pdf_ocr_from_link(pdf_url, file_name):
    response = requests.get(pdf_url)
    with BytesIO(response.content) as pdf_buffer:
        reader = PdfReader(pdf_buffer)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    save_ocr_text(text, file_name)
    return file_name

def pdf_ocr_from_file(file, file_name):
    with BytesIO(file) as pdf_buffer:
        reader = PdfReader(pdf_buffer)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    save_ocr_text(text, file_name)
    return file_name

def save_ocr_text(text, file_name):
    file_path = f"/content/{file_name}.txt"  # Adjust the directory as needed
    with open(file_path, "w") as text_file:
        text_file.write(text)

@app.post("/image/link")
async def ocr_from_image_link(file_name: str, image_url: str):
    try:
        return {"file_path": image_ocr_from_link(image_url, file_name)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/image/file")
async def ocr_from_image_file(file: UploadFile = File(...), file_name: str = None):
    try:
        if file_name is None:
            file_name = file.filename.rsplit(".", 1)[0]
        contents = await file.read()
        return {"file_path": image_ocr_from_file(contents, file_name)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pdf/link")
async def ocr_from_pdf_link(file_name: str, pdf_url: str):
    try:
        return {"file_path": pdf_ocr_from_link(pdf_url, file_name)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pdf/file")
async def ocr_from_pdf_file(file: UploadFile = File(...), file_name: str = None):
    try:
        if file_name is None:
            file_name = file.filename.rsplit(".", 1)[0]
        contents = await file.read()
        return {"file_path": pdf_ocr_from_file(contents, file_name)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
