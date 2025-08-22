"""
Сервис для работы с API Авито
Интеграция мессенджера Авито в CRM
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import logging
from dataclasses import dataclass
from enum import Enum
from datetime import timedelta

logger = logging.getLogger(__name__)

class MessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    LINK = "link"
    SYSTEM = "system"
    DELETED = "deleted"

@dataclass
class AvitoMessage:
    id: str
    author_id: int
    content: Dict[str, Any]
    created: int
    direction: str  # "in" or "out"
    type: MessageType
    is_read: bool = False
    
    @property
    def created_datetime(self):
        return datetime.fromtimestamp(self.created)
    
    def to_dict(self):
        return {
            "id": self.id,
            "author_id": self.author_id,
            "content": self.content,
            "created": self.created,
            "created_datetime": self.created_datetime.isoformat(),
            "direction": self.direction,
            "type": self.type.value,
            "is_read": self.is_read
        }

@dataclass
class AvitoChat:
    id: str
    users: List[Dict[str, Any]]
    context: Optional[Dict[str, Any]]
    created: int
    updated: int
    last_message: Optional[AvitoMessage]
    unread_count: int = 0
    
    @property
    def created_datetime(self):
        return datetime.fromtimestamp(self.created)
    
    @property
    def updated_datetime(self):
        return datetime.fromtimestamp(self.updated)
    
    def to_dict(self):
        return {
            "id": self.id,
            "users": self.users,
            "context": self.context,
            "created": self.created,
            "created_datetime": self.created_datetime.isoformat(),
            "updated": self.updated,
            "updated_datetime": self.updated_datetime.isoformat(),
            "last_message": self.last_message.to_dict() if self.last_message else None,
            "unread_count": self.unread_count
        }

class AvitoService:
    """Сервис для работы с API Авито"""
    
    def __init__(self, client_id: str, client_secret: str, user_id: int = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_id = user_id
        self.base_url = "https://api.avito.ru"
        self.auth_url = "https://api.avito.ru/token"
        self.access_token = None
        self.token_expires_at = None
        
    async def _get_access_token(self) -> str:
        """Получение токена доступа через OAuth 2.0 client_credentials"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
            
        async with aiohttp.ClientSession() as session:
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "messenger:read messenger:write"
            }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            logger.info(f"Getting access token for client_id: {self.client_id[:10]}...")
            
            async with session.post(self.auth_url, data=data, headers=headers) as response:
                response_text = await response.text()
                logger.info(f"Token response status: {response.status}")
                
                if response.status != 200:
                    logger.error(f"Failed to get access token: {response_text}")
                    raise Exception(f"Failed to get access token (status {response.status}): {response_text}")
                    
                result = await response.json()
                self.access_token = result["access_token"]
                expires_in = result.get("expires_in", 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                
                logger.info(f"Access token received, expires in {expires_in} seconds")
                return self.access_token
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Выполнение запроса к API Авито"""
        token = await self._get_access_token()
        
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        headers["Accept"] = "application/json"
        if method in ["POST", "PUT", "PATCH"]:
            headers["Content-Type"] = "application/json"
        
        url = f"{self.base_url}{endpoint}"
        
        logger.info(f"Making API request: {method} {endpoint}")
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, **kwargs) as response:
                response_text = await response.text()
                logger.debug(f"API response status: {response.status}, body length: {len(response_text)}")
                
                if response.status == 403:
                    logger.error(f"Access denied (403): {response_text}")
                    error_msg = "Permission denied. Check User ID and app permissions."
                    try:
                        error_data = await response.json()
                        if error_data.get("error", {}).get("message"):
                            error_msg = error_data["error"]["message"]
                    except:
                        pass
                    raise Exception(f"403 Forbidden: {error_msg}")
                    
                if response.status not in [200, 201]:
                    logger.error(f"API request failed: {response_text}")
                    raise Exception(f"API request failed with status {response.status}: {response_text}")
                    
                try:
                    return await response.json()
                except:
                    logger.error(f"Failed to parse JSON response: {response_text[:500]}")
                    return {}
    
    async def get_chats(self, unread_only: bool = False, limit: int = 100, offset: int = 0) -> List[AvitoChat]:
        """Получение списка чатов"""
        if not self.user_id:
            logger.error("User ID is not set. Please configure Avito service with user_id.")
            raise Exception("User ID is not set. Please configure Avito service with user_id.")
            
        params = {
            "limit": limit,
            "offset": offset,
            "unread_only": str(unread_only).lower(),
            "chat_types": "u2i,u2u"  # чаты по объявлениям и между пользователями
        }
        
        logger.info(f"Getting chats for user_id: {self.user_id} with params: {params}")
        
        result = await self._make_request(
            "GET",
            f"/messenger/v2/accounts/{self.user_id}/chats",
            params=params
        )
        
        logger.info(f"Received {len(result.get('chats', []))} chats from API")
        
        chats = []
        for chat_data in result.get("chats", []):
            try:
                last_message = None
                if chat_data.get("last_message"):
                    msg = chat_data["last_message"]
                    last_message = AvitoMessage(
                        id=msg.get("id", ""),
                        author_id=msg.get("author_id", 0),
                        content=msg.get("content", {}),
                        created=msg.get("created", 0),
                        direction=msg.get("direction", "in"),
                        type=MessageType(msg.get("type", "text")),
                        is_read=msg.get("is_read", False)
                    )
                
                chat = AvitoChat(
                    id=chat_data.get("id", ""),
                    users=chat_data.get("users", []),
                    context=chat_data.get("context"),
                    created=chat_data.get("created", 0),
                    updated=chat_data.get("updated", 0),
                    last_message=last_message,
                    unread_count=chat_data.get("unread_count", 0)
                )
                chats.append(chat)
            except Exception as e:
                logger.error(f"Error processing chat data: {e}")
                continue
        
        logger.info(f"Retrieved {len(chats)} chats")
        return chats
    
    async def get_chat_messages(self, chat_id: str, limit: int = 100, offset: int = 0) -> List[AvitoMessage]:
        """Получение сообщений чата"""
        params = {
            "limit": limit,
            "offset": offset
        }
        
        result = await self._make_request(
            "GET",
            f"/messenger/v3/accounts/{self.user_id}/chats/{chat_id}/messages/",
            params=params
        )
        
        messages = []
        # API может возвращать массив напрямую или объект с ключом messages
        if isinstance(result, list):
            messages_data = result
        else:
            messages_data = result.get("messages", [])
        
        logger.info(f"Retrieved {len(messages_data)} messages for chat {chat_id}")
        logger.debug(f"API result structure: {type(result)}, is_list: {isinstance(result, list)}")
        
        for msg in messages_data:
            message = AvitoMessage(
                id=msg["id"],
                author_id=msg.get("author_id", 0),
                content=msg.get("content", {}),
                created=msg.get("created", 0),
                direction=msg.get("direction", "in"),
                type=MessageType(msg.get("type", "text")),
                is_read=msg.get("isRead", msg.get("is_read", False))
            )
            messages.append(message)
        
        return messages
    
    async def send_message(self, chat_id: str, text: str) -> AvitoMessage:
        """Отправка текстового сообщения"""
        data = {
            "message": {
                "text": text
            },
            "type": "text"
        }
        
        result = await self._make_request(
            "POST",
            f"/messenger/v1/accounts/{self.user_id}/chats/{chat_id}/messages",
            json=data
        )
        
        return AvitoMessage(
            id=result["id"],
            author_id=self.user_id,
            content=result.get("content", {}),
            created=result.get("created", 0),
            direction="out",
            type=MessageType(result.get("type", "text")),
            is_read=True
        )
    
    async def send_image(self, chat_id: str, image_id: str) -> AvitoMessage:
        """Отправка изображения"""
        data = {
            "image_id": image_id
        }
        
        result = await self._make_request(
            "POST",
            f"/messenger/v1/accounts/{self.user_id}/chats/{chat_id}/messages/image",
            json=data
        )
        
        return AvitoMessage(
            id=result["id"],
            author_id=result.get("author_id", self.user_id),
            content=result.get("content", {}),
            created=result.get("created", 0),
            direction="out",
            type=MessageType.IMAGE,
            is_read=True
        )
    
    async def upload_image(self, image_data: bytes) -> str:
        """Загрузка изображения"""
        token = await self._get_access_token()
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        url = f"{self.base_url}/messenger/v1/accounts/{self.user_id}/uploadImages"
        
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('uploadfile[]', image_data, filename='image.jpg', content_type='image/jpeg')
            
            async with session.post(url, headers=headers, data=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Failed to upload image: {error_text}")
                    raise Exception(f"Failed to upload image: {error_text}")
                    
                result = await response.json()
                # Возвращаем ID первого загруженного изображения
                return list(result.keys())[0]
    
    async def mark_chat_as_read(self, chat_id: str) -> bool:
        """Отметить чат как прочитанный"""
        result = await self._make_request(
            "POST",
            f"/messenger/v1/accounts/{self.user_id}/chats/{chat_id}/read"
        )
        
        return result.get("ok", False)
    
    async def delete_message(self, chat_id: str, message_id: str) -> bool:
        """Удаление сообщения (в течение часа после отправки)"""
        await self._make_request(
            "POST",
            f"/messenger/v1/accounts/{self.user_id}/chats/{chat_id}/messages/{message_id}"
        )
        
        return True
    
    async def get_chat_info(self, chat_id: str) -> AvitoChat:
        """Получение информации о чате"""
        result = await self._make_request(
            "GET",
            f"/messenger/v2/accounts/{self.user_id}/chats/{chat_id}"
        )
        
        last_message = None
        if result.get("last_message"):
            msg = result["last_message"]
            last_message = AvitoMessage(
                id=msg["id"],
                author_id=msg.get("author_id", 0),
                content=msg.get("content", {}),
                created=msg.get("created", 0),
                direction=msg.get("direction", "in"),
                type=MessageType(msg.get("type", "text")),
                is_read=msg.get("is_read", False)
            )
        
        return AvitoChat(
            id=result["id"],
            users=result.get("users", []),
            context=result.get("context"),
            created=result.get("created", 0),
            updated=result.get("updated", 0),
            last_message=last_message
        )
    
    async def subscribe_webhook(self, webhook_url: str) -> bool:
        """Подписка на webhook уведомления"""
        data = {
            "url": webhook_url
        }
        
        result = await self._make_request(
            "POST",
            "/messenger/v3/webhook",
            json=data
        )
        
        return result.get("ok", False)
    
    async def unsubscribe_webhook(self, webhook_url: str) -> bool:
        """Отписка от webhook уведомлений"""
        data = {
            "url": webhook_url
        }
        
        result = await self._make_request(
            "POST",
            "/messenger/v1/webhook/unsubscribe",
            json=data
        )
        
        return result.get("ok", False)
    
    async def add_to_blacklist(self, blocked_user_id: int, chat_id: str) -> bool:
        """Добавление пользователя в черный список"""
        data = {
            "users": [
                {
                    "id": blocked_user_id,
                    "chat_id": chat_id
                }
            ]
        }
        
        result = await self._make_request(
            "POST",
            f"/messenger/v2/accounts/{self.user_id}/blacklist",
            json=data
        )
        
        return True

# Singleton instance
avito_service = None

def init_avito_service(client_id: str, client_secret: str, user_id: int):
    """Инициализация сервиса Авито"""
    global avito_service
    avito_service = AvitoService(client_id, client_secret, user_id)
    return avito_service

def get_avito_service() -> AvitoService:
    """Получение экземпляра сервиса Авито"""
    if avito_service is None:
        raise Exception("Avito service is not initialized. Call init_avito_service first.")
    return avito_service