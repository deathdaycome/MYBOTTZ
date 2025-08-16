# app/admin/routers/backup.py
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, Any, Optional
import os
import io

from ...database.database import get_db
from ...database.models import AdminUser
from ...services.backup_service import backup_service
from ...config.logging import get_logger
from ..auth import get_current_admin_user

logger = get_logger(__name__)
router = APIRouter(prefix="/backup", tags=["backup"])
templates = Jinja2Templates(directory="app/admin/templates")


@router.get("/", response_class=HTMLResponse)
async def backup_page(
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Страница управления резервными копиями"""
    # Только для владельца
    if current_user.role != "owner" and current_user.username != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    return templates.TemplateResponse(
        "backup.html",
        {
            "request": request,
            "user": current_user
        }
    )


@router.get("/list")
async def list_backups(
    current_user: AdminUser = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Получить список резервных копий"""
    # Только для владельца
    if current_user.role != "owner" and current_user.username != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    try:
        backups = backup_service.list_backups()
        return {
            "success": True,
            "backups": backups,
            "auto_backup_enabled": backup_service.auto_backup_enabled,
            "backup_time": backup_service.backup_time,
            "max_backups": backup_service.max_backups
        }
    except Exception as e:
        logger.error(f"Ошибка получения списка backup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create")
async def create_backup(
    description: Optional[str] = None,
    current_user: AdminUser = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Создать резервную копию"""
    # Только для владельца
    if current_user.role != "owner" and current_user.username != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    try:
        result = backup_service.create_backup(
            description=description or f"Manual backup by {current_user.username}"
        )
        
        if result['success']:
            return {
                "success": True,
                "message": "Резервная копия создана успешно",
                "backup_name": result['backup_name'],
                "metadata": result['metadata']
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Неизвестная ошибка'))
            
    except Exception as e:
        logger.error(f"Ошибка создания backup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restore/{backup_name}")
async def restore_backup(
    backup_name: str,
    current_user: AdminUser = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Восстановить резервную копию"""
    # Только для владельца
    if current_user.role != "owner" and current_user.username != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    try:
        # Создаем резервную копию перед восстановлением
        pre_restore_backup = backup_service.create_backup(
            description=f"Pre-restore backup (before restoring {backup_name})"
        )
        
        if not pre_restore_backup['success']:
            raise HTTPException(
                status_code=500, 
                detail="Не удалось создать резервную копию перед восстановлением"
            )
        
        # Восстанавливаем
        result = backup_service.restore_backup(backup_name)
        
        if result['success']:
            return {
                "success": True,
                "message": "База данных восстановлена успешно",
                "pre_restore_backup": pre_restore_backup['backup_name'],
                "restored_tables": result.get('restored_tables', []),
                "restored_records": result.get('restored_records', 0)
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Неизвестная ошибка'))
            
    except Exception as e:
        logger.error(f"Ошибка восстановления backup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{backup_name}")
async def delete_backup(
    backup_name: str,
    current_user: AdminUser = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Удалить резервную копию"""
    # Только для владельца
    if current_user.role != "owner" and current_user.username != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    try:
        success = backup_service.delete_backup(backup_name)
        
        if success:
            return {
                "success": True,
                "message": "Резервная копия удалена"
            }
        else:
            raise HTTPException(status_code=404, detail="Резервная копия не найдена")
            
    except Exception as e:
        logger.error(f"Ошибка удаления backup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{backup_name}")
async def download_backup(
    backup_name: str,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Скачать резервную копию"""
    # Только для владельца
    if current_user.role != "owner" and current_user.username != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    try:
        from pathlib import Path
        
        backup_dir = Path("backups")
        
        # Проверяем сжатую версию
        compressed_file = backup_dir / f"{backup_name}.tar.gz"
        if compressed_file.exists():
            return FileResponse(
                path=compressed_file,
                media_type='application/gzip',
                filename=f"{backup_name}.tar.gz"
            )
        
        # Проверяем несжатую версию и сжимаем на лету
        backup_path = backup_dir / backup_name
        if backup_path.exists():
            import tarfile
            import tempfile
            
            # Создаем временный архив
            temp_file = tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False)
            
            with tarfile.open(temp_file.name, 'w:gz') as tar:
                tar.add(backup_path, arcname=backup_name)
            
            return FileResponse(
                path=temp_file.name,
                media_type='application/gzip',
                filename=f"{backup_name}.tar.gz"
            )
        
        raise HTTPException(status_code=404, detail="Резервная копия не найдена")
        
    except Exception as e:
        logger.error(f"Ошибка скачивания backup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_backup(
    file: UploadFile = File(...),
    current_user: AdminUser = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Загрузить резервную копию"""
    # Только для владельца
    if current_user.role != "owner" and current_user.username != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    try:
        if not file.filename.endswith('.tar.gz'):
            raise HTTPException(
                status_code=400, 
                detail="Неверный формат файла. Ожидается .tar.gz"
            )
        
        from pathlib import Path
        
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Сохраняем файл
        file_path = backup_dir / file.filename
        
        contents = await file.read()
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        # Проверяем, что это валидный backup
        import tarfile
        import json
        
        try:
            with tarfile.open(file_path, 'r:gz') as tar:
                # Ищем metadata.json
                members = tar.getmembers()
                metadata_found = False
                
                for member in members:
                    if 'metadata.json' in member.name:
                        metadata_file = tar.extractfile(member)
                        metadata = json.loads(metadata_file.read().decode('utf-8'))
                        metadata_found = True
                        break
                
                if not metadata_found:
                    file_path.unlink()
                    raise HTTPException(
                        status_code=400,
                        detail="Файл не является валидной резервной копией"
                    )
        except tarfile.TarError:
            file_path.unlink()
            raise HTTPException(
                status_code=400,
                detail="Не удалось прочитать архив"
            )
        
        return {
            "success": True,
            "message": "Резервная копия загружена успешно",
            "filename": file.filename,
            "size": len(contents)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка загрузки backup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto-backup/toggle")
async def toggle_auto_backup(
    enabled: bool,
    current_user: AdminUser = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Включить/выключить автоматическое резервное копирование"""
    # Только для владельца
    if current_user.role != "owner" and current_user.username != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    try:
        backup_service.auto_backup_enabled = enabled
        
        if enabled:
            backup_service.start_auto_backup()
            message = "Автоматическое резервное копирование включено"
        else:
            backup_service.stop_auto_backup()
            message = "Автоматическое резервное копирование выключено"
        
        return {
            "success": True,
            "message": message,
            "enabled": enabled
        }
        
    except Exception as e:
        logger.error(f"Ошибка переключения auto-backup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/settings")
async def update_backup_settings(
    settings: Dict[str, Any],
    current_user: AdminUser = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Обновить настройки резервного копирования"""
    # Только для владельца
    if current_user.role != "owner" and current_user.username != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    try:
        if 'backup_time' in settings:
            backup_service.backup_time = settings['backup_time']
        
        if 'max_backups' in settings:
            backup_service.max_backups = int(settings['max_backups'])
        
        # Перезапускаем автоматическое резервное копирование с новыми настройками
        if backup_service.auto_backup_enabled:
            backup_service.stop_auto_backup()
            backup_service.start_auto_backup()
        
        return {
            "success": True,
            "message": "Настройки обновлены",
            "settings": {
                "backup_time": backup_service.backup_time,
                "max_backups": backup_service.max_backups,
                "auto_backup_enabled": backup_service.auto_backup_enabled
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка обновления настроек backup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))