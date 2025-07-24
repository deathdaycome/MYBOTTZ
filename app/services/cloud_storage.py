"""
Сервис для работы с облачным хранилищем файлов
Поддержка S3-совместимых хранилищ
"""
import os
import logging
from typing import Optional, BinaryIO
from pathlib import Path
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from ..config.production import get_production_config

logger = logging.getLogger(__name__)

class CloudStorageService:
    """Сервис для работы с облачным хранилищем"""
    
    def __init__(self):
        self.config = get_production_config()
        self.client = None
        self.bucket_name = self.config.CLOUD_STORAGE_BUCKET
        
        if self.config.STORAGE_TYPE == "cloud" and self._should_use_cloud():
            self._init_s3_client()
    
    def _should_use_cloud(self) -> bool:
        """Проверяет, можно ли использовать облачное хранилище"""
        return all([
            self.config.CLOUD_STORAGE_BUCKET,
            self.config.CLOUD_STORAGE_ACCESS_KEY,
            self.config.CLOUD_STORAGE_SECRET_KEY,
            self.config.CLOUD_STORAGE_REGION
        ])
    
    def _init_s3_client(self):
        """Инициализирует S3 клиент"""
        try:
            self.client = boto3.client(
                's3',
                aws_access_key_id=self.config.CLOUD_STORAGE_ACCESS_KEY,
                aws_secret_access_key=self.config.CLOUD_STORAGE_SECRET_KEY,
                region_name=self.config.CLOUD_STORAGE_REGION
            )
            
            # Проверяем доступность bucket
            self.client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Cloud storage initialized for bucket: {self.bucket_name}")
            
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Failed to initialize cloud storage: {e}")
            self.client = None
    
    def upload_file(self, file_data: BinaryIO, file_path: str) -> str:
        """
        Загружает файл в хранилище
        
        Args:
            file_data: Данные файла
            file_path: Путь для сохранения файла
            
        Returns:
            URL файла или локальный путь
        """
        if self.client and self.config.STORAGE_TYPE == "cloud":
            return self._upload_to_cloud(file_data, file_path)
        else:
            return self._upload_locally(file_data, file_path)
    
    def _upload_to_cloud(self, file_data: BinaryIO, file_path: str) -> str:
        """Загружает файл в облако"""
        try:
            # Убираем начальный слэш если есть
            cloud_key = file_path.lstrip('/')
            
            self.client.upload_fileobj(
                file_data,
                self.bucket_name,
                cloud_key,
                ExtraArgs={'ACL': 'public-read'}
            )
            
            # Возвращаем публичный URL
            url = f"https://{self.bucket_name}.s3.{self.config.CLOUD_STORAGE_REGION}.amazonaws.com/{cloud_key}"
            logger.info(f"File uploaded to cloud: {url}")
            return url
            
        except ClientError as e:
            logger.error(f"Failed to upload file to cloud: {e}")
            # Если не удалось загрузить в облако, сохраняем локально
            return self._upload_locally(file_data, file_path)
    
    def _upload_locally(self, file_data: BinaryIO, file_path: str) -> str:
        """Сохраняет файл локально"""
        try:
            # Создаем полный путь
            full_path = Path(self.config.UPLOAD_DIR) / file_path.lstrip('/')
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Сохраняем файл
            with open(full_path, 'wb') as f:
                file_data.seek(0)  # Возвращаемся в начало файла
                f.write(file_data.read())
            
            # Возвращаем относительный URL
            relative_path = f"/uploads/{file_path.lstrip('/')}"
            logger.info(f"File saved locally: {relative_path}")
            return relative_path
            
        except Exception as e:
            logger.error(f"Failed to save file locally: {e}")
            raise
    
    def delete_file(self, file_path: str) -> bool:
        """
        Удаляет файл из хранилища
        
        Args:
            file_path: Путь к файлу или URL
            
        Returns:
            True если файл удален успешно
        """
        if self.client and self.config.STORAGE_TYPE == "cloud":
            return self._delete_from_cloud(file_path)
        else:
            return self._delete_locally(file_path)
    
    def _delete_from_cloud(self, file_path: str) -> bool:
        """Удаляет файл из облака"""
        try:
            # Извлекаем ключ из URL
            if file_path.startswith('http'):
                # Если это URL, извлекаем ключ
                cloud_key = file_path.split(f"{self.bucket_name}.s3.{self.config.CLOUD_STORAGE_REGION}.amazonaws.com/")[1]
            else:
                cloud_key = file_path.lstrip('/')
            
            self.client.delete_object(Bucket=self.bucket_name, Key=cloud_key)
            logger.info(f"File deleted from cloud: {cloud_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete file from cloud: {e}")
            return False
    
    def _delete_locally(self, file_path: str) -> bool:
        """Удаляет локальный файл"""
        try:
            if file_path.startswith('/uploads/'):
                # Убираем /uploads/ prefix
                relative_path = file_path[9:]
            else:
                relative_path = file_path.lstrip('/')
            
            full_path = Path(self.config.UPLOAD_DIR) / relative_path
            
            if full_path.exists():
                full_path.unlink()
                logger.info(f"File deleted locally: {full_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {full_path}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete local file: {e}")
            return False
    
    def get_file_url(self, file_path: str) -> str:
        """
        Возвращает URL для доступа к файлу
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            URL файла
        """
        if self.config.STORAGE_TYPE == "cloud" and file_path.startswith('http'):
            return file_path
        else:
            # Локальный файл
            if not file_path.startswith('/uploads/'):
                file_path = f"/uploads/{file_path.lstrip('/')}"
            return f"{self.config.BASE_URL}{file_path}"

# Создаем единственный экземпляр сервиса
cloud_storage = CloudStorageService()

def get_cloud_storage() -> CloudStorageService:
    """Возвращает экземпляр сервиса облачного хранилища"""
    return cloud_storage