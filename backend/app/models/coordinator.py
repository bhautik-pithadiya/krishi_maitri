from pydantic import BaseModel

class CoordinatorRequest(BaseModel):
    task_type: str  # e.g., 'disease_diagnosis', 'weather_forecast', 'generate_voice'
    payload: dict   # dynamic data
