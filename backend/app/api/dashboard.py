from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.domain import Document, LandRecord, DuplicateCandidate, ConflictRecord, AuditLog

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_analytics(db: Session = Depends(get_db)):
    total_docs = db.query(Document).count()
    total_records = db.query(LandRecord).count()
    verified_records = db.query(LandRecord).filter(LandRecord.verification_status == "Verified").count()
    pending_records = db.query(LandRecord).filter(LandRecord.verification_status.in_(["Pending", "LowConfidence"])).count()
    flagged_records = db.query(LandRecord).filter(LandRecord.verification_status == "Flagged").count()
    rejected_records = db.query(LandRecord).filter(LandRecord.verification_status == "Rejected").count()
    
    total_dups = db.query(DuplicateCandidate).filter(DuplicateCandidate.status == "Pending").count()
    active_conflicts = db.query(ConflictRecord).filter(ConflictRecord.status == "Active").count()

    all_records = db.query(LandRecord).all()
    avg_conf = round(sum(r.overall_confidence for r in all_records) / len(all_records), 2) if all_records else 0.85

    # Confidence distribution histogram
    conf_dist = [
        {"range": "< 60%", "count": sum(1 for r in all_records if r.overall_confidence < 0.60)},
        {"range": "60% - 75%", "count": sum(1 for r in all_records if 0.60 <= r.overall_confidence < 0.75)},
        {"range": "75% - 90%", "count": sum(1 for r in all_records if 0.75 <= r.overall_confidence < 0.90)},
        {"range": "> 90%", "count": sum(1 for r in all_records if r.overall_confidence >= 0.90)},
    ]

    # Verification status pie chart
    status_counts = [
        {"name": "Verified", "value": verified_records, "color": "#10b981"},
        {"name": "Pending Verification", "value": pending_records, "color": "#f59e0b"},
        {"name": "Flagged (Conflict)", "value": flagged_records, "color": "#ef4444"},
        {"name": "Rejected", "value": rejected_records, "color": "#6b7280"},
    ]

    # District progress bar chart
    district_progress = [
        {"district": "Rampur District", "digitized": 1420, "pending": 180, "rate": "88.7%"},
        {"district": "Lucknow District", "digitized": 3100, "pending": 240, "rate": "92.8%"},
        {"district": "Indore District", "digitized": 2250, "pending": 310, "rate": "87.8%"},
        {"district": "Nagpur District", "digitized": 1890, "pending": 420, "rate": "81.8%"},
    ]

    # Audit logs preview
    audit_logs = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(10).all()

    return {
        "metrics": {
            "total_uploaded_documents": total_docs,
            "total_land_records": total_records,
            "verified_records": verified_records,
            "pending_verification": pending_records,
            "flagged_conflicts": flagged_records,
            "duplicate_candidates": total_dups,
            "active_conflicts": active_conflicts,
            "average_confidence": avg_conf
        },
        "confidence_distribution": conf_dist,
        "status_distribution": status_counts,
        "district_progress": district_progress,
        "recent_audit_logs": audit_logs
    }
