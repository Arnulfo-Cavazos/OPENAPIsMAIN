from fastapi import FastAPI, HTTPException
import pandas as pd
from pydantic import BaseModel
from github import Github
import os
from dotenv import load_dotenv

# Cargar variables de entorno (.env)
load_dotenv()

app = FastAPI(title="Employee CSV API")

# Variables de entorno
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_FILE_PATH = os.getenv("GITHUB_FILE_PATH")

# Inicializar GitHub
g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPO)

# Función para cargar el CSV desde GitHub
def load_csv():
    contents = repo.get_contents(GITHUB_FILE_PATH)
    csv_data = contents.decoded_content.decode("utf-8")
    df = pd.read_csv(pd.compat.StringIO(csv_data))
    return df

# Función para guardar cambios al CSV y hacer commit
def save_csv(df, message="Update data.csv"):
    csv_buffer = df.to_csv(index=False)
    contents = repo.get_contents(GITHUB_FILE_PATH)
    repo.update_file(
        GITHUB_FILE_PATH,
        message,
        csv_buffer,
        contents.sha
    )

# Modelo para recibir datos
class Employee(BaseModel):
    num: int
    Name: str
    TimeOffBalance: float
    Job: str
    Address: str
    RequestedTimeOff: int

# ---- ENDPOINTS ---- #

@app.get("/")
def root():
    return {"message": "Welcome to the Employee CSV API!"}

@app.get("/employees")
def get_all_employees():
    df = load_csv()
    return df.to_dict(orient="records")

@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    df = load_csv()
    emp = df[df['num'] == employee_id]
    if emp.empty:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp.to_dict(orient="records")[0]

@app.get("/search/")
def search_employee(name: str):
    df = load_csv()
    result = df[df['Name'].str.contains(name, case=False, na=False)]
    if result.empty:
        raise HTTPException(status_code=404, detail="Employee not found")
    return result.to_dict(orient="records")

@app.post("/employees")
def add_employee(emp: Employee):
    df = load_csv()
    if emp.num in df['num'].values:
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    new_row = pd.DataFrame([emp.dict()])
    df = pd.concat([df, new_row], ignore_index=True)
    save_csv(df, message=f"Add employee {emp.Name}")
    return {"message": f"Employee {emp.Name} added successfully"}

@app.put("/employees/{employee_id}")
def update_employee(employee_id: int, emp: Employee):
    df = load_csv()
    index = df.index[df['num'] == employee_id].tolist()
    if not index:
        raise HTTPException(status_code=404, detail="Employee not found")
    df.loc[index[0]] = emp.dict()
    save_csv(df, message=f"Update employee {emp.Name}")
    return {"message": f"Employee {emp.Name} updated successfully"}
