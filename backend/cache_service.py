"""
Servicio de caché para encodings faciales
Evita recargar encodings desde la BD en cada validación
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pickle

class EncodingCache:
    def __init__(self, ttl_minutes: int = 30):
        """
        Args:
            ttl_minutes: Tiempo de vida del caché en minutos
        """
        self._cache: Dict[int, Tuple[object, datetime]] = {}
        self._ttl = timedelta(minutes=ttl_minutes)
    
    def get(self, employee_id: int) -> Optional[object]:
        """Obtiene encoding del caché si existe y no expiró"""
        if employee_id in self._cache:
            encoding, timestamp = self._cache[employee_id]
            if datetime.utcnow() - timestamp < self._ttl:
                return encoding
            else:
                # Expiró, eliminar
                del self._cache[employee_id]
        return None
    
    def set(self, employee_id: int, encoding: object):
        """Guarda encoding en caché"""
        self._cache[employee_id] = (encoding, datetime.utcnow())
    
    def invalidate(self, employee_id: int):
        """Invalida el caché de un empleado específico"""
        if employee_id in self._cache:
            del self._cache[employee_id]
    
    def clear(self):
        """Limpia todo el caché"""
        self._cache.clear()
    
    def get_stats(self) -> dict:
        """Retorna estadísticas del caché"""
        return {
            'size': len(self._cache),
            'ttl_minutes': self._ttl.total_seconds() / 60
        }

# Instancia global del caché
encoding_cache = EncodingCache(ttl_minutes=30)
