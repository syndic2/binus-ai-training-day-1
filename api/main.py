from fastapi import (
    FastAPI,
    UploadFile,
    File,
    BackgroundTasks,
    HTTPException,
    Response,
    Request,
)
from pydantic import BaseModel
from celery.result import AsyncResult
from typing import Any, Optional

import os
import uuid

from http import HTTPStatus

from tasks.celery_app import celery_app
from tasks.celery_tasks import (
    run_research,
    run_market_research,
    run_tax_research,
    run_tax_advise,
    run_file_text_analyzer,
    run_anomaly_detection,
    run_forecasting
)

app = FastAPI()

UPLOADS = 'uploads'

os.makedirs(UPLOADS, exist_ok=True)

class ResearchInput(BaseModel):
    topic: str
    audience: str

@app.post('/research')
async def research(data: ResearchInput):
    task = run_research.delay(data.topic, data.audience)
    
    return {
        'status': True,
        'message': None,
        'data': {
            'task_id': task.id
        }
    }

class MarketResearchInput(BaseModel):
    topic: str
    current_year: str

@app.post('/market-research')
async def market_research(data: MarketResearchInput):
    task = run_market_research.delay(data.topic, data.current_year)
    
    return {
        'status': True,
        'message': None,
        'data': {
            'task_id': task.id
        }
    }

class TaxResearchInput(BaseModel):
    country: str
    year: str

@app.post('/tax-research')
async def tax_research(data: TaxResearchInput):
    task = run_tax_research.delay(data.country, data.year)
    
    return {
        'status': True,
        'message': None,
        'data': {
            'task_id': task.id
        }
    }

@app.post('/tax-advise')
async def tax_advise(data: TaxResearchInput):
    task = run_tax_advise.delay(data.country, data.year)
    
    return {
        'status': True,
        'message': None,
        'data': {
            'task_id': task.id
        }
    }

@app.post('/file-text-analyzer')
async def file_text_analyzer(file: UploadFile = File(...)):
    if file.content_type != 'text/plain':
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='File must be a text/plain'
        )

    file_extention = os.path.splitext(file.filename)[1] or '.text'
    unique_name = f'{uuid.uuid4().hex}{file_extention}'
    file_location = os.path.join(UPLOADS, unique_name)

    content = await file.read()
    with open(file_location, 'wb') as buffer:
        buffer.write(content)

    task = run_file_text_analyzer.delay(file_location)
    
    return {
        'status': True,
        'message': None,
        'data': {
            'task_id': task.id
        }
    }

@app.post('/anomaly-detection')
async def anomaly_detection(file: UploadFile = File(...)):
    if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='File must be an excel file'
        )

    file_extention = os.path.splitext(file.filename)[1] or '.xlsx'
    unique_name = f'{uuid.uuid4().hex}{file_extention}'
    file_location = os.path.join(UPLOADS, unique_name)

    content = await file.read()
    with open(file_location, 'wb') as buffer:
        buffer.write(content)

    task = run_anomaly_detection.delay(file_location)
    
    return {
        'status': True,
        'message': None,
        'data': {
            'task_id': task.id
        }
    }

@app.post('/forecasting')
async def forecasting(file: UploadFile = File(...)):
    if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='File must be an excel file'
        )

    file_extention = os.path.splitext(file.filename)[1] or '.xlsx'
    unique_name = f'{uuid.uuid4().hex}{file_extention}'
    file_location = os.path.join(UPLOADS, unique_name)

    content = await file.read()
    with open(file_location, 'wb') as buffer:
        buffer.write(content)

    task = run_forecasting.delay(file_location)
    
    return {
        'status': True,
        'message': None,
        'data': {
            'task_id': task.id
        }
    }

class TaskStatus(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None

@app.get('/status/{task_id}', response_model=TaskStatus)
async def get_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)

    response = {
        'task_id': task_id,
        'status': task_result.state,
        'result': None,
        'error': None
    }

    if task_result.state == 'SUCCESS':
        response['result'] = task_result.result
    elif task_result.state == 'FAILURE':
        response['error'] = str(task_result.info)

    return response