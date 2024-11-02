import os
import dspy
import asyncio
import logging  
import litellm
litellm.success_callback = ["langfuse"]
litellm.failure_callback = ["langfuse"] # logs errors to langfuse
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-46f0ade7-4859-40b8-828f-896b0d3acafc"
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-699a3072-af03-403f-a047-47c073da0251"
lm = dspy.LM('gpt-4o-mini', api_key=os.environ["OPENAI_API_KEY"], max_tokens=None)
dspy.configure(lm=lm)

class Job_Descriptions_Gen(dspy.Signature):
    """Generate Professional job Recruitements based on job title, salary, position, and skills."""
    job_title = dspy.InputField()
    organization = dspy.InputField()
    organization_description = dspy.InputField()
    salary = dspy.InputField()
    position = dspy.InputField()
    experience = dspy.InputField()
    responsibilities = dspy.InputField()
    work_hours = dspy.InputField()
    skills = dspy.InputField()
    output_language = dspy.InputField()
    
    title_result= dspy.OutputField(desc="Generated Job Title")
    organization_description_result= dspy.OutputField(desc="Generated Long Organization Description")
    job_description= dspy.OutputField(desc="Generated Job Description")
    responsibilities_result= dspy.OutputField(desc="Generated Responsibilities")
    experience_result= dspy.OutputField(desc="Generated Experience")
    skills_result= dspy.OutputField(desc="Generated Skills")
    salary_result= dspy.OutputField(desc="Generated Salary")
    work_hours_result= dspy.OutputField(desc="Generated Work Hours")
    
    
    


class Job_Descriptions_Gen_CoT(dspy.Module):
    def __init__(self):
        super().__init__()
        self.progress = dspy.ChainOfThought(Job_Descriptions_Gen)
        
    def forward(self, job_title, salary, position, skills, work_hours, responsibilities, output_language, organization, organization_description, experience):
        try:
            result = self.progress(
                job_title=job_title,
                salary=salary,
                position=position,
                skills=skills,
                work_hours=work_hours,
                responsibilities=responsibilities,
                output_language=output_language,
                organization=organization,
                organization_description=organization_description,
                experience=experience
            )
            return result
        except Exception as e:
            logging.error(f"Error in job description generation: {str(e)}")
            raise
    
