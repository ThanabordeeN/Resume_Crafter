# RESUME_WORKS

## Description
This project is a backend application that utilizes FastAPI and Uvicorn to provide a web server. It includes functionalities for generating and scanning CVs using machine learning models.

## Project Structure
backend/ model.py 

llms/ CV_Generate.py CV_Scan.py 

main.py 

requirements.txt


## Requirements
The project dependencies are listed in the `requirements.txt` file. The main dependencies are:
- FastAPI
- Uvicorn
- dspy

## Installation
1. Clone the repository:
    git clone <repository-url>
2. Navigate to the project directory:
    cd <project-directory>
3. Install the dependencies:
    pip install -r requirements.txt

## Usage
1. Run the FastAPI server:
    uvicorn main:app --reload

2. Access the API documentation at `http://127.0.0.1:8000/docs`.

## Files
- `backend/model.py`: Contains the data models used in the application.
- `llms/CV_Generate.py`: Script for generating CVs using machine learning models.
- `llms/CV_Scan.py`: Script for scanning and analyzing CVs using machine learning models.
- `main.py`: The entry point of the FastAPI application.
- `requirements.txt`: Lists the dependencies required for the project.

## License
This project is licensed under the MIT License.