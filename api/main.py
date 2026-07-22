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
    run_forecasting,
    run_helmet_detection
)

from telegram import Update, Bot
from telegram.ext import (
    Application, 
    CommandHandler, 
    ContextTypes, 
    MessageHandler, 
    filters,
)
from contextlib import asynccontextmanager

UPLOADS = 'uploads'
TELEGRAM_BOT_ID = '8628544333:AAHPSjVrwHjxZHB77R7J84GRAKST1NySDgA'
WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'https://munich-header-gentle-lesser.trycloudflare.com/webhook')

ptb = (
    Application.builder()
        .updater(None)
        .token(TELEGRAM_BOT_ID)
        .read_timeout(7)
        .get_updates_read_timeout(42)
        .build()
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ptb.bot.set_webhook(url=WEBHOOK_URL)
    async with ptb:
        await ptb.start()
        yield
    await ptb.stop()

import asyncio

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Halo, testing')

async def image_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_size = update.message.photo[-1]
    file_id = photo_size.file_id
    new_file = await context.bot.get_file(file_id)

    file_extention = os.path.splitext(new_file.file_path)[1] or '.jpg'
    unique_name = f'{uuid.uuid4().hex}{file_extention}'
    file_location = os.path.join(UPLOADS, unique_name)

    await new_file.download_to_drive(file_location)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text='Image downloaded successfully'
    )

async def bot_research(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text('Silakan berikan topik riset. Contoh: /research AI in 2024')
        return

    topic = ' '.join(context.args)
    
    # 1. Kirim pesan awal (Thinking status)
    status_message = await update.message.reply_text(f'🔍 Sedang meneliti tentang: {topic}...\n(Mohon tunggu, AI sedang berpikir)')

    # 2. Kirim action "typing" agar muncul status "typing..." di Telegram user
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # 3. Jalankan task Celery
    task = run_tax_research.delay('Indonesia', '2024')

    # 4. Polling hasil
    try:
        count = 0
        while not task.ready():
            # Kirim status typing hanya setiap 5 detik agar tidak terkena Flood Control
            if count % 5 == 0:
                try:
                    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
                except:
                    pass 
            
            await asyncio.sleep(1)
            count += 1

            # Timeout setelah 5 menit (300 detik)
            if count > 300:
                await status_message.edit_text(f'⚠️ Riset untuk "{topic}" memakan waktu terlalu lama. Silakan coba lagi nanti atau cek manual.')
                return
        
        print(f"DEBUG: Task {task.id} is ready after {count} seconds.")
        result = task.get()
        print(f"DEBUG: Successfully retrieved result for {task.id}. Sending new message to Telegram...")
        
        # Hapus pesan status "Thinking..."
        try:
            await status_message.delete()
        except:
            pass

        # Jika hasil terlalu panjang, potong sesuai limit Telegram
        if len(result) > 4000:
            result = result[:4000] + "..."
            
        # Kirim pesan BARU (bukan edit) agar status typing lebih cepat hilang
        await update.message.reply_text(f'✅ **Hasil Riset: {topic}**\n\n{result}', parse_mode='Markdown')
        print(f"DEBUG: New message sent for {task.id}. Handler finished.")
        
    except Exception as e:
        await status_message.edit_text(f'❌ Terjadi kesalahan: {str(e)}')

ptb.add_handler(CommandHandler('start', start_command))
ptb.add_handler(MessageHandler(filters.PHOTO, image_handle))
ptb.add_handler(CommandHandler('research', bot_research))

app = FastAPI(lifespan=lifespan)

os.makedirs(UPLOADS, exist_ok=True)

@app.post('/webhook')
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    req_json = await request.json()
    update = Update.de_json(req_json, ptb.bot)
    
    # Jalankan proses update di background agar bisa langsung kirim respons 200 OK ke Telegram
    # Ini mencegah Telegram melakukan retry (mengirim ulang pesan) karena timeout
    background_tasks.add_task(ptb.process_update, update)

    return Response(status_code=HTTPStatus.OK)

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

@app.post('/helmet-detection')
async def helmet_detection(image: UploadFile = File(...)):
    if image.content_type != 'image/jpeg' and image.content_type != 'image/png':
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Image must be a jpeg or png'
        )

    file_extention = os.path.splitext(image.filename)[1] or '.jpg'
    unique_name = f'{uuid.uuid4().hex}{file_extention}'
    file_location = os.path.join(UPLOADS, unique_name)

    content = await image.read()
    with open(file_location, 'wb') as buffer:
        buffer.write(content)

    task = run_helmet_detection.delay(file_location)
    
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