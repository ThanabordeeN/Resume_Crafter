import os
import dspy
import asyncio

lm = dspy.LM('openai/gpt-4o-mini', api_key=os.environ["OPENAI_API_KEY"], max_tokens=None)
dspy.configure(lm=lm)


class Job_Descriptions_Gen(dspy.Signature):
    """Generate Professional job Recruitements based on job title, salary, position, and skills."""
    job_title = dspy.InputField()
    organization = dspy.InputField()
    organization_description = dspy.InputField()
    salary = dspy.InputField()
    position = dspy.InputField()
    experience = dspy.InputField()
    skills = dspy.InputField()
    output_language = dspy.InputField()
    job_description = dspy.OutputField(desc="1000 characters of job description , Clear Markdown Structure, and Professional")


class Job_Descriptions_Gen_CoT(dspy.Module):
    def __init__(self):
        super().__init__()
        self.progress = dspy.ChainOfThought(Job_Descriptions_Gen)
        
    def run(self, job_title, salary, position, skills, output_language, organization, organization_description, experience):
        return self.progress(
            job_title=job_title, 
            salary=salary, 
            position=position, 
            skills=skills, 
            output_language=output_language,
            organization=organization,
            organization_description=organization_description,
            experience=experience
        )
    
    async def arun(self, job_title, salary, position, skills, output_language, organization, organization_description, experience):
        # Run synchronous operation in a thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.run,
            job_title,
            salary,
            position,
            skills,
            output_language,
            organization,
            organization_description,
            experience
        )

