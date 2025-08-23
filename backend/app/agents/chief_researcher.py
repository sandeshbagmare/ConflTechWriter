"""
Chief Researcher Agent - Orchestrates the research and article generation process.
Uses free search services and template-based fallbacks.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..services.llm_service import LLMService
from ..services.search_service import FreeSearchService

logger = logging.getLogger(__name__)

class ChiefResearcher:
    """
    Chief Researcher Agent that orchestrates the entire article generation process.
    Uses free services and provides comprehensive fallbacks.
    """
    
    def __init__(self):
        self.llm_service = LLMService()
        self.logger = logger
        
    async def plan_research(self, topic: str, desired_depth: str = "intermediate") -> Dict[str, Any]:
        """
        Create a research plan for the given topic.
        
        Args:
            topic: The topic to research
            desired_depth: Target audience level (beginner, intermediate, expert)
            
        Returns:
            Research plan with queries and structure
        """
        try:
            self.logger.info(f"Planning research for topic: {topic}")
            
            # Generate research queries using LLM or fallback
            research_queries = await self.llm_service.generate_search_queries(
                research_question=topic,
                num_queries=8
            )
            
            # Create article structure
            structure = await self._create_article_structure(topic, desired_depth)
            
            plan = {
                "topic": topic,
                "desired_depth": desired_depth,
                "research_queries": research_queries,
                "article_structure": structure,
                "estimated_sections": len(structure.get("sections", [])),
                "created_at": datetime.utcnow().isoformat(),
                "status": "planned"
            }
            
            self.logger.info(f"Research plan created with {len(research_queries)} queries")
            return plan
            
        except Exception as e:
            self.logger.error(f"Failed to plan research: {e}")
            # Fallback plan
            return {
                "topic": topic,
                "desired_depth": desired_depth,
                "research_queries": [
                    f"{topic} tutorial",
                    f"{topic} best practices", 
                    f"{topic} implementation guide",
                    f"how to use {topic}",
                    f"{topic} examples"
                ],
                "article_structure": {
                    "title": topic.title(),
                    "sections": [
                        "Introduction",
                        "Core Concepts", 
                        "Implementation Guide",
                        "Best Practices",
                        "Common Challenges",
                        "Conclusion"
                    ]
                },
                "estimated_sections": 6,
                "created_at": datetime.utcnow().isoformat(),
                "status": "planned_fallback"
            }
    
    async def _create_article_structure(self, topic: str, depth: str) -> Dict[str, Any]:
        """Create a structured outline for the article."""
        
        depth_prompts = {
            "beginner": f"Create a beginner-friendly article structure for {topic} that explains fundamentals clearly",
            "intermediate": f"Create an intermediate-level article structure for {topic} with practical implementation details", 
            "expert": f"Create an expert-level article structure for {topic} focusing on advanced concepts and best practices"
        }
        
        prompt = f"""Create a detailed article structure for: {topic}

Target audience: {depth}

{depth_prompts.get(depth, depth_prompts['intermediate'])}

