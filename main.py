from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from llms.CV_Generate import Job_Descriptions_Gen_CoT
from llms.CV_Scan import Job_Scan_CoT
from concurrent.futures import ThreadPoolExecutor

from backend.model import save_job_to_db, save_scan_result_to_db
import logging
import asyncio
app = FastAPI()

class JobDescriptionRequest(BaseModel):
    job_title: str
    organization: str
    organization_description: str
    salary: str
    position: str
    responsibilities : str
    experience: str
    work_hours : str
    skills: str
    output_language: str

executor = ThreadPoolExecutor(max_workers=5)
# Remove the CVScanRequest class as we'll handle multipart form data directly

@app.post("/gen_job_desc/")
async def generate_job_description(request: JobDescriptionRequest) -> dict:
    job_gen = Job_Descriptions_Gen_CoT()
    
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(executor, job_gen, 
                                            request.job_title, 
                                            request.salary, 
                                            request.position, 
                                            request.skills, 
                                            request.output_language, 
                                            request.organization, 
                                            request.work_hours, 
                                            request.responsibilities, 
                                            request.organization_description, 
                                            request.experience)

        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to generate job description")
            
        # Access attributes directly from the result object
        job_description = getattr(result, 'job_description', '')
        save_success = await save_job_to_db(job_title=request.job_title, job_description=job_description)
        
        if not save_success:
            raise HTTPException(status_code=500, detail="Failed to save job to database")
            
        return {
            "job_title": getattr(result, 'title_result', ''),
            "organization_description": getattr(result, 'organization_description_result', ''),
            "job_description": job_description,
            "responsibilities": getattr(result, 'responsibilities_result', ''),
            "experience": getattr(result, 'experience_result', ''),
            "skills": getattr(result, 'skills_result', ''),
            "salary": getattr(result, 'salary_result', ''),
            "work_hours": getattr(result, 'work_hours_result', '')
        }
    except Exception as e:
        logging.error(f"Error generating job description: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scan_cv/")
async def scan_cv(
    resumes: UploadFile = File(...),
    job_descriptions: str = Form(...)
):
    cv_scan = Job_Scan_CoT()
    try:
        file_content = await resumes.read()
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(executor, cv_scan, file_content, job_descriptions)
        score = result.score
        reason = result.reason
        name = result.name
        email = result.email
        phone = result.phone
        await save_scan_result_to_db(name=name, score=score, reason=reason, email=email, phone=phone)
        return {
            "name": name,
            "score": score,
            "reason": reason,
            "email": email,
            "phone": phone
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/", response_class=HTMLResponse)
async def root():
    with open("index.html", "r") as file:
        return HTMLResponse(content=file.read(), status_code=200)

if __name__ == "__main__":
    import uvicorn
    import base64
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)