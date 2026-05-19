from beanie import Document
from typing import Optional


class Farmacy(Document):
    fnfnum: Optional[str] = None
    taxon: Optional[str] = None
    chem_id: Optional[str] = None
    chem_name: Optional[str] = None
    part_code: Optional[str] = None
    part_name: Optional[str] = None
    amt_lo: Optional[float] = None
    amt_hi: Optional[float] = None
    reference: Optional[str] = None
    ref_year: Optional[str] = None

    class Settings:
        name = "farmacies"
