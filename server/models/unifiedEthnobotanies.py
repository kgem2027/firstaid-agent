from beanie import Document
from typing import Optional


class UnifiedEthnobotany(Document):
    region: str  # "African" | "European" | "Chinese" | "Indian" | "North American"

    # Name fields
    latin_name: Optional[str] = None
    common_name: Optional[str] = None

    # Plant part to use (Indian: part_used, Chinese: UsePart)
    part_used: Optional[str] = None

    # Preparation process (Chinese: tcmwiki_processing)
    preparation: Optional[str] = None

    # Region-specific therapeutic fields
    health_problems: Optional[str] = None   # African
    therapeutic_area: Optional[str] = None  # European
    therapeutic_uses: Optional[str] = None  # Indian
    function: Optional[str] = None          # Chinese
    tcmwiki_actions: Optional[str] = None   # Chinese

    # Dosage
    dose: Optional[str] = None              # Indian
    tcmwiki_dosage: Optional[str] = None    # Chinese

    # North American
    use_type: Optional[str] = None
    category: Optional[str] = None

    # Shared
    description: Optional[str] = None
    embedding: Optional[list[float]] = None

    class Settings:
        name = "Unified Ethnobotanies"
