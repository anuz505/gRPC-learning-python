from pydantic import BaseModel, Field
from datetime import datetime


class HealthCheckResponse(BaseModel):
    status: str = Field(default="healthy")
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = Field(description="API version")
    services: dict[str, str] = Field(default_factory=dict, description="Service Status check")
