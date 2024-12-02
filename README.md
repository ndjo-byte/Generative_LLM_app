# LLM FastAPI App

### Welcome to the LLM FastAPI App! This app is a machine learning (ML) and DevOps project that leverages APIs and Docker to provide users with personalized SMART goal plans. It integrates a HuggingFace endpoint with LangChain to generate goal-setting plans based on user inputs. Additionally, the app is packaged using Docker for easy deployment. The app was created with an AWS MySQL database, but that datbase has since been deactivated. Future users and developers will need to create their own database, then update the database.py and .env accordingly.

This README will guide you through the app's functionality, setup, and how to run it using Docker.

## Table of Contents

- Overview
- Features
- Technology Stack
- Getting Started
- Environment Setup
- Running with Docker
- Endpoints
- Error Handling
- Contributing
- License

## Overview

The LLM FastAPI App is a web application designed to help users create SMART goals. It uses HuggingFace's LLM model to generate goal-setting plans based on user inputs. The app is built with FastAPI, which provides fast and modern web APIs, and utilizes a Pydantic model to validate inputs. The data is stored in a database, and Jinja2 templates are used to render HTML responses.

The app is fully Dockerized, enabling easy deployment and scalability. You can pull the image from Docker Hub using:

_docker pull ndjobyte/llmfastapi-app:v1_

## Features

Goal Setting: The app helps users generate detailed, actionable SMART goals.
ML-powered: Uses LangChain with HuggingFace’s Phi-3.5-mini-instruct model to generate personalized goal plans.
User-Friendly Interface: Provides a simple web interface to input goal details and generate a plan.
Database Integration: Stores generated goals in a database for later retrieval.
Dockerized: The app is packaged with Docker, making deployment easy and consistent.


## Technology Stack

FastAPI: High-performance web framework for building APIs.
LangChain: Framework for building language models, here used to integrate with HuggingFace’s API.
HuggingFace API: Provides access to powerful pre-trained models.
Pydantic: Data validation library used with FastAPI.
Jinja2: Template engine for rendering HTML.
Docker: Used to containerize the application for deployment.
MySQL: Database used to store user goal data.

## Getting Started

Environment Setup
Before running the app, ensure you have the necessary environment variables set up. You’ll need a HuggingFace API key to access the LLM model.

Clone this repository or download the source files.

Create a .env file in the root directory and add the following:

HF_API_KEY=your_huggingface_api_key

DATABASE_URL=your_database_url

Install the required dependencies:

_pip install -r requirements.txt_

Ensure your database is set up correctly. The app uses MySQL for storing goal data.

### Running with Docker

The app is Dockerized for easy deployment. To run the app using Docker, follow these steps:

Pull the Docker image from Docker Hub:

_docker pull ndjobyte/llmfastapi-app:v1_

Run the app using Docker:
(Having firstcreated a .env in the same directory with your API_KEY and DATABASE_URL)

_docker run --env-file .env -p 8000:80 ndjobyte/llmfastapi-app:v1_

This command runs the container in the background and maps port 8000 on your machine to port 80 in the container.
Visit the app in your browser at http://localhost:8000.

## Endpoints

Home (/)
Method: GET
Description: Returns the landing page of the app.
Response: Renders an HTML page with the input form for goal details.
Generate Goal Plan (/generate-plan/)

Method: POST
Description: Accepts the user's goal name, description, and deadline, and generates a SMART goal plan.
Form Parameters:
name: Name of the goal.
description: Description of the goal.
deadline: Deadline for the goal in the format yyyy-mm-dd.
Response: Renders the generated goal plan along with the primary ID of the goal.
Retrieve Goal (/get-goal/{goal_id})

Method: GET
Description: Retrieves a stored goal by its ID.
Path Parameter:
goal_id: The ID of the goal to retrieve.
Response: Renders the goal details including its name, description, and deadline.

## Error Handling

If any errors occur, they will be handled by FastAPI's built-in error handling. Common errors include:

Validation Errors: If the input does not meet the required criteria, a 422 Unprocessable Entity error is returned.
Internal Server Errors: Any issues with processing the request or generating the goal plan will return a 500 Internal Server Error with an appropriate error message.
Contributing

## I welcome contributions to this project! To contribute:

Fork the repository.
Create a new branch (git checkout -b feature-branch).
Make your changes and commit them (git commit -am 'Add feature').
Push to the branch (git push origin feature-branch).
Create a pull request.

## License

This project is licensed under the MIT License.

Feel free to reach out with any questions or suggestions. Happy coding! 🚀