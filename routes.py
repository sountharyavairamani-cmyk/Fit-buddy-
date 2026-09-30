from fastapi import APIRouter
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

import hashlib

_original_md5 = hashlib.md5

def compatible_md5(*args, **kwargs):
    kwargs.pop("usedforsecurity", None)
    return _original_md5(*args, **kwargs)

hashlib.md5 = compatible_md5

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
router = APIRouter()


class UserInput(BaseModel):
    goal: str
    age: int
    weight: int
    intensity: str


@router.get("/login", response_class=HTMLResponse)
def login_page():
    with open("templates/login.html", "r", encoding="utf-8") as file:
        return file.read()


@router.get("/register", response_class=HTMLResponse)
def register_page():
    with open("templates/register.html", "r", encoding="utf-8") as file:
        return file.read()


def create_plan(data):

    if data.goal == "weight loss":

        days = [
            ("Day 1", "30 min brisk walking + 15 min jogging", "Protein-rich breakfast, vegetables, fruits and enough water."),
            ("Day 2", "20 min cardio + 15 min squats, lunges and planks", "Eggs/paneer/dal, vegetables and controlled portions of rice."),
            ("Day 3", "30 min cycling or jogging + 10 min core workout", "Lean protein, fruits, vegetables and plenty of water."),
            ("Day 4", "25 min cardio + 20 min bodyweight workout", "Balanced meals with protein, vegetables and whole grains."),
            ("Day 5", "30 min brisk walking + HIIT for 15 min", "Protein-rich foods, vegetables and fruits; limit sugary foods."),
            ("Day 6", "40 min light cardio + stretching", "Balanced diet with protein, vegetables and healthy carbohydrates."),
            ("Day 7", "Rest day + 20 min easy walking + stretching", "Healthy balanced meals and good hydration.")
        ]

        nutrition = "Focus on protein, vegetables, fruits and balanced carbohydrates. Limit excessive sugar, fried foods and junk food."

    elif data.goal == "muscle gain":

        days = [
            ("Day 1", "Chest + Triceps: Push-ups, chest press and triceps exercises", "Protein-rich meals with eggs, milk, paneer, chicken or dal."),
            ("Day 2", "Back + Biceps: Rows, pull-ups and biceps curls", "Protein + rice/oats + vegetables and fruits."),
            ("Day 3", "Legs: Squats, lunges and calf raises", "Protein-rich foods with enough carbohydrates."),
            ("Day 4", "Shoulders + Core: Shoulder press, lateral raises and planks", "Balanced protein, carbohydrates and vegetables."),
            ("Day 5", "Chest + Back: Push-ups, rows and light strength training", "High-protein balanced meals and enough water."),
            ("Day 6", "Legs + Shoulders: Squats, lunges and shoulder exercises", "Protein, rice/oats, vegetables and fruits."),
            ("Day 7", "Rest + light stretching and walking", "Balanced nutritious meals and hydration.")
        ]

        nutrition = "Include protein-rich foods such as eggs, milk, paneer, chicken and dal along with rice, oats, vegetables and fruits."

    else:

        days = [
            ("Day 1", "30 min cardio + full-body exercises", "Balanced meals with protein, vegetables and fruits."),
            ("Day 2", "30 min walking + squats and planks", "Protein + carbohydrates + vegetables."),
            ("Day 3", "30 min cycling/jogging + stretching", "Balanced nutritious meals and water."),
            ("Day 4", "Full-body bodyweight workout for 30 min", "Protein-rich foods and vegetables."),
            ("Day 5", "30 min cardio + core exercises", "Balanced diet and fruits."),
            ("Day 6", "40 min light cardio + stretching", "Healthy balanced meals."),
            ("Day 7", "Rest + light walking + stretching", "Balanced diet and good hydration.")
        ]

        nutrition = "Maintain a balanced diet containing protein, carbohydrates, healthy fats, vegetables and fruits."

    return days, nutrition


@router.post("/generate-plan")
def download_pdf(data: UserInput):

    days, nutrition = create_plan(data)

    workout_text = (
        "7-DAY FITNESS PLAN\n\n"
        + "\n\n".join(
            day + "\n" + workout
            for day, workout, food in days
        )
    )

    return {
        "workout_plan": workout_text,
        "nutrition_tip": nutrition
    }