Return a JSON structure with title and sections array:
{{"title": "Article Title", "sections": ["Section 1", "Section 2", ...]}}"""
        
        try:
            result = await self.llm_service.generate_structured_response(prompt, {})
            
            if isinstance(result, dict) and "sections" in result:
                return result
            else:
                # Fallback structure
                return self._get_fallback_structure(topic, depth)
                
        except Exception as e:
            self.logger.warning(f"Failed to create structure, using fallback: {e}")
            return self._get_fallback_structure(topic, depth)
    
    def _get_fallback_structure(self, topic: str, depth: str) -> Dict[str, Any]:
        """Get fallback article structure based on depth level."""
        
        if depth == "beginner":
            sections = [
                "What is " + topic,
                "Why Use " + topic,
                "Basic Concepts",
                "Getting Started",
                "Simple Examples",
                "Next Steps"
            ]
        elif depth == "expert":
            sections = [
                "Advanced " + topic + " Concepts",
                "Architecture Patterns",
                "Performance Optimization",
                "Security Considerations", 
                "Production Deployment",
                "Troubleshooting",
                "Future Developments"
            ]
        else:  # intermediate
            sections = [
                "Introduction to " + topic,
                "Core Concepts",
                "Implementation Guide",
                "Best Practices",
                "Common Challenges",
                "Real-world Examples",
                "Conclusion"
            ]
        
        return {
            "title": f"Complete Guide to {topic.title()}",
            "sections": sections
        }
    
    async def conduct_research(self, research_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct research using the research plan.
        
        Args:
            research_plan: The research plan from plan_research()
            
        Returns:
            Research results with collected information
        """
        try:
            self.logger.info("Starting research phase")
            
            research_results = {
                "topic": research_plan["topic"],
                "sources": [],
                "key_points": [],
                "total_sources_found": 0,
                "research_completed_at": datetime.utcnow().isoformat()
            }
            
            # Use free search service
            async with FreeSearchService() as search_service:
                for query in research_plan["research_queries"][:5]:  # Limit to 5 queries
                    try:
                        self.logger.info(f"Searching for: {query}")
                        
                        # Get search results with content
                        results = await search_service.search_and_extract(query, max_results=3)
                        
                        for result in results:
                            # Extract key snippets
                            if result.get('content'):
                                snippets = await self.llm_service.extract_snippets(
                                    content=result['content'],
                                    research_question=research_plan["topic"],
                                    max_snippets=3
                                )
                                
                                research_results["sources"].append({
                                    "title": result.get('title', 'Unknown'),
                                    "url": result.get('url', ''),
                                    "snippets": snippets,
                                    "query": query
                                })
                        
                        research_results["total_sources_found"] += len(results)
                        
                        # Add delay to be respectful to search service
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        self.logger.warning(f"Search failed for query '{query}': {e}")
                        continue
            
            # Extract key points from all sources
            if research_results["sources"]:
                key_points = await self._extract_key_points(research_results["sources"])
                research_results["key_points"] = key_points
            
            self.logger.info(f"Research completed. Found {research_results['total_sources_found']} sources")
            return research_results
            
        except Exception as e:
            self.logger.error(f"Research phase failed: {e}")
            
            # Return minimal fallback research
            return {
                "topic": research_plan["topic"],
                "sources": [],
                "key_points": [
                    f"{research_plan['topic']} is an important technical concept",
                    f"Implementation requires careful planning and consideration",
                    f"Best practices should be followed for optimal results",
                    f"Common challenges include complexity and integration issues",
                    f"Proper testing and monitoring are essential"
                ],
                "total_sources_found": 0,
                "research_completed_at": datetime.utcnow().isoformat(),
                "fallback_used": True
            }
    
    async def _extract_key_points(self, sources: List[Dict[str, Any]]) -> List[str]:
        """Extract key points from research sources."""
        
        all_snippets = []
        for source in sources:
            for snippet in source.get("snippets", []):
                all_snippets.append(snippet.get("text", ""))
        
        if not all_snippets:
            return []
        
        # Combine snippets and extract key points
        combined_content = "\n".join(all_snippets[:10])  # Limit content
        
        try:
            prompt = f"""Extract 5-7 key points from this research content:

{combined_content}

Return as JSON array: ["point 1", "point 2", ...]"""
            
            result = await self.llm_service.generate_structured_response(prompt, {})
            
            if isinstance(result, list):
                return result[:7]  # Limit to 7 points
            else:
                return self._extract_fallback_points(combined_content)
                
        except Exception as e:
            self.logger.warning(f"Key point extraction failed: {e}")
            return self._extract_fallback_points(combined_content)
    
    def _extract_fallback_points(self, content: str) -> List[str]:
        """Extract key points using simple text processing."""
        
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 50]
        
        # Select diverse sentences as key points
        key_points = []
        for sentence in sentences[:7]:
            if sentence and not sentence.lower().startswith(('this', 'that', 'it', 'they')):
                key_points.append(sentence + '.')
        
        return key_points or [
            "Key concepts and principles are important to understand",
            "Implementation requires careful planning and consideration", 
            "Best practices should be followed for optimal results",
            "Common challenges include complexity and integration",
            "Proper testing and monitoring are essential"
        ]
    
    async def generate_article(
        self, 
        research_plan: Dict[str, Any], 
        research_results: Dict[str, Any],
        max_length: int = 5000
    ) -> Dict[str, Any]:
        """
        Generate the final article from research.
        
        Args:
            research_plan: The research plan
            research_results: Results from research phase
            max_length: Maximum article length in words
            
        Returns:
            Generated article with metadata
        """
        try:
            self.logger.info("Starting article generation")
            
            # Prepare content for article generation
            topic = research_plan["topic"]
            structure = research_plan["article_structure"]
            key_points = research_results.get("key_points", [])
            
            # Generate article using LLM or template
            article_prompt = f"""Write a comprehensive technical article about: {topic}

Article Structure:
{structure}

Key Research Points:
{chr(10).join('- ' + point for point in key_points)}

Target Audience: {research_plan.get('desired_depth', 'intermediate')}
Maximum Length: {max_length} words

Create a well-structured, informative article that covers all the key concepts and provides practical value."""
            
            article_content = await self.llm_service.generate_response(
                prompt=article_prompt,
                max_tokens=max_length * 2,  # Rough token estimate
                temperature=0.7
            )
            
            # Create final article package
            article = {
                "title": structure.get("title", topic.title()),
                "content": article_content,
                "topic": topic,
                "target_audience": research_plan.get("desired_depth", "intermediate"),
                "word_count": len(article_content.split()),
                "sources_used": len(research_results.get("sources", [])),
                "key_points": key_points,
                "generated_at": datetime.utcnow().isoformat(),
                "quality_score": self._calculate_quality_score(article_content, research_results),
                "metadata": {
                    "research_queries": research_plan.get("research_queries", []),
                    "total_sources": research_results.get("total_sources_found", 0),
                    "generation_method": "ai_with_research" if research_results.get("sources") else "template_based"
                }
            }
            
            self.logger.info(f"Article generated successfully. Word count: {article['word_count']}")
            return article
            
        except Exception as e:
            self.logger.error(f"Article generation failed: {e}")
            
            # Generate fallback article
            return await self._generate_fallback_article(research_plan, research_results)
    
    def _calculate_quality_score(self, content: str, research_results: Dict[str, Any]) -> float:
        """Calculate a quality score for the generated article."""
        
        score = 0.5  # Base score
        
        # Length bonus
        word_count = len(content.split())
        if word_count > 1000:
            score += 0.2
        elif word_count > 500:
            score += 0.1
        
        # Sources bonus
        source_count = len(research_results.get("sources", []))
        if source_count > 5:
            score += 0.2
        elif source_count > 2:
            score += 0.1
        
        # Structure bonus (simple check for headers)
        if content.count('#') > 3:
            score += 0.1
        
        return min(score, 1.0)
    
    async def _generate_fallback_article(
        self, 
        research_plan: Dict[str, Any], 
        research_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a fallback article when main generation fails."""
        
        topic = research_plan["topic"]
        structure = research_plan["article_structure"]
        
        # Use template-based generation
        fallback_content = f"""# {structure.get('title', topic.title())}

## Introduction

This comprehensive guide explores {topic} and provides practical insights for developers and technical professionals. Understanding {topic} is essential for modern software development and can significantly improve your technical capabilities.

## Core Concepts

{topic} involves several fundamental concepts that are important to understand:

- **Basic Principles**: The underlying theory and mechanisms
- **Key Components**: Main elements and their relationships  
- **Implementation Patterns**: Common approaches and methodologies
- **Best Practices**: Industry-standard recommendations

## Implementation Guide

### Getting Started

To implement {topic} effectively, follow these steps:

1. **Environment Setup**: Prepare your development environment
2. **Basic Configuration**: Set up the necessary components
3. **Initial Implementation**: Create a minimal working example
4. **Testing and Validation**: Verify your implementation works correctly

### Advanced Features

Once you have a basic implementation, consider these advanced features:

- **Performance Optimization**: Improve efficiency and speed
- **Security Considerations**: Implement proper security measures
- **Scalability Planning**: Prepare for growth and increased load
- **Monitoring and Logging**: Track performance and debug issues

## Best Practices

When working with {topic}, follow these best practices:

- **Code Quality**: Write clean, maintainable code
- **Documentation**: Provide clear documentation for your implementation
- **Testing**: Implement comprehensive testing strategies
- **Version Control**: Use proper version control practices

## Common Challenges

Some common challenges when implementing {topic} include:

- **Complexity**: Managing the complexity of implementation
- **Integration**: Integrating with existing systems
- **Performance**: Optimizing for performance requirements
- **Maintenance**: Keeping the implementation up to date

## Conclusion

{topic} is a powerful concept that can significantly improve your development capabilities. By following the guidelines and best practices outlined in this article, you can successfully implement and maintain a robust solution.

Remember to start with a solid foundation, follow best practices, and continuously improve your implementation based on feedback and changing requirements.

## Additional Resources

- Official documentation and specifications
- Community resources and forums  
- Related tools and frameworks
- Advanced topics for further learning
"""

        return {
            "title": structure.get("title", topic.title()),
            "content": fallback_content,
            "topic": topic,
            "target_audience": research_plan.get("desired_depth", "intermediate"),
            "word_count": len(fallback_content.split()),
            "sources_used": 0,
            "key_points": research_results.get("key_points", []),
            "generated_at": datetime.utcnow().isoformat(),
            "quality_score": 0.6,  # Medium quality for template
            "metadata": {
                "research_queries": research_plan.get("research_queries", []),
                "total_sources": 0,
                "generation_method": "template_fallback"
            },
            "is_fallback": True
        }
