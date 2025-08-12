from typing import List, Dict, Any, Tuple, Optional
import requests
import json
from datetime import datetime, timedelta
import re
from dataclasses import dataclass
from enum import Enum
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from config.settings import get_config
from config.languages import get_language_manager

class SourceType(Enum):
    """Types of medical information sources"""
    CLINIC_GUIDELINE = "clinical_guideline"
    PEER_REVIEWED = "peer_reviewed"
    MEDICAL_DATABASE = "medical_database"
    HEALTH_AUTHORITY = "health_authority"
    EDUCATIONAL = "educational"
    NEWS_ARTICLE = "news_article"


class MedicalDocuments:
    """Represents a retrived medical document"""
    title: str
    content: str
    url: str
    source: str
    source_type: SourceType
    publication_date: Optional[datetime]
    credibility_score: float
    relevance_score: float
    regional_relevance: float
    recency_score: float
    final_score: float
    extracted_entities: List[str]
    semantic_concepts: List[str]


class RetrivalContext:
    """Context information for retrival"""
    patient_demographics: Dict[str, Any]
    geographical_region: str
    current_season: str
    image_analysis_results: Dict[str, Any]
    medical_entities: Dict[str, Any]
    urgency_level: str  # "emergency", "urgent", "routine"


class SemanticRetrivalService:
    """Medical info retrival with semantic understanding"""

    def __init__(self):
        self.config = get_config()
        self.lang_manager = get_language_manager()

        try:
            # For semantic search
            self.semantic_model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"Warning: Could not load semantic model: {e}")

        # Source credibility evaluation scores
        self.source_weights = {
            SourceType.CLINICAL_GUIDELINE: 1.0,
            SourceType.HEALTH_AUTHORITY: 0.9,
            SourceType.PEER_REVIEWED: 0.8,
            SourceType.MEDICAL_DATABASE: 0.7,
            SourceType.EDUCATIONAL: 0.5,
            SourceType.NEWS_ARTICLE: 0.3
        }

        # Trusted medical sources
        self.trusted_sources = {
            "pubmed.ncbi.nlm.nih.gov": SourceType.PEER_REVIEWED,
            "canada.ca": SourceType.HEALTH_AUTHORITY,
            "who.int": SourceType.HEALTH_AUTHORITY,
            "mayoclinic.org": SourceType.MEDICAL_DATABASE,
            "uptodate.com": SourceType.CLINICAL_GUIDELINE,
            "cochranelibrary.com": SourceType.PEER_REVIEWED,
            "nejm.org": SourceType.PEER_REVIEWED,
            "bmj.com": SourceType.PEER_REVIEWED,
            "cma.ca": SourceType.HEALTH_AUTHORITY,
            "healthcanada.gc.ca": SourceType.HEALTH_AUTHORITY
        }