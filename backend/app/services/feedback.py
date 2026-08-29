from sqlalchemy.orm import Session
from app.models.domain import TrainingFeedback

class ContinuousLearningStore:
    @staticmethod
    def record_feedback(
        db: Session,
        document_id: int,
        field_name: str,
        original_val: str,
        corrected_val: str,
        source_region: dict,
        verifier_name: str
    ) -> TrainingFeedback:
        feedback = TrainingFeedback(
            document_id=document_id,
            field_name=field_name,
            original_value=original_val,
            corrected_value=corrected_val,
            source_region=source_region,
            verifier_name=verifier_name
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback

feedback_store = ContinuousLearningStore()