@router.post("/download-pdf")
def download_pdf(data: UserInput):

    days, nutrition = create_plan(data)

    pdf_buffer = BytesIO()

    pdf = canvas.Canvas(pdf_buffer, pagesize=A4)

    width, height = A4

    # Background
    pdf.setFillColorRGB(0.04, 0.07, 0.06)
    pdf.rect(0, 0, width, height, fill=1, stroke=0)

    # Main title
    pdf.setFillColorRGB(0.1, 1, 0.5)
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(
        width / 2,
        height - 55,
        "FITBUDDY AI"
    )

    pdf.setFillColorRGB(0.8, 0.8, 0.8)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawCentredString(
        width / 2,
        height - 80,
        "7-DAY FITNESS PLAN"
    )

    # User details box
    y = height - 120

    pdf.setFillColorRGB(0.1, 0.13, 0.12)
    pdf.roundRect(
        40,
        y - 45,
        width - 80,
        45,
        8,
        fill=1,
        stroke=0
    )

    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont("Helvetica-Bold", 10)

    pdf.drawString(
        55,
        y - 20,
        "Goal: " + data.goal
    )

    pdf.drawString(
        220,
        y - 20,
        "Age: " + str(data.age)
    )

    pdf.drawString(
        330,
        y - 20,
        "Weight: " + str(data.weight) + " kg"
    )

    y -= 75

    # Seven day plans
    for day, workout, food in days:

        if y < 150:
            pdf.showPage()

            pdf.setFillColorRGB(0.04, 0.07, 0.06)
            pdf.rect(0, 0, width, height, fill=1, stroke=0)

            y = height - 55

        # Day heading
        pdf.setFillColorRGB(0.1, 1, 0.5)
        pdf.setFont("Helvetica-Bold", 15)
        pdf.drawString(
            50,
            y,
            day
        )

        y -= 22

        # Workout
        pdf.setFillColorRGB(0.2, 0.8, 1)
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(
            60,
            y,
            "WORKOUT"
        )

        y -= 16

        pdf.setFillColorRGB(1, 1, 1)
        pdf.setFont("Helvetica", 9)

        # Split long workout text
        words = workout.split()
        line = ""

        for word in words:

            if len(line + " " + word) > 75:
                pdf.drawString(70, y, line)
                y -= 13
                line = word
            else:
                if line:
                    line += " " + word
                else:
                    line = word

        if line:
            pdf.drawString(70, y, line)
            y -= 18

        # Nutrition
        pdf.setFillColorRGB(1, 0.8, 0.2)
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(
            60,
            y,
            "NUTRITION"
        )

        y -= 16

        pdf.setFillColorRGB(1, 1, 1)
        pdf.setFont("Helvetica", 9)

        words = food.split()
        line = ""

        for word in words:

            if len(line + " " + word) > 75:
                pdf.drawString(70, y, line)
                y -= 13
                line = word
            else:
                if line:
                    line += " " + word
                else:
                    line = word

        if line:
            pdf.drawString(70, y, line)
            y -= 25

        # Divider
        pdf.setStrokeColorRGB(0.2, 0.3, 0.25)
        pdf.line(50, y + 8, width - 50, y + 8)

    # General nutrition
    if y < 120:
        pdf.showPage()

        pdf.setFillColorRGB(0.04, 0.07, 0.06)
        pdf.rect(0, 0, width, height, fill=1, stroke=0)

        y = height - 55

    pdf.setFillColorRGB(0.1, 1, 0.5)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(
        50,
        y,
        "GENERAL NUTRITION"
    )

    y -= 25

    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont("Helvetica", 9)

    words = nutrition.split()
    line = ""

    for word in words:

        if len(line + " " + word) > 80:

            pdf.drawString(60, y, line)
            y -= 14

            if y < 60:
                pdf.showPage()

                pdf.setFillColorRGB(0.04, 0.07, 0.06)
                pdf.rect(0, 0, width, height, fill=1, stroke=0)

                y = height - 55

            line = word

        else:

            if line:
                line += " " + word
            else:
                line = word

    if line:
        pdf.drawString(60, y, line)

    # Footer
    pdf.setFillColorRGB(0.5, 0.5, 0.5)
    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(
        width / 2,
        25,
        "FitBuddy AI • Personal Fitness Planner"
    )

    pdf.save()

    pdf_buffer.seek(0)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            'attachment; filename="FitBuddy_AI_7_Day_Plan.pdf"'
        }
    )