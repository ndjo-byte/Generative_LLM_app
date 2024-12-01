from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate
from fastapi import FastAPI, HTTPException, Depends, Request, Form
from pydantic import BaseModel, model_validator, Field
from dotenv import load_dotenv
import os
from database import insert_goal, close_connection, db
from datetime import datetime, date 
from fastapi.templating import Jinja2Templates



#app design template
#templates = Jinja2Templates(directory="templates")



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

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Goal Setting App"}




#fast api endpoint / functions: chat 

@app.post('/generate-plan/')
async def generate_plan(prompt:PredInput, today: str = Depends(get_today)):
	
	try: 

		user_input_variables = project_prompt.format( 
			#langchain method for user to input variables
			name= prompt.name,
			description = prompt.description,
			deadline = prompt.deadline,
            today = today
			)
		
		#use model 
		goal_plan = llm.invoke(user_input_variables)

            
		#insert into db
		primary_id = insert_goal(prompt.name, prompt.description, prompt.deadline, goal_plan)

		return {"primary_id": primary_id, "project_name": prompt.name, "goal_plan": goal_plan} #dictionary for json format

	except Exception as e:

		raise HTTPException(status_code=500, detail=(f'Error in generating model: {str(e)}')) 



#retrieve a specific plan using id 

@app.get("/get-goal/{goal_id}")
async def get_goal(goal_id: int):
    try:
        query = f"SELECT * FROM goals WHERE id = %s"
        with db.cursor() as cursor:  # Here the cursor is used to interact with the DB
            cursor.execute(query, (goal_id,))
            goal = cursor.fetchone()

        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")

        return goal  # Return the goal data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving goal: {str(e)}")



#retrieve all goals 

@app.get("/get-all-goals")
async def get_all_goals():
    try:
        query = "SELECT * FROM goals"
        with db.cursor() as cursor:
            cursor.execute(query)
            goals = cursor.fetchall()

        return {"goals": goals}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving goals: {str(e)}")