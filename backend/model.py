# Standard Library Imports
import os
import base64
import json

# Third-Party Imports
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel, field_validator
import redis

# Configuration
DB_FILENAME = 'jobs.db'
REDIS_HOST = 'redis'  # Assuming the Redis container is named 'redis' in the Docker network
REDIS_PORT = 6379
REDIS_DB = 0

# SQLAlchemy Base
Base = declarative_base()

# Models
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

# Pydantic Models
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

# Redis Setup
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# Database Setup
db_path = os.path.join(os.path.dirname(__file__), DB_FILENAME)
DATABASE_URL = f"sqlite:///{db_path}"
if not os.path.exists(db_path):
    open(db_path, 'w').close()
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Database Functions
def save_job_to_db(job_title, job_description):
    new_job = Job(job_title=job_title, job_description=job_description)
    session.add(new_job)
    session.commit()

def save_scan_result_to_db(name, score, reason, email, phone):
    new_scan_result = ScanResult(name=name, score=score, reason=reason, email=email, phone=phone)
    session.add(new_scan_result)
    session.commit()

def get_all_jobs():
    try:
        cached_jobs = redis_client.get("jobs")
        if cached_jobs:
            print("use cache")
            return [Job(**job) for job in json.loads(cached_jobs)]
    except Exception as e:
        print(f"Redis error: {e}")
    
    jobs = session.query(Job).all()
    if jobs:
        try:
            print("store cache")
            jobs_dict = [{column.name: getattr(job, column.name) for column in job.__table__.columns} for job in jobs]
            redis_client.set("jobs", json.dumps(jobs_dict))
        except Exception as e:
            print(f"Redis error: {e}")
    return jobs

def get_all_scan_results():
    try:
        cached_scan_results = redis_client.get("scan_results")
        if cached_scan_results:
            print("use cache")
            return [ScanResult(**scan_result) for scan_result in json.loads(cached_scan_results)]
    except Exception as e:
        print(f"Redis error: {e}")
    
    scan_results = session.query(ScanResult).all()
    if scan_results:
        try:
            print("store cache")
            scan_results_dict = [{column.name: getattr(scan_result, column.name) for column in scan_result.__table__.columns} for scan_result in scan_results]
            redis_client.set("scan_results", json.dumps(scan_results_dict))
        except Exception as e:
            print(f"Redis error: {e}")
    return scan_results

def get_job_by_id(job_id):
    try:
        cached_job = redis_client.get(f"job:{job_id}")
        if cached_job:
            print("use cache")
            return Job(**json.loads(cached_job))
    except Exception as e:
        print(f"Redis error: {e}")
    
    job = session.query(Job).filter(Job.id == job_id).first()
    if job:
        try:
            print("store cache")
            job_dict = {column.name: getattr(job, column.name) for column in job.__table__.columns}
            redis_client.set(f"job:{job_id}", json.dumps(job_dict))
        except Exception as e:
            print(f"Redis error: {e}")
    return job

def get_scan_result_by_id(scan_result_id):
    try:
        cached_scan_result = redis_client.get(f"scan_result:{scan_result_id}")
        if cached_scan_result:
            print("use cache")
            return ScanResult(**json.loads(cached_scan_result))
    except Exception as e:
        print(f"Redis error: {e}")
    
    scan_result = session.query(ScanResult).filter(ScanResult.id == scan_result_id).first()
    if scan_result:
        try:
            print("store cache")
            scan_result_dict = {column.name: getattr(scan_result, column.name) for column in scan_result.__table__.columns}
            redis_client.set(f"scan_result:{scan_result_id}", json.dumps(scan_result_dict))
        except Exception as e:
            print(f"Redis error: {e}")
    return scan_result

# Example usage
# save_job_to_db("Software Engineer", "Develop and maintain software applications.")
print(get_all_jobs())
print(get_all_scan_results())