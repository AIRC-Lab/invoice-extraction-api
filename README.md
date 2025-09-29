# Invoice Extraction API

This project provides a FastAPI-based API for extracting information from invoice PDFs or images using Google Gemini AI. It supports multi-file uploads, asynchronous processing with Celery and Redis, and is designed for containerized deployment with Docker.

## Features

- **Invoice Data Extraction**: Utilizes Google Gemini Pro Vision for intelligent extraction of key invoice details.
- **Multi-file Support**: Process multiple invoice files in a single request.
- **Asynchronous Processing**: Leverages Celery and Redis for background job processing, preventing API timeouts.
- **Job Status Tracking**: API endpoint to check the status and results of extraction jobs.
- **Containerized Deployment**: Docker and Docker Compose for easy setup and deployment.

## Project Structure

```
.env
Dockerfile.app
Dockerfile.worker
docker-compose.yml
requirements.txt
app/
├── main.py
└── schemas.py
config/
└── config.py
worker/
└── celery_app.py
```

## Setup and Deployment

### Prerequisites

- Docker and Docker Compose installed.
- Google Gemini API Key.

### 1. Obtain Google Gemini API Key

Get your API key from the [Google AI Studio](https://aistudio.google.com/app/apikey).

### 2. Configure Environment Variables

Create a `.env` file in the root directory of the project and add your Gemini API key:

```
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

### 3. Build and Run with Docker Compose

Navigate to the root directory of the project and run:

```bash
docker-compose up --build -d
```

This command will:
- Build the Docker images for the FastAPI application and Celery worker.
- Start a Redis container.
- Start the FastAPI application (accessible at `http://localhost:8000`).
- Start the Celery worker.

## API Endpoints

### 1. Extract Invoice

- **URL**: `/extract-invoice`
- **Method**: `POST`
- **Description**: Upload one or more invoice files (PDF or image) for extraction.
- **Request Body**: `multipart/form-data` with `files` field (multiple files allowed).
- **Response**: A list of task statuses, each containing a `task_id` and `filename`.

Example using `curl`:

```bash
curl -X POST "http://localhost:8000/extract-invoice" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@/path/to/your/invoice1.pdf" \
  -F "files=@/path/to/your/invoice2.jpg"
```

### 2. Get Task Status

- **URL**: `/status/{task_id}`
- **Method**: `GET`
- **Description**: Check the status and retrieve the extracted data for a specific task.
- **Response**: A JSON object with `task_id`, `status`, `filename`, and `result` (extracted data).

Example using `curl`:

```bash
curl -X GET "http://localhost:8000/status/YOUR_TASK_ID"
```

## Development

### Local Setup (without Docker)

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Redis**: You'll need a running Redis instance. You can use Docker for this:
   ```bash
   docker run --name some-redis -p 6379:6379 -d redis
   ```

3. **Set environment variables**:
   Create a `.env` file as described above.

4. **Run FastAPI app**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Run Celery worker**:
   ```bash
   celery -A worker.celery_app worker --loglevel=info
   ```

## Future Improvements

- **PDF to Image Conversion**: Implement a robust PDF to image conversion step before sending to Gemini Pro Vision.
- **Error Handling**: More detailed error handling and logging.
- **Authentication**: Add API key authentication for secure access.
- **Structured Output Validation**: Implement Pydantic models for validating Gemini's JSON output.
- **Frontend**: A simple web interface for uploading invoices and viewing results.

