
# Service Documentation

This document provides an overview and usage instructions for the service that generates job descriptions and scans resumes to match them against job descriptions.

## Table of Contents

- Overview
- Installation
- API Endpoints
  - Generate Job Description
  - Scan CV
- Folder Structure
- Usage

## Overview

The service is built using FastAPI and leverages language models through the `dspy` library. It provides two main functionalities:

1. **Generate Job Description**: Creates professional job descriptions based on input parameters.
2. **Scan CV**: Analyzes resumes against job descriptions to provide a match score and extracts candidate information.

## Installation

1. Clone the repository.
2. Navigate to the project directory.
3. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

4. Set environment variables:

   - `OPENAI_API_KEY`: Your OpenAI API key.
   - `MODEL` (optional): The language model to use (default is `"openai/gpt-4o-mini"`).

## API Endpoints

### Generate Job Description

- **Endpoint**: `/gen_job_desc/`
- **Method**: `POST`
- **Description**: Generates a professional job description based on provided details.

**Request Body**:

```json
{
  "job_title": "Software Engineer",
  "organization": "Tech Corp",
  "organization_description": "A leading tech company specializing in AI solutions.",
  "salary": "Competitive",
  "position": "Full-Time",
  "experience": "3+ years",
  "skills": "Python, Machine Learning, REST APIs",
  "output_language": "English"
}
```

**Response**:

```json
{
  "Job_Title": "Software Engineer",
  "Job_Description": "Generated job description with clear markdown structure..."
}
```

**Implementation**: Defined in 

main.py


```python
@app.post("/gen_job_desc/")
async def generate_job_description(request: JobDescriptionRequest):
    job_gen = Job_Descriptions_Gen_CoT()
    try:
        result = job_gen.run(
            job_title=request.job_title,
            salary=request.salary,
            position=request.position,
            skills=request.skills,
            output_language=request.output_language,
            organization=request.organization,
            organization_description=request.organization_description,
            experience=request.experience
        )
        save_job_to_db(job_title=request.job_title, job_description=result.job_description)
        return {"Job_Title": request.job_title, "Job_Description": result.job_description}, 200
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Scan CV

- **Endpoint**: `/scan_cv/`
- **Method**: `POST`
- **Description**: Scans a resume and a job description to provide a match score and candidate details.

**Request Body**:

```json
{
  "resumes": "base64-encoded PDF content",
  "job_descriptions": "Job description text"
}
```

**Response**:

```json
{
  "name": "Candidate Name",
  "score": "Match score between 1-100",
  "reason": "Explanation for the score",
  "email": "candidate@example.com",
  "phone": "Contact number"
}
```

**Implementation**: Defined in 

main.py



```python
@app.post("/scan_cv/")
async def scan_cv(request: CVScanRequest):
    cv_scan = Job_Scan_CoT()
    try:
        result = cv_scan.run(resumes=request.resumes, job_descriptions=request.job_descriptions)
        save_scan_result_to_db(
            name=result.name,
            score=result.score,
            reason=result.reason,
            email=result.email,
            phone=result.phone
        )
        return {
            "name": result.name,
            "score": result.score,
            "reason": result.reason,
            "email": result.email,
            "phone": result.phone
        }, 200
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Folder Structure

```
backend/
  └── model.py
docker-compose.yml
Dockerfile
llms/
  ├── CV_Generate.py
  └── CV_Scan.py
main.py
README.md
requirements.txt
```

- **main.py**: Main entry point of the API service.
- **CV_Generate.py**: Contains the `Job_Descriptions_Gen_CoT` class for generating job descriptions.
- **CV_Scan.py**: Contains the `Job_Scan_CoT` class for scanning resumes.
- **model.py**: Handles database interactions.

## Usage

Run the service using Uvicorn:

```sh
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Example Request for Generating Job Description

```sh
curl -X POST "http://localhost:8000/gen_job_desc/" \
-H "Content-Type: application/json" \
-d '{
  "job_title": "Data Analyst",
  "organization": "Data Inc.",
  "organization_description": "We specialize in data analytics solutions.",
  "salary": "$70,000 - $90,000",
  "position": "Full-Time",
  "experience": "2+ years",
  "skills": "SQL, Python, Data Visualization",
  "output_language": "English"
}'
```

### Example Request for Scanning CV

```sh
curl -X POST "http://localhost:8000/scan_cv/" \
-H "Content-Type: application/json" \
-d '{
  "resumes": "base64-encoded PDF content",
  "job_descriptions": "Job description text"
}'
```

## Dependencies

- `fastapi`
- `pydantic`
- `dspy`
- `fitz`
- `pytesseract` and `Pillow` for OCR functionality

## Environment Variables

- `OPENAI_API_KEY`: API key for OpenAI language models.
- `MODEL`: (Optional) Specify a language model (default is `"openai/gpt-4o-mini"`).

