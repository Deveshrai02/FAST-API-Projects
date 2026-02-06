from fastapi import FastAPI , Path , HTTPException , Query
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel , Field , computed_field
from typing import Annotated , Literal, Optional

app = FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(...,description="Unique identifier for the patient" , example="P001")]
    name: Annotated[str, Field(...,description="Name of the patient" , example="John Doe")]
    city:Annotated[str, Field(...,description="City of the patient" , example="New York")]
    age: Annotated[int, Field(...,gt=0,lt=120,description="Age of the patient" , example=30)]
    gender: Annotated[Literal["Male", "Female", "Other"], Field(...,description="Gender of the patient" , example="Male")]
    height: Annotated[float, Field(...,gt=0,description="Height of the patient in mtrs" , example=17.5)]
    weight: Annotated[float, Field(...,gt=0,description="Weight of the patient in kg" , example=70.0)]
    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)
    @computed_field
    @property
    def verdict(self) -> str:
        bmi = self.bmi
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 25:
            return "Normal weight"
        elif 25 <= bmi < 30:
            return "Overweight"
        else:
            return "Obese"
        
class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(None,description="Name of the patient" , example="John Doe")]
    city:Annotated[Optional[str], Field(None,description="City of the patient" , example="New York")]
    age: Annotated[Optional[int], Field(None,gt=0,lt=120,description="Age of the patient" , example=30)]
    gender: Annotated[Optional[Literal["Male", "Female", "Other"]], Field(None,description="Gender of the patient" , example="Male")]
    height: Annotated[Optional[float], Field(None,gt=0,description="Height of the patient in mtrs" , example=17.5)]
    weight: Annotated[Optional[float], Field(None,gt=0,description="Weight of the patient in kg" , example=70.0)]


def load_data():
    with open("patients.json", "r") as f:
        data = json.load(f)
    return data
def save_data(data):
    with open("patients.json", "w") as f:
        json.dump(data, f, indent=4)

@app.get("/")
def hello():
    return {"message": "Patient Management System API"}

@app.get("/about")
def about():
    return {"message": "This is a simple FastAPI application for managing patient data."}

@app.get("/view")
def view_patients():
    data = load_data()
    return {"patients": data}

@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description="The ID of the patient to retrieve" , example="P001")):
    data = load_data()
    if patient_id in data:
        return {"patient": data[patient_id]}
    raise HTTPException(status_code=404, detail="Patient not found")

@app.get("/sort")
def sort_patients(sort_by: str = Query(..., description="Sort on basis of height , weight or bmi" , example="height") , 
                  order: str = Query("asc", description="Sort order: asc or desc" , example="asc")):
    valid_sort_fields = ["height", "weight", "bmi"]
    if sort_by not in valid_sort_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort field. Must be one of {valid_sort_fields}")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid sort order. Must be 'asc' or 'desc'")
    data = load_data()
    sorted_data = sorted(data.values(), key=lambda x: x[sort_by], reverse=(order == "desc"))
    return {"patients": sorted_data}

@app.post("/create")
def create_patient(patient: Patient):
    data = load_data()
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient already exists")
    data[patient.id] = patient.model_dump(exclude=['id'])
    save_data(data)
    return JSONResponse(status_code=201, content={"message": "Patient created successfully"})

@app.put("/edit/{patient_id}")
def update_patient(patient_id: str, patient_update: PatientUpdate):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    updated_patient = data[patient_id].copy()
    for key, value in patient_update.model_dump(exclude_unset=True).items():
        updated_patient[key] = value
    updated_patient["bmi"] = round(updated_patient["weight"] / (updated_patient["height"] ** 2), 2) if updated_patient["height"] > 0 else 0
    updated_patient["verdict"] = "Underweight" if updated_patient["bmi"] < 18.5 else "Normal weight" if updated_patient["bmi"] < 25 else "Overweight" if updated_patient["bmi"] < 30 else "Obese"
    data[patient_id] = updated_patient
    save_data(data)
    return JSONResponse(status_code=200, content={"message": "Patient updated successfully"})

@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    del data[patient_id]
    save_data(data)
    return JSONResponse(status_code=200, content={"message": "Patient deleted successfully"})