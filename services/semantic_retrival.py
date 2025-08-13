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


class MedicalDocument:
    """Represents a retrieved medical document"""
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


class RetrievalContext:
    """Context information for retreival"""
    patient_demographics: Dict[str, Any]
    geographical_region: str
    current_season: str
    image_analysis_results: Dict[str, Any]
    medical_entities: Dict[str, Any]
    urgency_level: str  # "emergency", "urgent", "routine"


class SemanticRetrievalService:
    """Medical info retrieval with semantic understanding"""


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


    def retrieve_medical_information(self, queries: List[str], context: RetrievalContext, max_results: int = 20) -> List[MedicalDocument]:
        """Retrieval function with semantic understanding"""

        try:
            all_documents = []
            
            for query in queries:
                # Step 1: Searches multiple sources
                raw_results = self._search_multiple_sources(query, max_results_per_source=5)
                
                # Step 2: Extracts medical entities from results
                enriched_results = self._extract_medical_entities_from_results(raw_results, context)
                
                # Step 3: Calculates semantic similarity
                semantic_results = self._calculate_semantic_similarity(enriched_results, query, context)
                
                # Step 4: Applies evaluation scoring
                scored_results = self._apply_intelligent_scoring(semantic_results, context)
                
                all_documents.extend(scored_results)
            
            # Step 5: Removes duplicates and rank by final score
            unique_documents = self._remove_duplicates_and_rank(all_documents)
            
            # Step 6: Applies context-aware filtering
            filtered_documents = self._apply_context_filtering(unique_documents, context)
            
            return filtered_documents[:max_results]
            
        except Exception as e:
            print(f"Retrieval error: {str(e)}")
            return []
        
    
    def _search_multiple_sources(self, query: str, max_results_per_source: int = 5)  -> List[Dict[str, Any]]:
        """Searches multiple medical databases and sources"""
        results = []
        
        # PubMed
        pubmed_results = self._search_pubmed(query, max_results_per_source)
        results.extend(pubmed_results)
        
        # Google Scholar for recent papers
        scholar_results = self._search_google_scholar(query, max_results_per_source)
        results.extend(scholar_results)
        
        # Health Canada and WHO
        authority_results = self._search_health_authorities(query, max_results_per_source)
        results.extend(authority_results)
        
        # Medical database
        database_results = self._search_medical_databases(query, max_results_per_source)
        results.extend(database_results)
        
        return results
    

    def _search_pubmed(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Searches PubMed"""
        try:
            # PubMed eSearch
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "json",
                "sort": "relevance"
            }
            
            response = requests.get(search_url, params=search_params, timeout=10)
            if response.status_code != 200:
                return []
            
            search_data = response.json()
            pmids = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not pmids:
                return []
            
            # Get article details
            fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "xml"
            }
            
            fetch_response = requests.get(fetch_url, params=fetch_params, timeout=15)
            if fetch_response.status_code != 200:
                return []
            
            # Parse XML and extract information
            results = self._parse_pubmed_xml(fetch_response.text, pmids)
            return results
            
        except Exception as e:
            print(f"PubMed search error: {e}")
            return []
    

    def _search_google_scholar(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Searches Google Scholar for recent medical literature"""
        try:
            # Note: This is a simplified implementation
            # In production, use proper Google Scholar API or serpapi
            
            # For now, return mock results with realistic structure
            mock_results = []
            
            # This would be replaced with actual Google Scholar API calls
            scholar_query = f"{query} medical research recent"
            
            # Mock some recent research results
            current_year = datetime.now().year
            for i in range(min(3, max_results)):
                mock_results.append({
                    "title": f"Recent research on {query.split()[0]} - Study {i+1}",
                    "content": f"Abstract discussing {query} with recent findings...",
                    "url": f"https://scholar.google.com/mock_{i}",
                    "source": "Google Scholar",
                    "publication_date": datetime(current_year - i, 6, 15),
                    "source_type": SourceType.PEER_REVIEWED
                })
            
            return mock_results
            
        except Exception as e:
            print(f"Google Scholar search error: {e}")
            return []
        

    def _search_health_authorities(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Searches health authority websites (Canada and WHO)"""
        try:
            results = []
            
            # Health Canada search
            hc_results = self._search_health_canada(query, max_results // 2)
            results.extend(hc_results)
            
            # WHO search
            who_results = self._search_who(query, max_results // 2)
            results.extend(who_results)
            
            return results
            
        except Exception as e:
            print(f"Health authority search error: {e}")
            return []
        

    def _search_health_canada(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Searches Health Canada website"""
        try:
            # Mock Health Canada results
            # In production, implement actual Health Canada API or web scraping
            results = []
            
            canadian_topics = [
                "Canadian treatment guidelines",
                "Health Canada recommendations", 
                "Canadian medical protocols"
            ]
            
            for i, topic in enumerate(canadian_topics[:max_results]):
                results.append({
                    "title": f"{topic} for {query.split()[0]}",
                    "content": f"Health Canada guidance on {query}...",
                    "url": f"https://canada.ca/health/mock_{i}",
                    "source": "Health Canada",
                    "publication_date": datetime.now() - timedelta(days=30*i),
                    "source_type": SourceType.HEALTH_AUTHORITY
                })
            
            return results
            
        except Exception as e:
            print(f"Health Canada search error: {e}")
            return []
        

    def _search_who(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Searches WHO website"""
        try:
            # Mock WHO results
            results = []
            
            who_topics = [
                "WHO guidelines",
                "Global health recommendations",
                "International medical standards"
            ]
            
            for i, topic in enumerate(who_topics[:max_results]):
                results.append({
                    "title": f"{topic} - {query.split()[0]}",
                    "content": f"WHO recommendations regarding {query}...",
                    "url": f"https://who.int/health/mock_{i}",
                    "source": "World Health Organization",
                    "publication_date": datetime.now() - timedelta(days=60*i),
                    "source_type": SourceType.HEALTH_AUTHORITY
                })
            
            return results
            
        except Exception as e:
            print(f"WHO search error: {e}")
            return []
    

    def _search_medical_databases(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Searches medical databases like UpToDate, Mayo Clinic"""
        try:
            results = []
            
            # Mock results from various medical databases
            databases = [
                ("Mayo Clinic", "mayoclinic.org", SourceType.MEDICAL_DATABASE),
                ("UpToDate", "uptodate.com", SourceType.CLINICAL_GUIDELINE),
                ("Cochrane Library", "cochranelibrary.com", SourceType.PEER_REVIEWED)
            ]
            
            for db_name, domain, source_type in databases:
                if len(results) >= max_results:
                    break
                    
                results.append({
                    "title": f"{db_name}: {query.split()[0]} information",
                    "content": f"Comprehensive {db_name} information about {query}...",
                    "url": f"https://{domain}/mock_result",
                    "source": db_name,
                    "publication_date": datetime.now() - timedelta(days=15),
                    "source_type": source_type
                })
            
            return results
            
        except Exception as e:
            print(f"Medical database search error: {e}")
            return []
    

    def _parse_pubmed_xml(self, xml_content: str, pmids: List[str]) -> List[Dict[str, Any]]:
        """Parses PubMed XML response"""
        try:
            # Simplified XML parsing - in production use proper XML parser
            results = []
            
            # Mock parsing for now
            for i, pmid in enumerate(pmids[:3]):
                results.append({
                    "title": f"PubMed Article {pmid}: Medical Research",
                    "content": f"Abstract for PMID {pmid} discussing medical topics...",
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "source": "PubMed",
                    "publication_date": datetime.now() - timedelta(days=30*i),
                    "source_type": SourceType.PEER_REVIEWED
                })
            
            return results
            
        except Exception as e:
            print(f"PubMed XML parsing error: {e}")
            return []
    

    def _extract_medical_entities_from_results(self, 
                                             results: List[Dict[str, Any]], 
                                             context: RetrievalContext) -> List[Dict[str, Any]]:
        """Extracts medical entities from search results"""
        try:
            enriched_results = []
            
            # Medical entity patterns
            medical_patterns = {
                'conditions': r'\b(?:syndrome|disease|disorder|condition|diagnosis)\b',
                'symptoms': r'\b(?:pain|fever|rash|swelling|inflammation|bleeding)\b',
                'medications': r'\b(?:mg|tablet|capsule|injection|therapy|treatment)\b',
                'anatomy': r'\b(?:heart|lung|liver|kidney|brain|skin|muscle|bone)\b'
            }
            
            for result in results:
                text = f"{result.get('title', '')} {result.get('content', '')}".lower()
                
                extracted_entities = []
                for entity_type, pattern in medical_patterns.items():
                    matches = re.findall(pattern, text)
                    extracted_entities.extend([f"{entity_type}:{match}" for match in matches])
                
                # Add context-relevant entities
                context_entities = []
                if context.medical_entities:
                    primary_condition = context.medical_entities.get('primary_condition', '')
                    symptoms = context.medical_entities.get('symptoms', [])
                    
                    if primary_condition.lower() in text:
                        context_entities.append(f"primary_condition:{primary_condition}")
                    
                    for symptom in symptoms:
                        if symptom.lower() in text:
                            context_entities.append(f"symptom:{symptom}")
                
                result['extracted_entities'] = extracted_entities
                result['context_entities'] = context_entities
                enriched_results.append(result)
            
            return enriched_results
            
        except Exception as e:
            print(f"Entity extraction error: {e}")
            return results
    

    def _calculate_semantic_similarity(self, 
                                     results: List[Dict[str, Any]], 
                                     query: str, 
                                     context: RetrievalContext) -> List[Dict[str, Any]]:
        """Calculates semantic similarity between query and results"""
        try:
            if not self.semantic_model:
                # Fallback to keyword matching
                return self._fallback_keyword_similarity(results, query)
            
            # Encode query
            query_embedding = self.semantic_model.encode([query])
            
            # Create enhanced query with context
            enhanced_query = self._create_enhanced_query(query, context)
            enhanced_embedding = self.semantic_model.encode([enhanced_query])
            
            for result in results:
                # Combine title and content for semantic analysis
                result_text = f"{result.get('title', '')} {result.get('content', '')}"
                result_embedding = self.semantic_model.encode([result_text])
                
                # Calculate similarity scores
                basic_similarity = cosine_similarity(query_embedding, result_embedding)[0][0]
                enhanced_similarity = cosine_similarity(enhanced_embedding, result_embedding)[0][0]
                
                # Combine similarities with weights
                semantic_score = (basic_similarity * 0.6) + (enhanced_similarity * 0.4)
                
                result['semantic_similarity'] = float(semantic_score)
                result['semantic_concepts'] = self._extract_semantic_concepts(result_text)
            
            return results
            
        except Exception as e:
            print(f"Semantic similarity error: {e}")
            return self._fallback_keyword_similarity(results, query)
    

    def _create_enhanced_query(self, original_query: str, context: RetrievalContext) -> str:
        """Creates enhanced query with context information"""
        enhanced_parts = [original_query]
        
        # Add medical context
        if context.medical_entities:
            primary_condition = context.medical_entities.get('primary_condition', '')
            if primary_condition:
                enhanced_parts.append(primary_condition)
            
            symptoms = context.medical_entities.get('symptoms', [])
            enhanced_parts.extend(symptoms[:3])  # Top 3 symptoms
        
        # Add geographical context
        if context.geographical_region:
            enhanced_parts.append(f"{context.geographical_region} treatment guidelines")
        
        # Add seasonal context
        if context.current_season:
            enhanced_parts.append(f"{context.current_season} medical conditions")
        
        return " ".join(enhanced_parts)
    

    def _extract_semantic_concepts(self, text: str) -> List[str]:
        """Extracts semantic medical concepts from text"""
        # Simplified concept extraction
        medical_concepts = [
            'diagnosis', 'treatment', 'prevention', 'symptoms', 'prognosis',
            'etiology', 'epidemiology', 'pathophysiology', 'management',
            'guidelines', 'evidence', 'clinical', 'research', 'therapy'
        ]
        
        text_lower = text.lower()
        found_concepts = [concept for concept in medical_concepts if concept in text_lower]
        
        return found_concepts
    

    def _fallback_keyword_similarity(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Fallbacks keyword-based similarity when semantic model unavailable"""
        query_words = set(query.lower().split())
        
        for result in results:
            result_text = f"{result.get('title', '')} {result.get('content', '')}".lower()
            result_words = set(result_text.split())
            
            # Calculate Jaccard similarity
            intersection = query_words.intersection(result_words)
            union = query_words.union(result_words)
            
            similarity = len(intersection) / len(union) if union else 0
            result['semantic_similarity'] = similarity
            result['semantic_concepts'] = []
        
        return results
    

    def _apply_intelligent_scoring(self, 
                                 results: List[Dict[str, Any]], 
                                 context: RetrievalContext) -> List[MedicalDocument]:
        """Applies scoring based on multiple factors"""
        documents = []
        
        for result in results:
            # Calculate component scores
            credibility_score = self._calculate_credibility_score(result)
            relevance_score = self._calculate_relevance_score(result, context)
            recency_score = self._calculate_recency_score(result)
            regional_relevance = self._calculate_regional_relevance(result, context)
            
            # Calculate final weighted score
            final_score = (
                credibility_score * 0.3 +
                relevance_score * 0.3 +
                recency_score * 0.2 +
                regional_relevance * 0.2
            )
            
            # Create MedicalDocument
            doc = MedicalDocument(
                title=result.get('title', ''),
                content=result.get('content', ''),
                url=result.get('url', ''),
                source=result.get('source', ''),
                source_type=result.get('source_type', SourceType.EDUCATIONAL),
                publication_date=result.get('publication_date'),
                credibility_score=credibility_score,
                relevance_score=relevance_score,
                regional_relevance=regional_relevance,
                recency_score=recency_score,
                final_score=final_score,
                extracted_entities=result.get('extracted_entities', []),
                semantic_concepts=result.get('semantic_concepts', [])
            )
            
            documents.append(doc)
        
        return documents
    
    
    def _calculate_credibility_score(self, result: Dict[str, Any]) -> float:
        """Calculates credibility score based on source type and authority"""
        base_score = self.source_weights.get(result.get('source_type', SourceType.EDUCATIONAL), 0.5)
        
        # Boost score for trusted domains
        url = result.get('url', '').lower()
        for trusted_domain in self.trusted_sources:
            if trusted_domain in url:
                base_score = min(1.0, base_score + 0.1)
                break
        
        return base_score
    

    def _calculate_relevance_score(self, result: Dict[str, Any], context: RetrievalContext) -> float:
        """Calculates relevance score based on medical entities and context"""
        base_score = result.get('semantic_similarity', 0.5)
        
        # Boost for context entity matches
        context_entities = result.get('context_entities', [])
        entity_boost = len(context_entities) * 0.1
        
        # Boost for image analysis alignment (if visual symptoms)
        if context.image_analysis_results:
            visual_terms = ['visual', 'appearance', 'image', 'dermatology', 'skin']
            text = f"{result.get('title', '')} {result.get('content', '')}".lower()
            visual_boost = sum(0.05 for term in visual_terms if term in text)
        else:
            visual_boost = 0
        
        # Boost for urgency alignment
        if context.urgency_level == "emergency":
            urgency_terms = ['emergency', 'urgent', 'acute', 'immediate']
            text = f"{result.get('title', '')} {result.get('content', '')}".lower()
            urgency_boost = sum(0.1 for term in urgency_terms if term in text)
        else:
            urgency_boost = 0
        
        return min(1.0, base_score + entity_boost + visual_boost + urgency_boost)
    

    def _calculate_recency_score(self, result: Dict[str, Any]) -> float:
        """Calculates recency score with exponential decay"""
        pub_date = result.get('publication_date')
        if not pub_date:
            return 0.5  # Default for unknown dates
        
        days_old = (datetime.now() - pub_date).days
        
        # Exponential decay: newer is better
        if days_old <= 30:
            return 1.0  # Perfect score for last month
        elif days_old <= 365:
            return 0.8  # Good score for last year
        elif days_old <= 1095:  # 3 years
            return 0.6
        elif days_old <= 1825:  # 5 years
            return 0.4
        else:
            return 0.2  # Older than 5 years
    

    def _calculate_regional_relevance(self, result: Dict[str, Any], context: RetrievalContext) -> float:
        """Calculates regional relevance score"""
        text = f"{result.get('title', '')} {result.get('content', '')}".lower()
        region = context.geographical_region.lower()
        
        # Direct region mentions
        if region in text:
            return 1.0
        
        # Canadian-specific terms
        canadian_terms = ['canada', 'canadian', 'health canada', 'ontario', 'quebec', 'british columbia']
        canadian_matches = sum(0.2 for term in canadian_terms if term in text)
        
        # North American relevance
        na_terms = ['north america', 'north american', 'usa', 'united states']
        na_matches = sum(0.1 for term in na_terms if term in text)
        
        return min(1.0, 0.5 + canadian_matches + na_matches)  # Base score 0.5
    

    def _remove_duplicates_and_rank(self, documents: List[MedicalDocument]) -> List[MedicalDocument]:
        """Removes duplicates and rank by final score"""
        # Simple deduplication by URL and title similarity
        seen_urls = set()
        unique_docs = []
        
        for doc in documents:
            if doc.url not in seen_urls:
                seen_urls.add(doc.url)
                unique_docs.append(doc)
        
        # Sort by final score (descending)
        return sorted(unique_docs, key=lambda x: x.final_score, reverse=True)
    

    def _apply_context_filtering(self, 
                               documents: List[MedicalDocument], 
                               context: RetrievalContext) -> List[MedicalDocument]:
        """Applies context-aware filtering"""
        filtered_docs = []
        
        for doc in documents:
            # Filter by minimum score threshold
            if doc.final_score < 0.3:
                continue
            
            # Emergency context: prioritize urgent/emergency content
            if context.urgency_level == "emergency":
                urgent_terms = ['emergency', 'urgent', 'acute', 'immediate', 'critical']
                text = f"{doc.title} {doc.content}".lower()
                if any(term in text for term in urgent_terms):
                    doc.final_score *= 1.2  # Boost emergency-relevant content
            
            # Seasonal filtering
            if context.current_season:
                seasonal_terms = {
                    'winter': ['influenza', 'flu', 'cold', 'respiratory'],
                    'summer': ['sunburn', 'heat', 'dehydration', 'allergies'],
                    'spring': ['allergies', 'pollen', 'asthma'],
                    'fall': ['allergies', 'respiratory', 'immune']
                }
                
                season_terms = seasonal_terms.get(context.current_season, [])
                text = f"{doc.title} {doc.content}".lower()
                if any(term in text for term in season_terms):
                    doc.regional_relevance *= 1.1  # Small seasonal boost
            
            filtered_docs.append(doc)
        
        # Re-sort after context adjustments
        return sorted(filtered_docs, key=lambda x: x.final_score, reverse=True)
    

    def format_retrieval_results(self, documents: List[MedicalDocument]) -> Dict[str, Any]:
        """Formats results for integration with existing system"""
        return {
            "total_documents": len(documents),
            "top_documents": [
                {
                    "title": doc.title,
                    "content": doc.content[:500] + "..." if len(doc.content) > 500 else doc.content,
                    "url": doc.url,
                    "source": doc.source,
                    "credibility_score": round(doc.credibility_score, 3),
                    "relevance_score": round(doc.relevance_score, 3),
                    "final_score": round(doc.final_score, 3),
                    "publication_date": doc.publication_date.isoformat() if doc.publication_date else None,
                    "key_entities": doc.extracted_entities[:5],
                    "semantic_concepts": doc.semantic_concepts[:3]
                }
                for doc in documents[:10]  # Top 10 results
            ],
            "source_distribution": self._calculate_source_distribution(documents),
            "average_credibility": sum(doc.credibility_score for doc in documents) / len(documents) if documents else 0,
            "retrieval_metadata": {
                "timestamp": datetime.now().isoformat(),
                "semantic_model_used": self.semantic_model is not None
            }
        }
    
    
    def _calculate_source_distribution(self, documents: List[MedicalDocument]) -> Dict[str, int]:
        """Calculates distribution of source types"""
        distribution = {}
        for doc in documents:
            source_type = doc.source_type.value
            distribution[source_type] = distribution.get(source_type, 0) + 1
        return distribution