from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker ,declarative_base
import os
from pydantic import BaseModel , field_validator
import base64

Base = declarative_base()
class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_title = Column(String, nullable=False)
    job_description = Column(String, nullable=False)
    def __repr__(self):
            return f"<Job(id={self.id}, job_title='{self.job_title}', job_description='{self.job_description}')>"

class ScanResult(Base):
    __tablename__ = 'scan_results'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    def __repr__(self):
        return f"<ScanResult(id={self.id}, name='{self.name}', score={self.score}, reason='{self.reason}', email='{self.email}', phone='{self.phone}')>"

class JobDescriptionRequest(BaseModel):
    job_title: str
    salary: str
    position: str
    skills: str
    output_language: str
    organization: str
    organization_description: str
    experience: str

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


# Database setup
db_path = os.path.join(os.path.dirname(__file__), 'jobs.db')
DATABASE_URL = f"sqlite:///{db_path}"  # Change this to your database URL
if not os.path.exists(db_path):
    open(db_path, 'w').close()
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def save_job_to_db(job_title, job_description):
    new_job = Job(job_title=job_title, job_description=job_description)
    session.add(new_job)
    session.commit()
    
def save_scan_result_to_db(name, score, reason, email, phone):
    new_scan_result = ScanResult(name=name, score=score, reason=reason, email=email, phone=phone)
    session.add(new_scan_result)
    session.commit()
    
def get_all_jobs():
    return session.query(Job).all()
def get_all_scan_results():
    return session.query(ScanResult).all()

def get_job_by_id(job_id):
    
    return session.query(Job).filter(Job.id == job_id).first()

def get_scan_result_by_id(scan_result_id):
    return session.query(ScanResult).filter(ScanResult.id == scan_result_id).first()

# Example usage
# save_job_to_db("Software Engineer", "Develop and maintain software applications.")
save_scan_result_to_db("John Doe", 90, "Good match","orawia@gmai.com", "1234567890")