# backend/routers/people.py
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
import os, uuid
from .. import database, models, utils, schemas

router = APIRouter(prefix="/api/people", tags=["people"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/add", response_model=schemas.PersonOut)
async def add_person(name: str = Form(...), image: UploadFile = File(...), db: Session = Depends(get_db)):
    # save uploaded image
    ext = os.path.splitext(image.filename)[1] or ".jpg"
    fname = f"{name}_{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(utils.FACES_DIR, fname)
    with open(save_path, "wb") as f:
        content = await image.read()
        f.write(content)

    # compute embedding (use cv2 to decode)
    import cv2, numpy as np
    arr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    emb = utils.img_to_embedding(img)
    if emb is None or emb.size==0:
        # still create person but embedding missing
        embedding_json = None
    else:
        embedding_json = utils.emb_to_json(emb)

    person = models.Person(name=name, image_path=save_path, embedding_json=embedding_json)
    db.add(person)
    try:
        db.commit()
        db.refresh(person)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Person add failed: "+str(e))
    return person

@router.delete("/{person_id}", status_code=200)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Xóa file ảnh nếu tồn tại
    if person.image_path and os.path.exists(person.image_path):
        try:
            os.remove(person.image_path)
        except Exception as e:
            print(f"Warning: could not delete image file: {e}")

    db.delete(person)
    db.commit()
    return {"message": "Person deleted successfully"}

@router.get("/", response_model=list[schemas.PersonOut])
def list_people(db: Session = Depends(get_db)):
    return db.query(models.Person).all()
