from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llms.CV_Generate import Job_Descriptions_Gen_CoT
from llms.CV_Scan import Job_Scan_CoT
from backend.model import save_job_to_db, save_scan_result_to_db

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

class CVScanRequest(BaseModel):
    resumes: str
    job_descriptions: str

    @field_validator('resumes')
    def validate_base64(cls, v):
        try:
            base64.b64decode(v)
            return v
        except Exception:
            raise ValueError('resumes must be a valid base64 encoded string')

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
        result = {"Job_Title": request.job_title, "Job_Description": result.job_description}
        return  result, 200
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scan_cv/")
async def scan_cv(request: CVScanRequest):
    cv_scan = Job_Scan_CoT()
    try:
        result = cv_scan.run(resumes=request.resumes, job_descriptions=request.job_descriptions)
        score = result.score
        reason = result.reason
        name = result.name
        email = result.email
        phone = result.phone
        save_scan_result_to_db(name=name, score=score, reason=reason, email=email, phone=phone)
        result = {
            "name": name,
            "score": score,
            "reason": reason,
            "email": email,
            "phone": phone
            }
        
        
        return result , 200
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    from pydantic import field_validator
    import base64
    uvicorn.run(app, host="0.0.0.0", port=8000)