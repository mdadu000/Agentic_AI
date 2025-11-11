import requests
from typing import Dict
from services.service import Service
from repos.repo import Repo
from constants import DB_NAME

# Create repo and service instances
repo = Repo(DB_NAME)
service = Service(repo)

async def get_all_restaurants() -> dict:
    """Retrieve all available restaurants."""
    return await service.get_all_restaurants()
