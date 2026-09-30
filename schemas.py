from pydantic import BaseModel

class UserInput(BaseModel):
    goal: str = "weight loss"
    intensity: str = "medium"
    age: int = 25
    weight: float = 70
    feedback: str = ""