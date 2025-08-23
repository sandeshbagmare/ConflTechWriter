"""
Article generation orchestrator with free services.
"""

import logging
from typing import Dict, Any
from datetime import datetime

from ..services.search_service import FreeSearchService
from ..services.llm_service import LLMService

logger = logging.getLogger(__name__)

class ArticleOrchestrator:
    """
    Orchestrates the complete article generation workflow using free services.
    """
    
    def __init__(self):
        self.search_service = FreeSearchService()
        self.llm_service = LLMService()
    
    async def generate_article(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete article using the free workflow.
        
        Args:
            job_data: Job parameters including topic, depth, etc.
            
        Returns:
            Complete article with metadata
        """
        topic = job_data.get("topic", "Technology")
        desired_depth = job_data.get("desired_depth", "intermediate")
        max_length = job_data.get("max_length", 5000)
        
        logger.info(f"Starting article generation for: {topic}")
        
        try:
            # Step 1: Generate research plan
            logger.info("Step 1: Generating research plan")
            research_plan = await self.llm_service.generate_research_plan(
                topic=topic,
                depth=desired_depth
            )
            
            # Step 2: Conduct research using free search
            logger.info("Step 2: Conducting research")
            research_data = await self._conduct_research(topic, research_plan)
            
            # Step 3: Generate the article
            logger.info("Step 3: Generating article content")
            article_data = await self.llm_service.generate_article(
                topic=topic,
                research_data=research_data,
                sections=research_plan.get("sections", []),
                max_length=max_length
            )
            
            # Step 4: Enhance and finalize
            logger.info("Step 4: Finalizing article")
            final_article = await self._finalize_article(
                article_data,
                research_data,
                topic
            )
            
            logger.info(f"Article generation completed for: {topic}")
            return {
                "success": True,
                "article": final_article,
                "metadata": {
                    "topic": topic,
                    "depth": desired_depth,
                    "word_count": final_article.get("word_count", 0),
                    "sources_used": len(research_data.get("sources", [])),
                    "generated_at": datetime.utcnow().isoformat(),
                    "generation_method": "free_services"
                }
            }
            
        except Exception as e:
            logger.error(f"Article generation failed for {topic}: {e}")
            
            # Generate fallback article
            fallback_article = await self._generate_fallback_article(topic, max_length)
            
            return {
                "success": True,  # Still return success with fallback
                "article": fallback_article,
                "metadata": {
                    "topic": topic,
                    "depth": desired_depth,
                    "word_count": fallback_article.get("word_count", 0),
                    "sources_used": 0,
                    "generated_at": datetime.utcnow().isoformat(),
                    "generation_method": "fallback_template",
                    "note": "Generated using template due to service limitations"
                },
                "warning": f"Used fallback generation due to: {str(e)}"
            }
    
    async def _conduct_research(self, topic: str, research_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct research using free search services."""
        research_data = {
            "sources": [],
            "key_points": [],
            "summary": ""
        }
        
        try:
            # Get search queries from research plan
            search_queries = research_plan.get("search_queries", [f"{topic} overview"])
            
            # Perform searches
            for query in search_queries[:5]:  # Limit to 5 queries to avoid rate limits
                try:
                    logger.info(f"Searching for: {query}")
                    results = await self.search_service.search_web(query, max_results=3)
                    
                    for result in results:
                        if len(research_data["sources"]) < 15:  # Limit total sources
                            research_data["sources"].append(result)
                            
                except Exception as e:
                    logger.warning(f"Search failed for query '{query}': {e}")
                    continue
            
            # Extract key points from sources
            research_data["key_points"] = await self._extract_key_points(
                research_data["sources"]
            )
            
            logger.info(f"Research completed: {len(research_data['sources'])} sources found")
            
        except Exception as e:
            logger.warning(f"Research phase failed: {e}")
            # Return empty research data - article generation will use templates
        
        return research_data
    
    async def _extract_key_points(self, sources: list) -> list:
        """Extract key points from research sources."""
        key_points = []
        
        try:
            # Simple extraction - get first sentence from each source snippet
            for source in sources:
                content = source.get("content", "")
                if content:
                    # Split into sentences and take the first meaningful one
                    sentences = content.split('. ')
                    for sentence in sentences:
                        if len(sentence.strip()) > 50:  # Skip very short sentences
                            key_points.append(sentence.strip() + ".")
                            break
                
                if len(key_points) >= 10:  # Limit key points
                    break
            
        except Exception as e:
            logger.warning(f"Key point extraction failed: {e}")
        
        return key_points
    
    async def _finalize_article(
        self,
        article_data: Dict[str, Any],
        research_data: Dict[str, Any],
        topic: str
    ) -> Dict[str, Any]:
        """Finalize the article with metadata and enhancements."""
        
        final_article = {
            "title": article_data.get("title", f"Guide to {topic}"),
            "content": article_data.get("content", ""),
            "summary": article_data.get("summary", ""),
            "word_count": article_data.get("word_count", 0)
        }
        
        # Add bibliography if we have sources
        if research_data.get("sources"):
            bibliography = []
            for i, source in enumerate(research_data["sources"][:10], 1):
                bibliography.append({
                    "id": i,
                    "title": source.get("title", "Unknown Source"),
                    "url": source.get("url", ""),
                    "domain": source.get("domain", ""),
                    "accessed": datetime.utcnow().strftime("%Y-%m-%d")
                })
            
            final_article["bibliography"] = bibliography
            
            # Add sources section to content if not already present
            if "## Sources" not in final_article["content"]:
                sources_section = "\n\n## Sources and References\n\n"
                for item in bibliography:
                    sources_section += f"{item['id']}. [{item['title']}]({item['url']})\n"
                
                final_article["content"] += sources_section
                final_article["word_count"] = len(final_article["content"].split())
        
        # Add quality metrics
        final_article["quality_metrics"] = {
            "readability_score": "intermediate",
            "source_count": len(research_data.get("sources", [])),
            "sections_count": len(final_article["content"].split("##")) - 1,
            "has_introduction": "# " in final_article["content"],
            "has_conclusion": "conclusion" in final_article["content"].lower()
        }
        
        return final_article
    
    async def _generate_fallback_article(self, topic: str, max_length: int) -> Dict[str, Any]:
        """Generate a basic article using templates when services fail."""
        
        title = f"Introduction to {topic}"
        
        content = f"""# {title}

## Overview

{topic} is an important subject that deserves careful consideration and analysis. This article provides a comprehensive introduction to help readers understand the key concepts and implications.

## Background

Understanding {topic} requires examining its foundational elements and how they relate to current developments in the field.

## Key Concepts

Several important concepts are central to {topic}:

- **Fundamental Principles**: The basic ideas that underpin {topic}
- **Current Applications**: How {topic} is being used today
- **Future Potential**: Where {topic} might lead in the future

## Current State

The current landscape of {topic} shows significant activity and development, with numerous organizations and researchers contributing to its advancement.

## Challenges and Opportunities

Like many evolving fields, {topic} presents both challenges that must be addressed and opportunities for innovation and growth.

## Future Outlook

Looking ahead, {topic} appears positioned for continued development and broader adoption across various sectors and applications.

## Conclusion

{topic} represents an important area of study and development. As the field continues to evolve, it will likely bring new insights and applications that benefit various stakeholders.

---

*This article provides a general introduction to {topic}. For more detailed and current information, please consult recent academic and industry sources.*
"""
        
        word_count = len(content.split())
        
        return {
            "title": title,
            "content": content,
            "summary": f"This article provides a comprehensive introduction to {topic}, covering key concepts, current applications, and future potential.",
            "word_count": word_count,
            "quality_metrics": {
                "readability_score": "beginner",
                "source_count": 0,
                "sections_count": 6,
                "has_introduction": True,
                "has_conclusion": True
            }
        }
