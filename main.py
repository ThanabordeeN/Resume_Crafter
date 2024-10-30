from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from llms.CV_Generate import Job_Descriptions_Gen_CoT
from llms.CV_Scan import Job_Scan_CoT
from backend.model import save_job_to_db, save_scan_result_to_db
import base64
app = FastAPI()

class JobDescriptionRequest(BaseModel):
    job_title: str
    organization: str
    organization_description: str
    salary: str
    position: str
    experience: str
    skills: str
    output_language: str

# Remove the CVScanRequest class as we'll handle multipart form data directly

@app.post("/gen_job_desc/")
async def generate_job_description(request: JobDescriptionRequest):
    job_gen = Job_Descriptions_Gen_CoT()
    
    try:
        result = await job_gen.arun(
            job_title=request.job_title,
            salary=request.salary,
            position=request.position,
            skills=request.skills,
            output_language=request.output_language,
            organization=request.organization,
            organization_description=request.organization_description,
            experience=request.experience
        )
        save_success = await save_job_to_db(job_title=request.job_title, job_description=result.job_description)
        if not save_success:
            raise HTTPException(status_code=500, detail="Failed to save job to database")
        return {"Job_Title": request.job_title, "Job_Description": result.job_description}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scan_cv/")
async def scan_cv(
    resumes: UploadFile = File(...),
    job_descriptions: str = Form(...)
):
    cv_scan = Job_Scan_CoT()
    try:
        file_content = await resumes.read()
        result = await cv_scan.arun(file_content, job_descriptions)
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
    uvicorn.run(app, host="0.0.0.0", port=8000)