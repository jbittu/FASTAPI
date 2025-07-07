from fastapi import FastAPI ,Path, HTTPException,Query
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel,Field, computed_field
from typing import Annotated, List, Dict,Literal, Optional
app= FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="The ID of the patient", example="P001")]
    name: Annotated[str, Field(..., description="The name of the patient", example="John Doe")]
    city: Annotated[str, Field(..., description="The city of the patient", example="New York")]
    # ail: Annotated[str, Field(..., description="The email of the patient", example="john.doe@example.com")]
    age: Annotated[int, Field(..., description="The age of the patient", example=30)]
    gender: Annotated[Literal['male','female','other'], Field(..., description="Genter of the patient", example="male")]
    height: Annotated[float, Field(..., description="The height of the patient in cm", example=175.5)]
    weight: Annotated[float, Field(..., description="The weight of the patient in kg", example=70.0)]
    

def load_data():
    with open('patients.json', 'r') as file:
        data = json.load(file)
    return data

@computed_field
@property
def bmi(self) -> float:
    """Calculate the Body Mass Index (BMI) of the patient."""
    return round(self.weight / ((self.height / 100) ** 2), 2)

@computed_field
@property
def verdict(self) -> str:
    """Determine the health verdict of the patient based on BMI."""
    bmi = self.bmi
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal weight"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obesity"
    
def save_data(data):
    with open('patients.json','w') as file:
        json.dump(data, file)

@app.get("/")
def hello():
    return {'message':'Hello, World!'}

@app.get("/patients")
def get_patients():
    data = load_data()
    return data

@app.get("/patients/{patient_id}")
def get_patient(patient_id: str = Path(..., description="The ID of the patient", example="P001")):
    data  = load_data()
    if patient_id in data:
        return data[patient_id]
    else:
        raise HTTPException(status_code=404, detail="patient not found")

@app.get("/sorted-patients")
def get_sorted_patients(sort_by: str = Query(..., description = "Field to sortby", example="age"), order: str = Query(..., description= "sort order asc or desc")):
    
    valid_fields = ["age", "name", "height", "weight"]

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort field select from {valid_fields}")

    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid sort order select from ['asc', 'desc']")
    
    data = load_data()
    sort_order= True if order == "asc" else False
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by), reverse=sort_order)

    return sorted_data

@app.post("/create")
def create_patient(patient: Patient):
    data = load_data()
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists")
    
    data[patient.id] = patient.model_dump(exclude=['id'])  # Exclude the id field from the model dump
    
    save_data(data)
    return JSONResponse(status_code=201, content={"message": "Patient created successfully", "patient": patient.model_dump()})

# Update an existing patient for this we need to build new pydantic model because in above pydantic model every field is required and during update it in not necessary for every field to have value
class UpdatePatient(BaseModel):
    name: Annotated[Optional[str], Field(description="The name of the patient", example="John Doe")] = None
    city: Annotated[Optional[str], Field(description="The city of the patient", example="New York")] = None
    age: Annotated[Optional[int], Field(description="The age of the patient", example=30)] = None
    gender: Annotated[Optional[Literal['male','female','other']], Field(description="Genter of the patient", example="male")] = None
    height: Annotated[Optional[float], Field(description="The height of the patient in cm", example=175.5)] = None
    weight: Annotated[Optional[float], Field(description="The weight of the patient in kg", example=70.0)] = None

@app.put("/update/{patient_id}")
def update_patient(patient_id: str, patient_update: UpdatePatient):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")

    existing_patient_info = data[patient_id]
    updated_patient_info = patient_update.model_dump(exclude_unset=True)  # Exclude unset fields to only update provided fields

    for key, value in updated_patient_info.items():
        if value is not None:  # Only update fields that are provided
            existing_patient_info[key] = value

    #now existing_patient_info -> pydantic object of calss Patient -> it will recalculate  computed fields like bmi and verdict -> pydantic object -> dict -> update the data dict -> save date
    existing_patient_info['id'] = patient_id  # Ensure the ID is set correctly
    existing_patient_info_obj = Patient(**existing_patient_info)  # Convert back to Patient model to
    existing_patient_info = existing_patient_info_obj.model_dump(exclude='id')  # Exclude the id field from the model dump
    data[patient_id] = existing_patient_info
    save_data(data)
    return JSONResponse(status_code=200, content={"message": "Patient updated successfully"})


# Delete a patient
@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")

    del data[patient_id]
    save_data(data)
    return JSONResponse(status_code=200, content={"message": "Patient deleted successfully"})


