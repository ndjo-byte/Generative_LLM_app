from huggingface_hub import InferenceClient
from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel


from dotenv import load_dotenv
import os


#load .env
load_dotenv('.env')


# Access the API key
api_key = os.getenv("HF_API_KEY")
client = InferenceClient(api_key=api_key)


#instantiate FastApi app
app = FastAPI()


# basemodel pydantic
class PredInput(BaseModel):
      name : str #name of project
      description : str #describe project 
      methodology : str = 'Agile' #e.g. Agile, Scrum, Waterfall
      objectives : str = '' #e.g. specific business goal


#fast api endpoint / functions: home 
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


#fast api endpoint / functions: chat 
@app.post('/generate-response/')
async def generate_response(prompt:PredInput):

	messages = [
			{
				"role": "user",
				"content": f"""
							Create a detailed project plan for a {prompt.methodology} project. 
							Name: {prompt.name}
							Description: {prompt.description}
							Objectives: {prompt.objectives}
							"""
			}
		]

	try: 
		completion = client.chat.completions.create(
			model="microsoft/Phi-3.5-mini-instruct", 
			messages=messages, 
			max_tokens=500
		)
		return completion.choices[0].message.content

	except Exception as e:
		raise HTTPException(status_code=500, detail=(f'Error in generating model: {str(e)}')) 