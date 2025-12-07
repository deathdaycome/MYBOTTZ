"""
WildBerries Integration Module
Provides integration with WildBerries marketplace API
"""

from .client import WildberriesClient
from .service import WildberriesService

__all__ = ["WildberriesClient", "WildberriesService"]
