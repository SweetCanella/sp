from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import ValidationError
from pydantic import BaseModel
import kr1.models as models

app = FastAPI()

feedbacks_store = []

# 1.1
@app.get("/")
async def root():
    return {"message": "Авторелоад действительно работает"}

# 1.2 корень  занят
@app.get("/html")
async def get_html():
    return FileResponse("index.html")

# 1.3
@app.post("/calculate")
async def calculate(num1: float, num2: float):
    return {"sum": num1 + num2}

# 1.4
my_user = models.User(name="Ваше Имя и Фамилия", id=1)

@app.get("/users")
async def get_user():
    return my_user

#1.5
@app.post("/user")
async def check_adult(user: models.UserAge):
    is_adult = user.age >= 18
    return {
        "name": user.name,
        "age": user.age,
        "is_adult": is_adult
    }

# 2.1 + 2.2
@app.post("/feedback")
async def add_feedback_validated(feedback: models.FeedbackValidated):
    feedbacks_store.append(feedback.model_dump())
    return {"message": f"Спасибо, {feedback.name}! Ваш отзыв сохранён."}

@app.get("/feedbacks")
async def get_all_feedbacks():
    return feedbacks_store