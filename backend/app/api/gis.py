from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.gis import gis_service

router = APIRouter(prefix="/gis", tags=["GIS"])

@router.get("/map-features")
def get_cadastral_map_features(village: str = Query("Rampur"), db: Session = Depends(get_db)):
    return gis_service.get_village_cadastral_geojson(db, village)
