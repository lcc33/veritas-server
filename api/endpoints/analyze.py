from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging

# Use absolute imports
from models.schemas import AnalysisRequest, AnalysisResponse, Claim
from services.claim_extractor import ClaimExtractor
from services.evidence_retriever import EvidenceRetriever
from services.analyzer import Analyzer
from services.cache import AnalysisCache

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
claim_extractor = ClaimExtractor()
evidence_retriever = EvidenceRetriever()
analyzer = Analyzer()
cache = AnalysisCache()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(request: AnalysisRequest):
    """
    Main analysis endpoint for fact-checking content
    """
    try:
        # Check cache first
        cache_key = f"{request.content_type}:{hash(request.content)}"
        cached_result = await cache.get_cached_analysis(cache_key)

        if cached_result:
            logger.info("Returning cached analysis")
            return cached_result

        # Extract claims from content
        claims = claim_extractor.extract_claims(request.content, request.max_claims)

        if not claims:
            raise HTTPException(
                status_code=400, detail="No factual claims found in the content"
            )

        # Analyze each claim
        analysis_results = []
        for claim in claims:
            # Retrieve evidence for the claim
            evidence = await evidence_retriever.retrieve_evidence(claim.text)

            # Analyze claim with evidence
            analysis = await analyzer.analyze_claim(claim.text, evidence)
            analysis_results.append(analysis)

        # Build response
        response = AnalysisResponse(
            claims=analysis_results,
            analyzed_at=datetime.utcnow(),
            source_type=request.content_type,
            total_claims_analyzed=len(analysis_results),
        )

        # Cache the result
        await cache.set_cached_analysis(cache_key, response)

        return response

    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
