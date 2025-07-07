from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Optional,Annotated
#using field we can add validation to the fields
class Patient(BaseModel):
    id: str
    name: Annotated[str, Field(min_length=3, max_length=50, 
                               description="The name of the patient must be between 3 and 50 characters",
                               title="Patient Name", example="John Doe")]  # Annotated is used to add metadata to the field
    # Field is used to add metadata to the field, like description, title, example, etc.
    email: EmailStr # automatic validation for email format given by pydantic without regex
    age: int=Field(gt=0,lt=100)  # gt means greater than, so age must be greater than 0
    height: float=Field(gt=0)  # gt means greater than, so height must be greater than 0
    weight: float= Field(gt=0)  # gt means greater than, so weight must be greater than 0
    alergys: Optional[List[str]] = None  # now this field become optional i.e not required
    # If we want to make it required, remove the Optional, optional filed default value is always None
    contact_details: dict[str, str]
    marital_status: bool = False  # dy default value is False


patient_data = {"id": "P001", "name": "John Doe","email": "john.doe@example.com", "age": 30, "height": 175.5, "weight": 70.0,
                "alergys": ["pollen", "nuts"],
                "contact_details": {"email": "john.doe@example.com", "phone": "123-456-7890"},
                "marital_status": True}

Patient1= Patient(**patient_data)

def insert_patient_data(patient: Patient):
    # Here you would typically insert the patient data into a database
    # For this example, we will just return the patient data
    return patient

inserted_patient = insert_patient_data(Patient1)
