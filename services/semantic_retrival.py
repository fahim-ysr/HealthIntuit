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

class SourceType:
    """Types of medical information sources"""


class MedicalDocuments:
    """Represents a retrived medical document"""


class RetrivalContext:
    """Context information for retrival"""


class SemanticRetrivalService:
    """Medical info retrival with semantic understanding"""