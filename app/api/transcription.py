"""
Transcription API Routes
Handles audio/video transcription endpoints
"""

import uuid
import asyncio
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Body
from fastapi.responses import FileResponse
from pydantic import BaseModel

import logging
logger = logging.getLogger(__name__)
from app.services.transcription_service import transcription_service


router = APIRouter(prefix="/transcription", tags=["Transcription"])


# Request models
class FinalizeUploadRequest(BaseModel):
    sessionId: str
    filename: str


class TranscriptionResponse(BaseModel):
    """Response model for transcription task"""
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    """Response model for task status"""
    task_id: str
    status: str
    progress: int
    stage: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None


@router.post("/upload-recording-chunk")
async def upload_recording_chunk(
    chunk: UploadFile = File(...),
    timestamp: str = Form(...),
    session_id: Optional[str] = Form(None)
):
    """
    Upload audio chunk for auto-save during recording

    Args:
        chunk: Audio chunk file
        timestamp: Timestamp of the chunk
        session_id: Session ID for grouping chunks

    Returns:
        Success message with session ID
    """
    try:
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())

        # Read chunk content
        content = await chunk.read()

        # Save chunk
        await transcription_service.save_chunk(content, session_id)

        logger.info(f"chunk_uploaded session_id={session_id} timestamp={timestamp} size={len(content)}")

        return {
            "success": True,
            "session_id": session_id,
            "timestamp": timestamp,
            "message": "Chunk saved successfully"
        }

    except Exception as e:
        logger.error(f"chunk_upload_error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/finalize", response_model=TranscriptionResponse)
async def finalize_recording(
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...)
):
    """
    Finalize recording and start transcription

    Args:
        audio: Final audio file
        background_tasks: FastAPI background tasks

    Returns:
        Task ID for tracking progress
    """
    try:
        # Generate task ID
        task_id = str(uuid.uuid4())

        # Read audio content
        content = await audio.read()

        # Save audio file
        file_path = await transcription_service.save_uploaded_file(
            content,
            f"recording_{task_id}.webm"
        )

        # Start processing in background
        background_tasks.add_task(
            transcription_service.process_audio,
            file_path,
            task_id
        )

        logger.info(f"transcription_started task_id={task_id} filename={audio.filename} size={len(content)}")

        return TranscriptionResponse(
            task_id=task_id,
            status="processing",
            message="Transcription started"
        )

    except Exception as e:
        logger.error(f"finalize_error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-video", response_model=TranscriptionResponse)
