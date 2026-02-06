from fastapi import FastAPI , Path , HTTPException , Query
import json

app = FastAPI()

def load_data():
    with open("patients.json", "r") as f:
        data = json.load(f)
    return data

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