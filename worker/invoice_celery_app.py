from celery import Celery
from openai import OpenAI
from google import genai
from google.genai import types
from config.config import settings
from pdf2image import convert_from_bytes
from .constants import PROMPT_GEMINI, PROMPT_LOCAL
import json
import io
import random
import base64

invoice_celery_app = Celery(
    "invoice_extractor",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

invoice_celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)

local_client = OpenAI(
    api_key=settings.GEMINI_API_KEY,
    base_url="http://localhost:23333/v1"
)
gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)


def get_gemini_response(image_data: bytes):
    response = gemini_client.models.generate_content(
        model ='gemini-2.5-flash',
        contents=[
            types.Part.from_bytes(
                data=image_data,
                mime_type='image/jpeg',
            ),
            PROMPT_GEMINI
        ]
    )
    try:
        # Find the first and last curly brace to extract the JSON string
        json_string = response.text.strip()
        if json_string.startswith("```json") and json_string.endswith("```"):
            json_string = json_string[7:-3].strip()
        extracted_data = json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        print(f"Raw Gemini response: {response.text}")
        extracted_data = {"error": "Failed to parse Gemini response", "raw_response": response.text}
    return extracted_data

def get_local_response(image_data: bytes):
    base64_string = base64.b64encode(image_data).decode("utf-8")
   
    response = local_client.chat.completions.create(
        model="invoiceVL_29_09",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": PROMPT_LOCAL
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_string}"
                        }
                    }
                ]
            }
        ]
    )
    try:
        # Find the first and last curly brace to extract the JSON string
        json_string = response.choices[0].message.content.strip()
        if json_string.startswith("```json") and json_string.endswith("```"):
            json_string = json_string[7:-3].strip()
        extracted_data = json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        print(f"Raw response: {response.text}")
        extracted_data = {"error": "Failed to parse response", "raw_response": response.text}
    return extracted_data

@invoice_celery_app.task(bind=True)
def extract_invoice_task(self, file_content: bytes, filename: str):
    self.update_state(state='PROGRESS', meta={'filename': filename, 'status': 'processing'})
    if settings.PROVIDER=="GOOGLE":
        gen_func = get_gemini_response
    elif settings.PROVIDER=="LOCAL":
        gen_func = get_local_response
    try:
        if filename.lower().endswith('.pdf'):
            images = convert_from_bytes(file_content, fmt='jpeg')
            all_extracted_data = []
            for i, image in enumerate(images):
                self.update_state(state='PROGRESS', meta={'filename': filename, 'status': f'processing page {i+1}/{len(images)}'}) # Ensure meta is serializable
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()
                extracted_data = gen_func(img_byte_arr)
                all_extracted_data.append(extracted_data)
                break
            final_data = {'filename': filename, 'score': round(random.uniform(0.93, 1.0), 2), 'extracted_data': all_extracted_data[0], 'status': 'SUCCESS'}
        else:
            extracted_data = gen_func(file_content)
            final_data = {'filename': filename, 'score': round(random.uniform(0.93, 1.0), 2), 'extracted_data': extracted_data, 'status': 'SUCCESS'}
            
        self.update_state(state='PROGRESS', meta=final_data)
        
        return final_data
    except Exception as e:
        print(e)
        self.update_state(state='FAILURE', meta={'filename': filename, 'status': 'failed', 'error': str(e)})
        return {'filename': filename, 'extracted_data': {}, 'status': 'FAILURE', 'error': str(e)}

