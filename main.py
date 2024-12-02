from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate
from fastapi import FastAPI, HTTPException, Depends, Request, Form
from pydantic import BaseModel, model_validator, Field
from dotenv import load_dotenv
import os
from database import insert_goal, close_connection, db
from datetime import datetime, date 

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse



#app design template
templates = Jinja2Templates(directory="templates")



# Load environment variables from the .env file
load_dotenv()  



# Access the API key using os.getenv()

api_key = os.getenv("HF_API_KEY")
if not api_key:
    raise ValueError("HF_API_KEY environment variable is not set")



# Define the lifespan for the FastAPI application

async def lifespan(app: FastAPI):
    
    print("App is starting...")
    
    # Yield to allow FastAPI to run the application
    yield
    
    
    print("App is shutting down...")
    close_connection()  # Close db connection when app closes



# Initialize FastAPI with the lifespan context

app = FastAPI(lifespan=lifespan)



# basemodel pydantic

class PredInput(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, example="My Goal")
    description: str = Field(..., min_length=10, max_length=500, example="A detailed description of the goal.")
    deadline: str = Field(..., 
        pattern=r"^\d{4}-\d{2}-\d{2}$",  # Enforce yyyy-mm-dd format for mysql input 
        example="e.g. yyyy-mm-dd -> 2024-12-31"
    )



#current date

def get_today():
    return date.today().strftime("%d/%m/%Y")



#configuring langchain with huggingface llm

llm = HuggingFaceEndpoint(
    repo_id="microsoft/Phi-3.5-mini-instruct",  
    model_kwargs={"max_length": 500},  # Tokens limit output
    huggingfacehub_api_token=api_key          
)



# langchain template with variables

template = """
You are an expert goal-setting coach. Help create a detailed and actionable SMART goal plan based on the following details:
- Goal name: {name}
- Goal description: {description}
- Deadline: {deadline}
- Current date: {today}

Ensure the goal is:
1. **Specific**: Clearly define what you want to achieve.
2. **Measurable**: Include measurable criteria to track progress.
3. **Achievable**: Make sure the goal is realistic and attainable.
4. **Relevant**: Ensure it aligns with the user's broader values or objectives.
5. **Time-bound**: Provide a specific timeline and milestones.

**Important**:
- Do not include any milestones or deadlines before {today}.
- Evenly distribute milestones over the timeline between {today} and {deadline}.
- Make sure the final milestone aligns with {deadline}.

Provide a step-by-step action plan with milestones, resources, and checkpoints for success.
"""



# langchain PromptTemplate

project_prompt = PromptTemplate(
    input_variables=["name", "description", "deadline", "today"],
    template=template
)



#fast api endpoint / functions: home 

""" @app.get("/")
async def root():
    return {"message": "Welcome to the AI Goal Setting App"} """

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



@app.post('/generate-plan/', response_class=HTMLResponse)
async def generate_plan(request: Request, name: str = Form(...), description: str = Form(...), deadline: str = Form(...), today: str = Depends(get_today)):
    try:
        prompt = PredInput(name=name, description=description, deadline=deadline)
        user_input_variables = project_prompt.format(name=prompt.name, description=prompt.description, deadline=prompt.deadline, today=today)
        goal_plan = llm.invoke(user_input_variables)
        primary_id = insert_goal(prompt.name, prompt.description, prompt.deadline, goal_plan)

        # Return the generated plan and id on the same page
        return templates.TemplateResponse("index.html", {"request": request, "primary_id": primary_id, "goal_plan": goal_plan, "name": prompt.name})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in generating plan: {str(e)}")



@app.get("/get-goal/{goal_id}", response_class=HTMLResponse)
async def get_goal(request: Request, goal_id: int):
    try:
        query = "SELECT * FROM goals WHERE id = %s"
        with db.cursor() as cursor:
            cursor.execute(query, (goal_id,))
            goal = cursor.fetchone()

        if not goal:
            return templates.TemplateResponse("index.html", {"request": request, "error": f"Goal with ID {goal_id} not found."})

        # Convert dates to strings for rendering
        goal['deadline'] = str(goal['deadline'])
        goal['created_at'] = str(goal['created_at'])

        return templates.TemplateResponse("index.html", {"request": request, "goal": goal})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving goal: {str(e)}")


