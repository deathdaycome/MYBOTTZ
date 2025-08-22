"""
OAuth роутер для Avito
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
import logging
from dotenv import load_dotenv

load_dotenv()

from ...services.avito_oauth_service import init_oauth_service, get_oauth_service
from ...services.avito_service import init_avito_service, get_avito_service
from ..middleware.auth import authenticate
from ..navigation import get_navigation_items

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/avito/oauth", tags=["avito-oauth"])
templates = Jinja2Templates(directory="app/admin/templates")

# Инициализируем OAuth сервис
AVITO_CLIENT_ID = os.getenv("AVITO_CLIENT_ID")
AVITO_CLIENT_SECRET = os.getenv("AVITO_CLIENT_SECRET")

if AVITO_CLIENT_ID and AVITO_CLIENT_SECRET:
    init_oauth_service(AVITO_CLIENT_ID, AVITO_CLIENT_SECRET)
    logger.info("Avito OAuth service initialized")

@router.get("/login")
async def oauth_login(request: Request, username: str = Depends(authenticate)):
    """Начало OAuth авторизации - редирект на Avito"""
    try:
        oauth_service = get_oauth_service()
        auth_url = oauth_service.get_authorization_url(state=username)
        return RedirectResponse(url=auth_url)
    except Exception as e:
        logger.error(f"OAuth login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback")
async def oauth_callback(
    request: Request,
    code: str = None,
    error: str = None,
    state: str = None
):
    """Callback для OAuth авторизации"""
    if error:
        logger.error(f"OAuth callback error: {error}")
        return templates.TemplateResponse("avito_oauth_error.html", {
            "request": request,
            "error": error,
            "navigation": get_navigation_items("/avito")
        })
    
    if not code:
        logger.error("OAuth callback without code")
        return templates.TemplateResponse("avito_oauth_error.html", {
            "request": request,
            "error": "No authorization code received",
            "navigation": get_navigation_items("/avito")
        })
    
    try:
        oauth_service = get_oauth_service()
        
        # Обмениваем код на токен
        token_data = await oauth_service.exchange_code_for_token(code)
        
        # Получаем информацию о пользователе
        try:
            user_info = await oauth_service.get_user_info()
            user_id = user_info.get('id')
            
            if user_id:
                # Сохраняем user_id в переменные окружения
                os.environ["AVITO_USER_ID"] = str(user_id)
                
                # Переинициализируем основной сервис с новым токеном
                init_avito_service(AVITO_CLIENT_ID, AVITO_CLIENT_SECRET, user_id)
                
                # Обновляем токен в основном сервисе
                avito_service = get_avito_service()
                avito_service.access_token = oauth_service.access_token
                avito_service.token_expires_at = oauth_service.token_expires_at
                
                logger.info(f"OAuth successful, user_id: {user_id}")
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            # Продолжаем даже если не удалось получить user info
            user_id = os.getenv("AVITO_USER_ID")
            if user_id:
                init_avito_service(AVITO_CLIENT_ID, AVITO_CLIENT_SECRET, int(user_id))
                avito_service = get_avito_service()
                avito_service.access_token = oauth_service.access_token
                avito_service.token_expires_at = oauth_service.token_expires_at
        
        # Редирект на страницу мессенджера
        return RedirectResponse(url="/avito?auth=success", status_code=303)
        
    except Exception as e:
        logger.error(f"OAuth callback processing error: {e}")
        return templates.TemplateResponse("avito_oauth_error.html", {
            "request": request,
            "error": str(e),
            "navigation": get_navigation_items("/avito")
        })

@router.get("/status")
async def oauth_status(username: str = Depends(authenticate)):
    """Проверка статуса OAuth авторизации"""
    try:
        oauth_service = get_oauth_service()
        
        # Проверяем наличие валидного токена
        try:
            token = await oauth_service.get_valid_token()
            has_token = bool(token)
        except:
            has_token = False
        
        return JSONResponse({
            "authorized": has_token,
            "has_refresh_token": bool(oauth_service.refresh_token),
            "token_expires_at": oauth_service.token_expires_at.isoformat() if oauth_service.token_expires_at else None
        })
    except Exception as e:
        return JSONResponse({
            "authorized": False,
            "error": str(e)
        })