async def upload_video(
    video: UploadFile = File(...)
):
    """
    Upload video/audio file for transcription

    Args:
        video: Video/audio file

    Returns:
        Task ID for tracking progress
    """
    import aiofiles
    try:
        # Generate task ID FIRST
        task_id = str(uuid.uuid4())

        # Initialize task IMMEDIATELY so we can return response right away
        transcription_service.tasks[task_id] = {
            "status": "processing",
            "progress": 0,
            "stage": "Сохранение файла (потоковая запись)...",
        }

        logger.info(f"video_upload_started task_id={{task_id}}             filename={{video.filename")

        # Save file SYNCHRONOUSLY to disk before starting background task
        file_extension = Path(video.filename).suffix
        file_path = transcription_service.upload_dir / f"{task_id}{file_extension}"

        # Stream file to disk chunk by chunk (10MB chunks)
        CHUNK_SIZE = 10 * 1024 * 1024  # 10MB chunks
        total_size = 0

        async with aiofiles.open(file_path, "wb") as f:
            while True:
                chunk = await video.read(CHUNK_SIZE)
                if not chunk:
                    break

                await f.write(chunk)
                total_size += len(chunk)

                # Validate size limit (10GB)
                if total_size > 10 * 1024 * 1024 * 1024:
                    # Delete partial file
                    file_path.unlink(missing_ok=True)
                    transcription_service.tasks[task_id] = {
                        "status": "failed",
                        "progress": 0,
                        "error": "Файл слишком большой. Максимальный размер 10GB"
                    }
                    raise HTTPException(status_code=413, detail="Файл слишком большой. Максимальный размер 10GB")

        logger.info(
            "video_saved",
            task_id=task_id,
            filename=video.filename,
            size=total_size,
            path=str(file_path)
        )

        # Update task status
        transcription_service.tasks[task_id]["stage"] = "Файл сохранен, начало обработки..."
        transcription_service.tasks[task_id]["progress"] = 10

        # Start processing in background with file PATH (not UploadFile object)
        asyncio.create_task(
            transcription_service.process_audio(file_path, task_id)
        )

        # Return response
        return TranscriptionResponse(
            task_id=task_id,
            status="processing",
            message="Загрузка принята, начинается обработка"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"video_upload_error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Get transcription task status

    Args:
        task_id: Task ID to check

    Returns:
        Current task status and progress
    """
    try:
        task = transcription_service.get_task_status(task_id)

        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        return TaskStatusResponse(
            task_id=task_id,
            status=task["status"],
            progress=task.get("progress", 0),
            stage=task.get("stage"),
            result=task.get("result"),
            error=task.get("error")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"status_check_error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download transcription result file

    Args:
        filename: Name of the file to download

    Returns:
        File download response
    """
    try:
        file_path = transcription_service.get_file_path(filename)

        if not file_path or not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )

        # Determine media type
        media_type = "application/octet-stream"
        if filename.endswith(".docx"):
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif filename.endswith(".mp3"):
            media_type = "audio/mpeg"

        logger.info(f"file_download filename={filename}")

        return FileResponse(
            path=str(file_path),
            media_type=media_type,
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"download_error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/task/{task_id}")
async def delete_task(task_id: str):
    """
    Delete transcription task and associated files

    Args:
        task_id: Task ID to delete

    Returns:
        Success message
    """
    try:
        task = transcription_service.get_task_status(task_id)

        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        # Delete associated files
        docx_file = transcription_service.get_file_path(f"{task_id}_transcript.docx")
        audio_file = transcription_service.get_file_path(f"{task_id}_audio.mp3")

        if docx_file and docx_file.exists():
            docx_file.unlink()

        if audio_file and audio_file.exists():
            audio_file.unlink()

        # Remove task from memory
        transcription_service.tasks.pop(task_id, None)

        logger.info(f"task_deleted task_id={task_id}")

        return {
            "success": True,
            "message": "Task and files deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"delete_error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-chunk")
async def upload_chunk(
    chunk: UploadFile = File(...),
    chunkIndex: int = Form(...),
    totalChunks: int = Form(...),
    sessionId: str = Form(...),
    filename: str = Form(...)
):
    """Upload file chunk for large video files"""
    try:
        import aiofiles

        # Create session directory
        session_dir = transcription_service.upload_dir / sessionId
        session_dir.mkdir(exist_ok=True)

        # Save chunk
        chunk_path = session_dir / f"chunk_{chunkIndex}"
        content = await chunk.read()

        async with aiofiles.open(chunk_path, "wb") as f:
            await f.write(content)

        logger.info(
            "chunk_uploaded",
            session=sessionId,
            chunk=chunkIndex,
            total=totalChunks,
            size=len(content)
        )

        return {"success": True, "chunkIndex": chunkIndex}

    except Exception as e:
        logger.error(f"chunk_upload_error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/finalize-upload", response_model=TranscriptionResponse)
async def finalize_upload(
    background_tasks: BackgroundTasks,
    request: FinalizeUploadRequest
):
    """Combine chunks and start processing"""
    try:
        session_id = request.sessionId
        filename = request.filename

        if not session_id or not filename:
            raise HTTPException(status_code=400, detail="Missing sessionId or filename")

        task_id = str(uuid.uuid4())
        session_dir = transcription_service.upload_dir / session_id

        if not session_dir.exists():
            raise HTTPException(status_code=404, detail="Session not found")

        # Check that chunks exist
        chunks = list(session_dir.glob("chunk_*"))
        if not chunks:
            raise HTTPException(status_code=404, detail="No chunks found")

        # Initialize task IMMEDIATELY
        transcription_service.tasks[task_id] = {
            "status": "processing",
            "progress": 0,
            "stage": "Подготовка к обработке...",
            "started_at": str(uuid.uuid4())  # Just a timestamp placeholder
        }

        # Start combining chunks and processing in background
        background_tasks.add_task(
            transcription_service.combine_chunks_and_process,
            session_id,
            filename,
            task_id
        )

        logger.info(
            "upload_finalized",
            task_id=task_id,
            session=session_id,
            filename=filename,
            chunk_count=len(chunks)
        )

        # Return IMMEDIATELY - don't wait for chunk combining
        return TranscriptionResponse(
            task_id=task_id,
            status="processing",
            message="File uploaded successfully, processing started"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"finalize_error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_transcriptions():
    """
    Get list of all completed transcriptions

    Returns:
        List of transcriptions with download links
    """
    try:
        from pathlib import Path
        import os

        transcriptions = []
        upload_dir = transcription_service.upload_dir

        # Find all transcript files
        for docx_file in sorted(upload_dir.glob("*_transcript.docx"), key=os.path.getmtime, reverse=True):
            task_id = docx_file.stem.replace("_transcript", "")
            audio_file = upload_dir / f"{task_id}_audio.mp3"

            if audio_file.exists():
                # Get file metadata
                created_at = datetime.fromtimestamp(docx_file.stat().st_mtime).isoformat()

                transcriptions.append({
                    "task_id": task_id,
                    "docx_url": f"/api/v1/transcription/download/{task_id}_transcript.docx",
                    "audio_url": f"/api/v1/transcription/download/{task_id}_audio.mp3",
                    "created_at": created_at,
                    "docx_size": docx_file.stat().st_size,
                    "audio_size": audio_file.stat().st_size
                })

        return {
            "success": True,
            "transcriptions": transcriptions,
            "total": len(transcriptions)
        }

    except Exception as e:
        logger.error(f"list_transcriptions_error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check endpoint for transcription service

    Returns:
        Service health status
    """
    try:
        # Check if ffmpeg is available
        import shutil
        ffmpeg_available = shutil.which("ffmpeg") is not None

        # Check if faster-whisper is available
        try:
            import faster_whisper
            whisper_available = True
        except ImportError:
            whisper_available = False

        return {
            "status": "healthy",
            "ffmpeg_available": ffmpeg_available,
            "whisper_available": whisper_available,
            "openrouter_configured": bool(transcription_service.openrouter_api_key),
            "active_tasks": len(transcription_service.tasks)
        }

    except Exception as e:
        logger.error(f"health_check_error: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
