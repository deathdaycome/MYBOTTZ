"""
Timeweb Cloud API Integration Service
Handles communication with Timeweb Cloud API for server management
"""

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class TimewebService:
    """Service for interacting with Timeweb Cloud API"""

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize Timeweb service

        Args:
            api_token: Timeweb Cloud API token (Bearer token)
                      If not provided, will try to get from TIMEWEB_API_TOKEN env var
        """
        self.api_token = api_token or os.getenv("TIMEWEB_API_TOKEN")
        self.base_url = "https://api.timeweb.cloud/api/v1"

        if not self.api_token:
            logger.warning("Timeweb API token not configured")

        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        Make HTTP request to Timeweb API with error handling

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for httpx request

        Returns:
            Response JSON data

        Raises:
            httpx.HTTPError: On request failure
        """
        url = f"{self.base_url}{endpoint}"

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"Timeweb API error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Timeweb API request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling Timeweb API: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_servers(self) -> List[Dict]:
        """
        Get list of all servers from Timeweb Cloud

        Returns:
            List of server objects with details

        Example response structure:
        {
            "servers": [
                {
                    "id": 123456,
                    "name": "my-server",
                    "status": "on",
                    "os": {"name": "Ubuntu", "version": "22.04"},
                    "cpu": 2,
                    "ram": 2048,
                    "disks": [{"size": 25600}],
                    "networks": [{"ips": [{"ip": "1.2.3.4", "is_main": true}]}],
                    "preset_id": 1,
                    "created_at": "2024-01-01T00:00:00Z"
                }
            ],
            "meta": {"total": 10}
        }
        """
        try:
            logger.info("Fetching servers from Timeweb Cloud")
            response = self._make_request("GET", "/servers")

            servers = response.get("servers", [])
            total = response.get("meta", {}).get("total", len(servers))

            logger.info(f"Successfully fetched {total} servers from Timeweb")
            return servers

        except Exception as e:
            logger.error(f"Failed to fetch servers from Timeweb: {str(e)}")
            return []

    async def get_server_details(self, server_id: int) -> Optional[Dict]:
        """
        Get detailed information about specific server

        Args:
            server_id: Timeweb server ID

        Returns:
            Server details or None if not found
        """
        try:
            logger.info(f"Fetching server details for ID {server_id}")
            response = self._make_request("GET", f"/servers/{server_id}")

            server = response.get("server")
            if server:
                logger.info(f"Successfully fetched details for server {server_id}")

            return server

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Server {server_id} not found in Timeweb")
                return None
            raise
        except Exception as e:
            logger.error(f"Failed to fetch server {server_id}: {str(e)}")
            return None

    async def get_account_finances(self) -> Optional[Dict]:
        """
        Get account balance and payment information

        Returns:
            Finance data with balance and payment info

        Example response:
        {
            "finances": {
                "balance": 1000.50,
                "currency": "RUB",
                "discount_end_date_at": "2024-12-31T23:59:59Z"
            }
        }
        """
        try:
            logger.info("Fetching account finances from Timeweb")
            response = self._make_request("GET", "/account/finances")

            finances = response.get("finances")
            if finances:
                logger.info(f"Account balance: {finances.get('balance')} {finances.get('currency')}")

            return finances

        except Exception as e:
            logger.error(f"Failed to fetch finances: {str(e)}")
            return None

    async def get_presets(self) -> List[Dict]:
        """
        Get available server presets (tariffs/configurations)

        Returns:
            List of preset configurations with pricing

        Example response:
        {
            "presets": [
                {
                    "id": 1,
                    "description": "2 CPU, 2 GB RAM, 25 GB SSD",
                    "price": 299.00,
                    "cpu": 2,
                    "ram": 2048,
                    "disk": 25600
                }
            ]
        }
        """
        try:
            logger.info("Fetching server presets from Timeweb")
            response = self._make_request("GET", "/presets/servers")

            presets = response.get("server_presets", [])  # API возвращает server_presets, не presets
            logger.info(f"Successfully fetched {len(presets)} presets")

            return presets

        except Exception as e:
            logger.error(f"Failed to fetch presets: {str(e)}")
            return []

    def parse_server_configuration(self, server: Dict) -> str:
        """
        Parse server data into human-readable configuration string

        Args:
            server: Server object from API

        Returns:
            Configuration string (e.g., "2 CPU / 2GB RAM / 25GB SSD")
        """
        try:
            cpu = server.get("cpu", 0)
            ram_mb = server.get("ram", 0)
            ram_gb = ram_mb / 1024 if ram_mb else 0

            # Get disk size (sum of all disks)
            disks = server.get("disks", [])
            total_disk_mb = sum(disk.get("size", 0) for disk in disks)
            disk_gb = total_disk_mb / 1024 if total_disk_mb else 0

            config = f"{cpu} CPU / {ram_gb:.0f}GB RAM / {disk_gb:.0f}GB SSD"

            # Add OS info if available
            os_info = server.get("os", {})
            if os_info:
                os_name = os_info.get("name", "")
                os_version = os_info.get("version", "")
                if os_name:
                    config += f" / {os_name}"
                    if os_version:
                        config += f" {os_version}"

            return config

        except Exception as e:
            logger.error(f"Error parsing server configuration: {str(e)}")
            return "Unknown configuration"

    def get_primary_ip(self, server: Dict) -> Optional[str]:
        """
        Extract primary IPv4 address from server data

        Args:
            server: Server object from API

        Returns:
            Primary IP address or None
        """
        try:
            networks = server.get("networks", [])
            for network in networks:
                ips = network.get("ips", [])
                for ip_obj in ips:
                    if ip_obj.get("is_main") and "." in ip_obj.get("ip", ""):
                        return ip_obj.get("ip")

            # Fallback: return first IPv4 found
            for network in networks:
                ips = network.get("ips", [])
                for ip_obj in ips:
                    ip = ip_obj.get("ip", "")
                    if "." in ip:  # Simple IPv4 check
                        return ip

            return None

        except Exception as e:
            logger.error(f"Error extracting IP address: {str(e)}")
            return None

    async def get_preset_price(self, preset_id: int) -> Optional[float]:
        """
        Get price for specific preset/tariff

        Args:
            preset_id: Preset ID from server

        Returns:
            Monthly price in rubles or None
        """
        try:
            presets = await self.get_presets()
            for preset in presets:
                if preset.get("id") == preset_id:
                    return preset.get("price")

            logger.warning(f"Preset {preset_id} not found")
            return None

        except Exception as e:
            logger.error(f"Error fetching preset price: {str(e)}")
            return None

    async def get_configurators(self) -> List[Dict]:
        """
        Get available server configurators with pricing

        Returns:
            List of configurator objects with pricing info
        """
        try:
            logger.info("Fetching server configurators from Timeweb")
            response = self._make_request("GET", "/configurator/servers")

            configurators = response.get("server_configurators", [])
            logger.info(f"Successfully fetched {len(configurators)} configurators")

            return configurators

        except Exception as e:
            logger.error(f"Failed to fetch configurators: {str(e)}")
            return []

    async def get_configurator_price(self, configurator_id: int, server: Dict) -> Optional[float]:
        """
        Calculate price for custom configured server

        Args:
            configurator_id: Configurator ID from server
            server: Server object with cpu, ram, disk specifications

        Returns:
            Monthly price in rubles or None
        """
        try:
            configurators = await self.get_configurators()

            # Find the configurator
            configurator = None
            for conf in configurators:
                if conf.get("id") == configurator_id:
                    configurator = conf
                    break

            if not configurator:
                logger.warning(f"Configurator {configurator_id} not found")
                return None

            prices = configurator.get("prices", {})

            # Get server specifications
            cpu = server.get("cpu", 0)
            ram_mb = server.get("ram", 0)
            ram_gb = ram_mb / 1024 if ram_mb else 0

            # Calculate total disk size
            disks = server.get("disks", [])
            total_disk_mb = sum(disk.get("size", 0) for disk in disks)
            disk_gb = total_disk_mb / 1024 if total_disk_mb else 0

            # Calculate price
            cpu_price = cpu * prices.get("cpu", 0)
            ram_price = ram_gb * prices.get("ram", 0)
            disk_price = disk_gb * prices.get("disk", 0)

            total_price = cpu_price + ram_price + disk_price

            logger.info(f"Calculated price for configurator {configurator_id}: "
                       f"{cpu} CPU (${cpu_price}) + {ram_gb:.1f}GB RAM (${ram_price}) + "
                       f"{disk_gb:.1f}GB Disk (${disk_price}) = ${total_price}")

            return total_price

        except Exception as e:
            logger.error(f"Error calculating configurator price: {str(e)}")
            return None

    async def get_server_price(self, server: Dict) -> Optional[float]:
        """
        Get monthly price for server (works for both preset and custom configured servers)

        Args:
            server: Server object from API

        Returns:
            Monthly price in rubles or None
        """
        try:
            preset_id = server.get("preset_id")
            configurator_id = server.get("configurator_id")

            if preset_id:
                # Standard preset-based server
                return await self.get_preset_price(preset_id)
            elif configurator_id:
                # Custom configured server
                return await self.get_configurator_price(configurator_id, server)
            else:
                logger.warning(f"Server {server.get('id')} has no preset_id or configurator_id")
                return None

        except Exception as e:
            logger.error(f"Error getting server price: {str(e)}")
            return None

    def is_configured(self) -> bool:
        """
        Check if service is properly configured with API token

        Returns:
            True if API token is set
        """
        return bool(self.api_token)


# Global instance
timeweb_service = TimewebService()
