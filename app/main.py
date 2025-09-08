from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os

app = FastAPI()

EXCEL_PATH = "data/users_data_2.xlsx"

# 📦 Modelo para agregar una fila
class UserData(BaseModel):
    num: int
    Name: str
    Job: str
    Address: str
    RequestedTimeOff: int

# 📄 Endpoint para visualizar todos los datos
@app.get("/users", summary="Get all user data from Excel")
def get_users():
    if not os.path.exists(EXCEL_PATH):
        raise HTTPException(status_code=404, detail="Excel file not found")
    df = pd.read_excel(EXCEL_PATH)
    return df.to_dict(orient="records")

# ➕ Endpoint para agregar una nueva fila
@app.post("/users", summary="Add a new user row to Excel")
def add_user(user: UserData):
    if os.path.exists(EXCEL_PATH):
        df = pd.read_excel(EXCEL_PATH)
    else:
        df = pd.DataFrame(columns=["num", "Name", "Job", "Address", "RequestedTimeOff"])
    
    new_row = {
        "num": user.num,
        "Name": user.Name,
        "Job": user.Job,
        "Address": user.Address,
        "RequestedTimeOff": user.RequestedTimeOff
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(EXCEL_PATH, index=False)
    return {"message": "User added successfully", "data": new_row}

