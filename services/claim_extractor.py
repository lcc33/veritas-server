from models.schemas import Claim
from typing import List

class ClaimExtractor:
    def extract_claims(self, text: str, max_claims: int = 5) -> List[Claim]:
        """
        Mock claim extraction - to be implemented
        """
        # For now, return simple sentence splitting
        sentences = text.split('.')
        claims = []
        
        for i, sentence in enumerate(sentences[:max_claims]):
            if sentence.strip():
                claims.append(Claim(
                    text=sentence.strip(),
                    start_index=0,
                    end_index=len(sentence)
                ))
        
        return claims