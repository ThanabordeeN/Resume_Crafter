# Standard Library Imports
import os
import base64
import json
from datetime import datetime

# Third-Party Imports
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel, field_validator
import redis.asyncio as redis

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

# 
# Redis Setup
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Redis Helper Function
@staticmethod
async def get_redis():
    return redis_client

# Database Setup
db_path = os.path.join(os.path.dirname(__file__), DB_FILENAME)
DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"
async_engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession)

# Database Functions
async def save_job_to_db(job_title: str, job_description: str):
    try:
        key = f"job:{datetime.now().isoformat()}"
        value = json.dumps({
            "job_title": job_title,
            "job_description": job_description
        })
        await redis_client.set(key, value)
        return True
    except Exception as e:
        print(f"Error saving job to db: {e}")
        return False

async def save_scan_result_to_db(name: str, score: float, reason: str, email: str, phone: str):
    try:
        key = f"scan:{datetime.now().isoformat()}"
        value = json.dumps({
            "name": name,
            "score": score,
            "reason": reason,
            "email": email,
            "phone": phone
        })
        await redis_client.set(key, value)
        return True
    except Exception as e:
        print(f"Error saving scan result to db: {e}")
        return False

async def get_all_jobs():
    redis = await get_redis()
    try:
        cached_jobs = await redis.get("jobs")
        if cached_jobs:
            return [Job(**job) for job in json.loads(cached_jobs)]
    except Exception as e:
        print(f"Redis error: {e}")
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Job))
        jobs = result.scalars().all()
        
        if jobs:
            try:
                jobs_dict = [{column.name: getattr(job, column.name) for column in job.__table__.columns} for job in jobs]
                await redis.set("jobs", json.dumps(jobs_dict))
            except Exception as e:
                print(f"Redis error: {e}")
        return jobs

async def get_all_scan_results():
    redis = await get_redis()
    try:
        cached_scan_results = await redis.get("scan_results")
        if cached_scan_results:
            return [ScanResult(**scan_result) for scan_result in json.loads(cached_scan_results)]
    except Exception as e:
        print(f"Redis error: {e}")
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(ScanResult))
        scan_results = result.scalars().all()
        
        if scan_results:
            try:
                scan_results_dict = [{column.name: getattr(scan_result, column.name) for column in scan_result.__table__.columns} for scan_result in scan_results]
                await redis.set("scan_results", json.dumps(scan_results_dict))
            except Exception as e:
                print(f"Redis error: {e}")
        return scan_results

async def get_job_by_id(job_id):
    redis = await get_redis()
    try:
        cached_job = await redis.get(f"job:{job_id}")
        if cached_job:
            return Job(**json.loads(cached_job))
    except Exception as e:
        print(f"Redis error: {e}")
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Job).filter(Job.id == job_id))
        job = result.scalars().first()
        
        if job:
            try:
                job_dict = {column.name: getattr(job, column.name) for column in job.__table__.columns}
                await redis.set(f"job:{job_id}", json.dumps(job_dict))
            except Exception as e:
                print(f"Redis error: {e}")
        return job

async def get_scan_result_by_id(scan_result_id):
    redis = await get_redis()
    try:
        cached_scan_result = await redis.get(f"scan_result:{scan_result_id}")
        if cached_scan_result:
            return ScanResult(**json.loads(cached_scan_result))
    except Exception as e:
        print(f"Redis error: {e}")
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(ScanResult).filter(ScanResult.id == scan_result_id))
        scan_result = result.scalars().first()
        
        if scan_result:
            try:
                scan_result_dict = {column.name: getattr(scan_result, column.name) for column in scan_result.__table__.columns}
                await redis.set(f"scan_result:{scan_result_id}", json.dumps(scan_result_dict))
            except Exception as e:
                print(f"Redis error: {e}")
        return scan_result

# Cleanup
async def cleanup():
    redis = await get_redis()
    redis.close()
    await redis.wait_closed()
