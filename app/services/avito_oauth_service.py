"""
Сервис OAuth авторизации для Avito API
Использует authorization_code flow для персональной авторизации
"""

import aiohttp
import asyncio
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging
import os
import json
from urllib.parse import urlencode
import webbrowser

logger = logging.getLogger(__name__)

class AvitoOAuthService:
    """Сервис для OAuth авторизации в Avito API"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_base_url = "https://avito.ru/oauth"
        self.token_url = "https://api.avito.ru/token"
        self.redirect_uri = "http://localhost:8001/avito/oauth/callback"
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.token_file = "avito_token.json"
        
        # Пробуем загрузить сохраненный токен
        self.load_saved_token()
    
    def load_saved_token(self):
        """Загрузка сохраненного токена из файла"""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                    self.access_token = data.get('access_token')
                    self.refresh_token = data.get('refresh_token')
                    expires_at = data.get('expires_at')
                    if expires_at:
                        self.token_expires_at = datetime.fromisoformat(expires_at)
                    logger.info("Loaded saved Avito token")
            except Exception as e:
                logger.error(f"Failed to load saved token: {e}")
    
    def save_token(self):
        """Сохранение токена в файл"""
        try:
            data = {
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'expires_at': self.token_expires_at.isoformat() if self.token_expires_at else None
            }
            with open(self.token_file, 'w') as f:
                json.dump(data, f)
            logger.info("Saved Avito token")
        except Exception as e:
            logger.error(f"Failed to save token: {e}")
    
    def get_authorization_url(self, state: str = None) -> str:
        """Получение URL для авторизации пользователя"""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'messenger:read messenger:write items:info user:read'
        }
        if state:
            params['state'] = state
        
        return f"{self.auth_base_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Dict:
        """Обмен authorization code на access token"""
        async with aiohttp.ClientSession() as session:
            data = {
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'redirect_uri': self.redirect_uri
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            logger.info("Exchanging authorization code for token")
            
            async with session.post(self.token_url, data=data, headers=headers) as response:
                response_text = await response.text()
                
                if response.status != 200:
                    logger.error(f"Failed to exchange code: {response_text}")
                    raise Exception(f"Failed to exchange code (status {response.status}): {response_text}")
                
                result = await response.json()
                self.access_token = result['access_token']
                self.refresh_token = result.get('refresh_token')
                expires_in = result.get('expires_in', 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                
                # Сохраняем токен
                self.save_token()
                
                logger.info("Successfully obtained access token")
                return result
    
    async def refresh_access_token(self) -> str:
        """Обновление access token используя refresh token"""
        if not self.refresh_token:
            raise Exception("No refresh token available")
        
        async with aiohttp.ClientSession() as session:
            data = {
                'grant_type': 'refresh_token',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            logger.info("Refreshing access token")
            
            async with session.post(self.token_url, data=data, headers=headers) as response:
                response_text = await response.text()
                
                if response.status != 200:
                    logger.error(f"Failed to refresh token: {response_text}")
                    raise Exception(f"Failed to refresh token (status {response.status}): {response_text}")
                
                result = await response.json()
                self.access_token = result['access_token']
                if 'refresh_token' in result:
                    self.refresh_token = result['refresh_token']
                expires_in = result.get('expires_in', 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                
                # Сохраняем обновленный токен
                self.save_token()
                
                logger.info("Successfully refreshed access token")
                return self.access_token
    
    async def get_valid_token(self) -> str:
        """Получение валидного access token"""
        # Если токен есть и не истек, возвращаем его
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
        
        # Если есть refresh token, пробуем обновить
        if self.refresh_token:
            try:
                return await self.refresh_access_token()
            except Exception as e:
                logger.error(f"Failed to refresh token: {e}")
                # Если обновление не удалось, нужна новая авторизация
                raise Exception("Token refresh failed. Please re-authorize.")
        
        # Если нет токена, нужна авторизация
        raise Exception("No valid token. Please authorize first.")
    
    async def get_user_info(self) -> Dict:
        """Получение информации о пользователе для определения user_id"""
        token = await self.get_valid_token()
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            }
            
            # Пробуем получить информацию о пользователе
            async with session.get('https://api.avito.ru/core/v1/accounts/self', headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    response_text = await response.text()
                    logger.error(f"Failed to get user info: {response_text}")
                    raise Exception(f"Failed to get user info: {response_text}")

# Глобальный экземпляр OAuth сервиса
_oauth_service: Optional[AvitoOAuthService] = None

def init_oauth_service(client_id: str, client_secret: str):
    """Инициализация OAuth сервиса"""
    global _oauth_service
    _oauth_service = AvitoOAuthService(client_id, client_secret)
    return _oauth_service

def get_oauth_service() -> AvitoOAuthService:
    """Получение экземпляра OAuth сервиса"""
    if _oauth_service is None:
        raise Exception("OAuth service is not initialized. Call init_oauth_service first.")
    return _oauth_service