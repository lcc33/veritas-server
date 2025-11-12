from datetime import datetime
from typing import List
import json
import logging
from models.schemas import ClaimAnalysis, Verdict, EvidenceSource
from services.llm.factory import LLMFactory

logger = logging.getLogger(__name__)

class Analyzer:
    def __init__(self):
        try:
            self.llm = LLMFactory.create_gemini_client()
            if self.llm:
                logger.info("Gemini LLM initialized successfully")
            else:
                logger.warning("Gemini LLM not available, check API key")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.llm = None
    
    async def analyze_claim(self, claim: str, evidence: List[EvidenceSource]) -> ClaimAnalysis:
        """
        Real analysis using Gemini LLM
        """
        try:
            # If LLM is not available, fall back to basic analysis
            if not self.llm:
                return self._fallback_analysis(claim, evidence)
            
            # Build the analysis prompt
            prompt = self._build_analysis_prompt(claim, evidence)
            
            # Define the expected response format
            response_format = {
                "verdict": "supported|disputed|unclear",
                "confidence": 0.85,
                "rationale": "Brief explanation based on the evidence...",
                "relevant_source_indices": [0, 1]  # indices of most relevant evidence
            }
            
            # Get structured response from Gemini
            llm_response = self.llm.generate_structured(prompt, response_format)
            
            # Process and validate the response
            analysis_result = self._process_llm_response(claim, evidence, llm_response)
            
            logger.info(f"Analysis complete: {analysis_result.verdict} with {analysis_result.confidence}% confidence")
            return analysis_result
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}, falling back to basic analysis")
            return self._fallback_analysis(claim, evidence)
    
    def _build_analysis_prompt(self, claim: str, evidence: List[EvidenceSource]) -> str:
        """Build the prompt for fact-checking analysis"""
        
        evidence_text = "\n".join([
            f"[Source {i+1}: {source.name}]\n{source.excerpt}\nCredibility: {source.credibility_score or 'N/A'}\n"
            for i, source in enumerate(evidence)
        ])
        
        prompt = f"""
        CLAIM TO ANALYZE: "{claim}"

        AVAILABLE EVIDENCE:
        {evidence_text}

        INSTRUCTIONS:
        1. Determine if the evidence SUPPORTS, DISPUTES, or if it's UNCLEAR regarding the claim
        2. Consider source credibility, evidence consistency, and factual accuracy
        3. If evidence is conflicting or insufficient, return "unclear"
        4. Provide a confidence score from 0-100 based on evidence strength
        5. Write a clear rationale explaining your reasoning
        6. Identify which evidence sources are most relevant (by index)

        CRITERIA:
        - SUPPORTED: Multiple credible sources confirm the claim
        - DISPUTED: Credible evidence directly contradicts the claim  
        - UNCLEAR: Insufficient, conflicting, or low-quality evidence

        Focus only on the provided evidence. Do not use external knowledge.
        """
        
        return prompt
    
    def _process_llm_response(self, claim: str, evidence: List[EvidenceSource], llm_response: dict) -> ClaimAnalysis:
        """Process and validate the LLM response"""
        
        # Validate required fields
        required_fields = ['verdict', 'confidence', 'rationale', 'relevant_source_indices']
        for field in required_fields:
            if field not in llm_response:
                raise ValueError(f"Missing required field in LLM response: {field}")
        
        # Validate verdict
        verdict_str = llm_response['verdict'].lower().strip()
        if verdict_str == 'supported':
            verdict = Verdict.SUPPORTED
        elif verdict_str == 'disputed':
            verdict = Verdict.DISPUTED
        elif verdict_str == 'unclear':
            verdict = Verdict.UNCLEAR
        else:
            logger.warning(f"Invalid verdict: {verdict_str}, defaulting to UNCLEAR")
            verdict = Verdict.UNCLEAR
        
        # Validate confidence score
        confidence = float(llm_response['confidence'])
        if confidence < 0 or confidence > 100:
            logger.warning(f"Confidence {confidence} out of range, clamping to 0-100")
            confidence = max(0, min(100, confidence))
        
        # Get relevant sources
        relevant_indices = llm_response.get('relevant_source_indices', [])
        relevant_sources = []
        for idx in relevant_indices:
            if 0 <= idx < len(evidence):
                relevant_sources.append(evidence[idx])
        
        # If no relevant sources specified, use all evidence
        if not relevant_sources:
            relevant_sources = evidence
        
        return ClaimAnalysis(
            claim_text=claim,
            verdict=verdict,
            confidence=confidence,
            rationale=llm_response['rationale'],
            sources=relevant_sources,
            analysis_timestamp=datetime.utcnow()
        )
    
    def _fallback_analysis(self, claim: str, evidence: List[EvidenceSource]) -> ClaimAnalysis:
        """Fallback analysis when LLM is unavailable"""
        logger.info("Using fallback analysis")
        
        if not evidence:
            evidence = [
                EvidenceSource(
                    name="Fallback Source",
                    url=None,
                    excerpt="Evidence retrieval unavailable.",
                    credibility_score=0.3
                )
            ]
        
        # Simple heuristic-based fallback
        claim_lower = claim.lower()
        controversial_terms = ['cure', 'miracle', 'conspiracy', 'hidden truth', 'they do not want you to know']
        
        if any(term in claim_lower for term in controversial_terms):
            verdict = Verdict.DISPUTED
            confidence = 60.0
            rationale = "Claim contains language patterns associated with misinformation."
        else:
            verdict = Verdict.UNCLEAR
            confidence = 40.0
            rationale = "Insufficient evidence available for proper analysis."
        
        return ClaimAnalysis(
            claim_text=claim,
            verdict=verdict,
            confidence=confidence,
            rationale=rationale,
            sources=evidence,
            analysis_timestamp=datetime.utcnow()
        )