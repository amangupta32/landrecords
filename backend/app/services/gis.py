from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.domain import MapFeature

class GISService:
    @staticmethod
    def get_village_cadastral_geojson(db: Session, village: str = "Rampur") -> Dict[str, Any]:
        features_db = db.query(MapFeature).filter(MapFeature.village == village).all()
        
        geojson_features = []
        for feat in features_db:
            geojson_features.append({
                "type": "Feature",
                "id": feat.id,
                "geometry": feat.geometry_geojson,
                "properties": {
                    "land_record_id": feat.land_record_id,
                    "khasra_number": feat.khasra_number,
                    "village": feat.village,
                    "tehsil": feat.tehsil,
                    "district": feat.district,
                    "owner_name": feat.owner_name,
                    "land_area_acres": feat.land_area_acres,
                    "status": feat.status,
                    "center": [feat.center_lat, feat.center_lng]
                }
            })

        return {
            "type": "FeatureCollection",
            "village": village,
            "center": [28.8124, 79.0250],
            "zoom": 15,
            "features": geojson_features
        }

gis_service = GISService()
