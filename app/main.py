from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
from github import Github
import os
from dotenv import load_dotenv
import logging
from io import StringIO

# ---------------------
# CONFIG
# ---------------------
logging.basicConfig(level=logging.INFO)
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_FILE_PATH = os.getenv("GITHUB_FILE_PATH")

app = FastAPI(title="Employee CSV API", version="1.0.0")

# ---------------------
# INIT GITHUB
# ---------------------
g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPO)

# ---------------------
# CACHE
# ---------------------
cached_df = None

# ---------------------
# MODELS
# ---------------------
class Employee(BaseModel):
    num: int
    Name: str
    TimeOffBalance: float
    Job: str
    Address: str
    RequestedTimeOff: int

# ---------------------
# UTILS
# ---------------------
def load_csv():
    global cached_df
    if cached_df is not None:
        return cached_df.copy()
    try:
        logging.info("Loading CSV from GitHub...")
        contents = repo.get_contents(GITHUB_FILE_PATH)
        csv_data = contents.decoded_content.decode("utf-8")
        df = pd.read_csv(StringIO(csv_data))
        cached_df = df.copy()
        logging.info(f"CSV loaded with {len(df)} rows")
        return df
    except Exception as e:
        logging.error(f"Failed to load CSV: {e}")
        raise HTTPException(status_code=500, detail="Failed to load CSV from GitHub")

def save_csv(df, message="Update data.csv"):
    try:
        csv_buffer = df.to_csv(index=False)
        contents = repo.get_contents(GITHUB_FILE_PATH)
        repo.update_file(GITHUB_FILE_PATH, message, csv_buffer, contents.sha)
        logging.info("CSV updated and committed to GitHub")
        global cached_df
        cached_df = df.copy()
    except Exception as e:
        logging.error(f"Failed to save CSV: {e}")
        raise HTTPException(status_code=500, detail="Failed to save CSV to GitHub")

# ---------------------
# ENDPOINTS
# ---------------------
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

@app.get("/openapi.yaml", include_in_schema=False)
def get_openapi_yaml():
    """
    Serve the OpenAPI YAML directly for HR tools.
    """
    from fastapi.openapi.utils import get_openapi
    import yaml
    openapi_schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
    with open("openapi.yaml", "w") as f:
        yaml.dump(openapi_schema, f)
    return FileResponse("openapi.yaml", media_type="application/yaml")
