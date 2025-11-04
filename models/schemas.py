from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum

class ContentType(str, Enum):
    TEXT = "text"
    URL = "url"

class Verdict(str, Enum):
    SUPPORTED = "supported"
    DISPUTED = "disputed"
    UNCLEAR = "unclear"

# Request Models
class AnalysisRequest(BaseModel):
    content: str
    content_type: ContentType = ContentType.TEXT
    max_claims: int = 5

# Claim Model - ADD THIS
class Claim(BaseModel):
    text: str
    start_index: Optional[int] = None
    end_index: Optional[int] = None

# Evidence Models
class EvidenceSource(BaseModel):
    name: str
    url: Optional[HttpUrl] = None
    excerpt: str
    credibility_score: Optional[float] = None

# Analysis Models
class ClaimAnalysis(BaseModel):
    claim_text: str
    verdict: Verdict
    confidence: float  # 0-100
    rationale: str
    sources: List[EvidenceSource]
    analysis_timestamp: datetime

class AnalysisResponse(BaseModel):
    claims: List[ClaimAnalysis]
    analyzed_at: datetime
    source_type: ContentType
    total_claims_analyzed: int