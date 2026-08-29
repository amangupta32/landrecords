import difflib
from typing import List, Dict, Any

class DuplicateDetector:
    @staticmethod
    def calculate_similarity(s1: str, s2: str) -> float:
        if not s1 or not s2:
            return 0.0
        s1_clean = s1.lower().replace(".", "").strip()
        s2_clean = s2.lower().replace(".", "").strip()
        return round(difflib.SequenceMatcher(None, s1_clean, s2_clean).ratio(), 2)

    def find_duplicates(self, record: dict, existing_records: List[dict]) -> List[dict]:
        duplicates = []
        rec_owner = record.get("owner_name", "")
        rec_khasra = record.get("khasra_number", "")
        rec_village = record.get("village", "")

        for ext in existing_records:
            if ext.get("id") == record.get("id"):
                continue

            sim_owner = self.calculate_similarity(rec_owner, ext.get("owner_name", ""))
            same_khasra = (rec_khasra.split("/")[0] == ext.get("khasra_number", "").split("/")[0])
            same_village = (rec_village.lower() == ext.get("village", "").lower())

            if same_khasra and same_village and sim_owner >= 0.75:
                duplicates.append({
                    "record_id_1": record.get("id"),
                    "record_id_2": ext.get("id"),
                    "owner_1": rec_owner,
                    "owner_2": ext.get("owner_name"),
                    "khasra_number": rec_khasra,
                    "village": rec_village,
                    "similarity_score": sim_owner,
                    "duplicate_reason": f"High name similarity ({int(sim_owner * 100)}%) for Khasra {rec_khasra} in {rec_village}.",
                    "status": "Pending"
                })
        return duplicates

class CrossDocumentConflictEngine:
    def detect_conflicts(self, khasra_number: str, village: str, records: List[dict]) -> Dict[str, Any]:
        """
        Cross-references records sharing the same Khasra & Village to find ownership mismatches or area discrepancies.
        Generates interactive graph nodes and edges payload.
        """
        conflicts = []
        
        # Filter matching plot records
        plot_recs = [r for r in records if r.get("village", "").lower() == village.lower() and r.get("khasra_number", "").split("/")[0] == khasra_number.split("/")[0]]

        if len(plot_recs) >= 2:
            owners = set([r.get("owner_name") for r in plot_recs if r.get("owner_name")])
            areas = [r.get("land_area") for r in plot_recs if r.get("land_area")]

            if len(owners) > 1:
                conflicts.append({
                    "khasra_number": khasra_number,
                    "village": village,
                    "doc_1_title": plot_recs[0].get("document_title", "Jamabandi_2024.pdf"),
                    "doc_2_title": plot_recs[1].get("document_title", "SaleDeed_2023.png"),
                    "conflict_type": "Ownership Mismatch",
                    "description": f"Conflicting owners detected across documents: '{list(owners)[0]}' vs '{list(owners)[1]}'.",
                    "severity": "Critical",
                    "status": "Active"
                })

            if len(areas) >= 2 and abs(areas[0] - areas[1]) > 0.05:
                conflicts.append({
                    "khasra_number": khasra_number,
                    "village": village,
                    "doc_1_title": plot_recs[0].get("document_title", "Jamabandi_2024.pdf"),
                    "doc_2_title": plot_recs[1].get("document_title", "SaleDeed_2023.png"),
                    "conflict_type": "Area Discrepancy",
                    "description": f"Discrepancy in recorded plot land area: {areas[0]} Acres vs {areas[1]} Acres.",
                    "severity": "High",
                    "status": "Active"
                })

        # Generate Visual Network Graph Payload
        nodes = [
            {"id": f"plot_{khasra_number}", "label": f"Plot Khasra {khasra_number}", "type": "plot", "color": "#ef4444" if conflicts else "#10b981"},
        ]
        edges = []

        for idx, r in enumerate(plot_recs):
            doc_id = f"doc_{r.get('id', idx)}"
            owner_id = f"owner_{idx}"
            
            nodes.append({"id": doc_id, "label": r.get("document_type", f"Doc #{idx+1}"), "type": "document", "color": "#3b82f6"})
            nodes.append({"id": owner_id, "label": r.get("owner_name", "Unknown"), "type": "owner", "color": "#8b5cf6"})

            edges.append({"source": doc_id, "target": f"plot_{khasra_number}", "label": "References", "status": "active"})
            edges.append({"source": owner_id, "target": doc_id, "label": "Claimant", "status": "active"})
            
            if conflicts:
                edges.append({"source": f"owner_0", "target": f"owner_1", "label": "Ownership Conflict", "status": "conflict"})

        return {
            "conflicts": conflicts,
            "graph_payload": {
                "nodes": nodes,
                "edges": edges
            }
        }

duplicate_detector = DuplicateDetector()
conflict_engine = CrossDocumentConflictEngine()
