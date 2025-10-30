from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.services.forecasting_service import ForecastingService

router = APIRouter(prefix="/api/forecast", tags=["forecast"])

class ForecastController:
    def __init__(self, forecasting_service: ForecastingService):
        self.forecasting_service = forecasting_service
