"""End-to-End Demo runner script for Land Record AI Pipeline."""

import os
import sys
from pathlib import Path
import json
import cv2
import numpy as np

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pipeline import LandRecordAIPipeline


def create_sample_land_record_image(output_path: Path) -> Path:
    """Generate a realistic synthetic land record document for demonstration."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    h, w = 900, 1200
    canvas = np.full((h, w, 3), 245, dtype=np.uint8)

    # Add document header and boundary box
    cv2.rectangle(canvas, (40, 40), (w - 40, h - 40), (40, 40, 40), 2)
    cv2.rectangle(canvas, (45, 45), (w - 45, 120), (60, 60, 60), 1)

    # Text headers
    cv2.putText(canvas, "UTTAR PRADESH REVENUE DEPARTMENT - RECORD OF RIGHTS", (160, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (20, 20, 20), 2)
    cv2.putText(canvas, "(JAMABANDI / KHATAUNI - FORM 45)", (420, 115),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 50, 50), 1)

    # Table layout lines
    cv2.line(canvas, (45, 180), (w - 45, 180), (40, 40, 40), 2)
    cv2.line(canvas, (45, 230), (w - 45, 230), (40, 40, 40), 1)
    cv2.line(canvas, (45, 550), (w - 45, 550), (40, 40, 40), 2)

    # Table columns
    cv2.putText(canvas, "Khata No.", (60, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 20), 2)
    cv2.putText(canvas, "Khasra / Survey No.", (200, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 20), 2)
    cv2.putText(canvas, "Tenure Holder / Owner", (480, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 20), 2)
    cv2.putText(canvas, "Area (Acre)", (820, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 20), 2)
    cv2.putText(canvas, "Mutation No.", (1000, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 20), 2)

    # Row data
    cv2.putText(canvas, "00089", (60, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (10, 10, 10), 2)
    cv2.putText(canvas, "245/1", (200, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (10, 10, 10), 2)
    cv2.putText(canvas, "RAMESH KUMAR SHARMA S/O HARISH CHANDRA SHARMA", (480, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (10, 10, 10), 2)
    cv2.putText(canvas, "4.25 Acre", (820, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (10, 10, 10), 2)
    cv2.putText(canvas, "MUT-2023-882", (1000, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (10, 10, 10), 2)

    # Location footer
    cv2.putText(canvas, "Village: Rampur | Tehsil: Rampur Tehsil | District: Rampur District | State: Uttar Pradesh",
                (60, 600), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (30, 30, 30), 2)
    cv2.putText(canvas, "Date of Verification: 15/01/2024", (60, 640),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (30, 30, 30), 2)

    # Introduce a slight realistic skew (1.5 degrees)
    center = (w // 2, h // 2)
    rot_mat = cv2.getRotationMatrix2D(center, 1.5, 1.0)
    skewed = cv2.warpAffine(canvas, rot_mat, (w, h), borderValue=(250, 250, 250))

    cv2.imwrite(str(output_path), skewed)
    return output_path


def main():
    print("=" * 80)
    print(" LAND RECORD AI - FULL END-TO-END PIPELINE DEMONSTRATION")
    print("=" * 80)

    # Step 1: Create sample image
    sample_path = Path("./data/raw/sample_khasra_doc.png")
    print(f"\n[1] Preparing synthetic land record document at: {sample_path}")
    create_sample_land_record_image(sample_path)

    # Step 2: Initialize LandRecordAIPipeline
    print("[2] Initializing LandRecordAIPipeline (OpenCV + Multi-Engine OCR + Hybrid NLP + Validation + Explainable Scorer)...")
    pipeline = LandRecordAIPipeline(save_debug_artifacts=True)

    # Step 3: Execute full pipeline
    print("[3] Executing full digitization pipeline...")
    output = pipeline.process(
        image=str(sample_path),
        document_id="demo_jamabandi_up_01"
    )

    # Step 4: Display results
    print("\n" + "=" * 80)
    print(" PIPELINE EXECUTION OUTPUT")
    print("=" * 80)
    print(f"  • Document ID        : {output.document_id}")
    print(f"  • Processing Latency : {output.processing_time_ms} ms")
    print(f"  • Quality Grade      : {output.document_quality.quality.upper()} (Laplacian blur variance: {output.document_quality.laplacian_variance:.1f})")
    print(f"  • OCR Engine Used    : {output.ocr.primary_engine} (Confidence: {output.ocr.average_confidence * 100:.1f}%)")
    print(f"  • Overall Confidence : {output.confidence.overall * 100:.1f}% [TIER: {output.confidence.tier.value}]")
    print(f"  • Human Review Needed: {output.needs_human_review}")

    print("\n" + "-" * 80)
    print(" EXTRACTED STRUCTURED FIELDS")
    print("-" * 80)
    if output.fields.khasra_numbers:
        k = output.fields.khasra_numbers[0]
        print(f"  • Khasra / Survey No.: {k.value} (Confidence: {k.confidence * 100:.1f}%, BBox: {k.bbox})")
    if output.fields.khata_numbers:
        kh = output.fields.khata_numbers[0]
        print(f"  • Khata Account No.  : {kh.value} (Confidence: {kh.confidence * 100:.1f}%, BBox: {kh.bbox})")
    if output.fields.owner_names:
        o = output.fields.owner_names[0]
        print(f"  • Owner / Khatedar   : {o.name} [Relation: {o.relation_type or 'N/A'} {o.relation_name or ''}]")
    if output.fields.land_area.value is not None:
        a = output.fields.land_area
        print(f"  • Land Area          : {a.value} {a.unit} (Confidence: {a.confidence * 100:.1f}%)")
    loc = output.fields.location
    print(f"  • Location Hierarchy : Village {loc.village} -> Tehsil {loc.tehsil} -> District {loc.district} -> State {loc.state}")
    if output.fields.mutation_reference:
        m = output.fields.mutation_reference
        print(f"  • Mutation Reference : {m.mutation_number}")
    if output.fields.record_date:
        d = output.fields.record_date
        print(f"  • Record Date (ISO)  : {d.iso_date} (Raw: {d.raw_date})")

    print("\n" + "-" * 80)
    print(" 4-TIER EXPLAINABLE CONFIDENCE BREAKDOWN")
    print("-" * 80)
    for field_name, detail in output.field_confidences.items():
        c = detail.components
        print(f"  [{field_name.upper()}]: Score = {detail.score * 100:.1f}% ({detail.tier.value})")
        print(f"     Components: OCR={c.ocr * 100:.1f}% (40%), Extraction={c.extraction * 100:.1f}% (30%), Validation={c.validation * 100:.1f}% (20%), Context={c.context * 100:.1f}% (10%)")
        for reason in detail.reasons:
            print(f"     -> {reason}")

    print("\n" + "-" * 80)
    print(" SYSTEM EXPLANATIONS & AUDIT LOG")
    print("-" * 80)
    for exp in output.explanations:
        print(f"  * {exp}")

    print("\n" + "=" * 80)
    print(" DEMO EXECUTION COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()
