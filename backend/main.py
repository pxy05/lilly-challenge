from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import uvicorn
import json
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INTERNAL_SERVER_ERROR = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Internal server error"
)

class Medicine(BaseModel):
    name: str
    price: Optional[float] = None

class CreateMedicineRequest(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., ge=0)

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v):
        if v.strip() == "":
            raise ValueError('Name cannot be empty string')
        return v.strip()

class UpdateMedicineRequest(BaseModel):
    price: float = Field(..., ge=0)

class MedicineResponse(BaseModel):
    code: int
    medicine: Optional[Medicine] = None
    message: Optional[str] = None
    error: Optional[str] = None

class AverageResponse(BaseModel):
    code: int
    average_price: Optional[float] = None

def does_med_exist(name: str) -> bool:
    try:
        with open('data.json') as meds:
            data = json.load(meds)
            for med in data["medicines"]:
                if med['name'] == name:
                    return True
        return False
    except Exception as e:
        logging.error(e)
        raise INTERNAL_SERVER_ERROR

@app.get("/medicines", status_code=status.HTTP_200_OK)
def get_all_meds():

    data = {}
    try:
        with open('data.json') as meds:
            data = json.load(meds)
    except Exception as e:
        logging.error(e)
        raise INTERNAL_SERVER_ERROR
    
    logging.info(f"Successful /medicines call")
    return data

@app.get("/medicines/{name}", status_code=status.HTTP_200_OK, response_model=MedicineResponse)
def get_single_med(name: str):

    name = name.strip()

    if (name == ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name cannot be empty string"
        )


    medicine = {}
    try:
        with open('data.json') as meds:
            data = json.load(meds)
            for med in data["medicines"]:
                if med['name'] == name:
                    medicine = med

    except Exception as e:
        logging.error(e)
        raise INTERNAL_SERVER_ERROR

    if (medicine == {}):
        logging.info(f"Medicine: '{name}' not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found"
        )
    else:
        return {
            "code": 200,
            "medicine": medicine
        }



@app.post("/medicines", status_code=status.HTTP_201_CREATED, response_model=MedicineResponse)
def create_med(medicine: CreateMedicineRequest):

    if does_med_exist(medicine.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medicine already exists"
        )

    try:
        with open('data.json', 'r+') as meds:
            db = json.load(meds)
            new_med = {"name": medicine.name, "price": medicine.price}
            db["medicines"].append(new_med)
            meds.seek(0)
            json.dump(db, meds)
            meds.truncate()
        
        result = get_single_med(medicine.name)
        return {
            "code": 201,
            "message": f"Medicine created successfully with name: {medicine.name}",
            "medicine": result["medicine"]
            }
    except Exception as e:
        logging.error(e)
        raise INTERNAL_SERVER_ERROR
        


@app.patch("/medicines/{name}", status_code=status.HTTP_200_OK, response_model=MedicineResponse)
def update_med(name: str, update_data: UpdateMedicineRequest):

    name = name.strip()
    
    if (name == ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name cannot be empty string"
        )

    try:
        with open('data.json', 'r+') as meds:
            db = json.load(meds)
            for med in db["medicines"]:
                if med['name'] == name:
                    med['price'] = update_data.price
                    meds.seek(0)
                    json.dump(db, meds)
                    meds.truncate()
                    result = get_single_med(name)
                    return {
                        "code": 200,
                        "message": f"Medicine updated successfully with name: {name}",
                        "medicine": result["medicine"]
                        }
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(e)
        raise INTERNAL_SERVER_ERROR

@app.delete("/medicines/{name}", status_code=status.HTTP_200_OK, response_model=MedicineResponse)
def delete_med(name: str):

    name = name.strip()
    
    if (name == ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name cannot be empty string"
        )
    try:
        with open('data.json', 'r+') as meds:
            db = json.load(meds)
            for med in db["medicines"]:
                if med['name'] == name:
                    db["medicines"].remove(med)
                    meds.seek(0)
                    json.dump(db, meds)
                    meds.truncate()
                    return {
                        "code": 200,
                        "message": f"Medicine deleted successfully with name: {name}"
                        }
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(e)
        raise INTERNAL_SERVER_ERROR

# Add your average function here
@app.get("/average", status_code=status.HTTP_200_OK, response_model=AverageResponse)
def average_price():

    total: float = float(0)
    db_len: int = 0
    
    try:
        with open('data.json', 'r+') as meds:
            db = json.load(meds)
            for med in db['medicines']:
                price = med['price']
                if (price is not None and isinstance(price, (float))):
                    total += med['price']
                    db_len += 1
        
            if db_len == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No medicines with prices found"
                )
        
            return {
                "code": 200,
                "average_price": total/db_len
                }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(e)
        raise INTERNAL_SERVER_ERROR

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
