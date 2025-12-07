"""
Сервис для работы с Wialon API
Отслеживание транспорта в реальном времени
"""

import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from ..config.logging import get_logger
from ..config.settings import settings

logger = get_logger(__name__)


class WialonService:
    """Сервис для интеграции с Wialon API"""

    def __init__(self):
        # API credentials
        self.base_url = "https://hst-api.online.stavtrack.com/wialon/ajax.html"
        self.token = "c1e370f15eb4e4dfc782d35787542986169EEC3EB6849E8F2A5C7AEF8658DD35E9B90F42"
        self.session_id = None

    async def _make_request(
        self,
        svc: str,
        params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Выполнить запрос к Wialon API

        Args:
            svc: Название сервиса (например, 'core/search_items')
            params: Параметры запроса

        Returns:
            Ответ от API
        """
        try:
            request_params = {
                "svc": svc,
                "params": json.dumps(params or {}),
                "sid": self.token
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    params=request_params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Проверка на ошибку в ответе
                        if isinstance(data, dict) and "error" in data:
                            logger.error(f"Wialon API error: {data.get('error')}")
                            return {"error": data.get("error")}

                        return data
                    else:
                        logger.error(f"Wialon API request failed: {response.status}")
                        return {"error": f"HTTP {response.status}"}

        except asyncio.TimeoutError:
            logger.error("Wialon API request timeout")
            return {"error": "Timeout"}
        except Exception as e:
            logger.error(f"Wialon API request exception: {e}")
            return {"error": str(e)}

    async def login_with_token(self) -> bool:
        """Авторизация с использованием токена

        Returns:
            True если авторизация успешна
        """
        try:
            result = await self._make_request("token/login", {"token": self.token})

            if "error" not in result and "eid" in result:
                self.session_id = result.get("eid")
                logger.info(f"Wialon authorization successful, session: {self.session_id}")
                return True
            else:
                logger.error(f"Wialon authorization failed: {result}")
                return False

        except Exception as e:
            logger.error(f"Wialon login error: {e}")
            return False

    async def get_units(self) -> List[Dict[str, Any]]:
        """Получить список всех единиц транспорта (units)

        Returns:
            Список объектов транспорта
        """
        try:
            # Параметры поиска
            params = {
                "spec": {
                    "itemsType": "avl_unit",  # Тип объектов - транспорт
                    "propName": "sys_name",    # Поиск по имени
                    "propValueMask": "*",       # Все объекты
                    "sortType": "sys_name"      # Сортировка по имени
                },
                "force": 1,  # Принудительное обновление данных
                "flags": 1025,  # Флаги: 1 (базовая информация) + 1024 (позиция)
                "from": 0,
                "to": 0  # 0 = все объекты
            }

            result = await self._make_request("core/search_items", params)

            if "error" in result:
                logger.error(f"Failed to get units: {result['error']}")
                return []

            # Извлекаем список units
            if isinstance(result, dict) and "items" in result:
                units = result["items"]
                logger.info(f"Retrieved {len(units)} units from Wialon")
                return units

            return []

        except Exception as e:
            logger.error(f"Error getting units: {e}")
            return []

    async def get_unit_location(self, unit_id: int) -> Optional[Dict[str, Any]]:
        """Получить текущее местоположение транспорта

        Args:
            unit_id: ID единицы транспорта

        Returns:
            Информация о местоположении
        """
        try:
            # Обновляем данные объекта
            params = {
                "id": unit_id,
                "flags": 1025  # Базовая информация + позиция
            }

            result = await self._make_request("core/update_data_flags", params)

            if "error" in result:
                return None

            # Извлекаем информацию о позиции
            if "pos" in result:
                pos = result["pos"]
                return {
                    "unit_id": unit_id,
                    "lat": pos.get("y"),     # Широта
                    "lon": pos.get("x"),     # Долгота
                    "speed": pos.get("s"),   # Скорость
                    "course": pos.get("c"),  # Курс
                    "altitude": pos.get("z"), # Высота
                    "time": pos.get("t"),    # Время GPS
                    "satellites": pos.get("sc") # Количество спутников
                }

            return None

        except Exception as e:
            logger.error(f"Error getting unit location: {e}")
            return None

    async def get_all_units_with_locations(self) -> List[Dict[str, Any]]:
        """Получить все единицы транспорта с их текущими координатами

        Returns:
            Список транспорта с координатами
        """
        try:
            units = await self.get_units()

            result = []
            for unit in units:
                # Извлекаем базовую информацию
                unit_data = {
                    "id": unit.get("id"),
                    "name": unit.get("nm"),  # Название
                    "unique_id": unit.get("uid"),  # Уникальный ID
                }

                # Добавляем координаты если есть
                if "pos" in unit:
                    pos = unit["pos"]
                    unit_data.update({
                        "lat": pos.get("y"),
                        "lon": pos.get("x"),
                        "speed": pos.get("s", 0),
                        "course": pos.get("c", 0),
                        "altitude": pos.get("z", 0),
                        "time": pos.get("t", 0),
                        "satellites": pos.get("sc", 0)
                    })

                # Добавляем информацию о датчиках если есть
                if "sens" in unit:
                    unit_data["sensors"] = unit["sens"]

                result.append(unit_data)

            logger.info(f"Retrieved {len(result)} units with locations")
            return result

        except Exception as e:
            logger.error(f"Error getting units with locations: {e}")
            return []

    async def get_unit_messages(
        self,
        unit_id: int,
        time_from: int,
        time_to: int,
        flags: int = 0
    ) -> List[Dict[str, Any]]:
        """Получить сообщения (треки) транспорта за период

        Args:
            unit_id: ID транспорта
            time_from: Начало периода (Unix timestamp)
            time_to: Конец периода (Unix timestamp)
            flags: Флаги данных

        Returns:
            Список сообщений
        """
        try:
            params = {
                "itemId": unit_id,
                "timeFrom": time_from,
                "timeTo": time_to,
                "flags": flags,
                "flagsMask": 0xFFFFFFFF,
                "loadCount": 0xFFFFFFFF
            }

            result = await self._make_request("messages/load_interval", params)

            if "error" in result:
                logger.error(f"Failed to get messages: {result['error']}")
                return []

            if "messages" in result:
                return result["messages"]

            return []

        except Exception as e:
            logger.error(f"Error getting unit messages: {e}")
            return []

    async def get_drivers(self) -> List[Dict[str, Any]]:
        """Получить список водителей

        Returns:
            Список водителей
        """
        try:
            params = {
                "spec": {
                    "itemsType": "avl_resource",
                    "propName": "sys_name",
                    "propValueMask": "*",
                    "sortType": "sys_name"
                },
                "force": 1,
                "flags": 8192,  # Флаг для водителей
                "from": 0,
                "to": 0
            }

            result = await self._make_request("core/search_items", params)

            if "error" in result:
                return []

            # Обрабатываем результат
            drivers = []
            if "items" in result:
                for item in result["items"]:
                    if "drvrs" in item:  # Есть водители
                        for driver_id, driver_data in item["drvrs"].items():
                            drivers.append({
                                "id": driver_id,
                                "name": driver_data.get("n", ""),
                                "phone": driver_data.get("p", ""),
                                "code": driver_data.get("c", "")
                            })

            logger.info(f"Retrieved {len(drivers)} drivers")
            return drivers

        except Exception as e:
            logger.error(f"Error getting drivers: {e}")
            return []


# Глобальный экземпляр сервиса
wialon_service = WialonService()
