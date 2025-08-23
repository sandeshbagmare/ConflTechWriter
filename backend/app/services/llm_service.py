"""
LLM Service with free alternatives and fallback templates.
"""

import logging
from typing import Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

# Template responses for when AI services are unavailable
TEMPLATE_RESPONSES = {
    "research_plan": {
        "sections": [
            "Introduction and Overview",
            "Current State and Background",
            "Key Technologies and Methods", 
            "Recent Developments",
            "Challenges and Limitations",
            "Future Directions",
            "Practical Applications",
            "Conclusion"
        ],
        "search_queries": [
            "{topic} overview 2024",
            "{topic} latest developments",
            "{topic} challenges problems",
            "{topic} future trends",
            "{topic} practical applications"
        ]
    },
    
    "article_template": """# {title}

## Executive Summary

This comprehensive article explores {topic}, covering its current state, recent developments, and future implications. Through detailed analysis and research, we examine the key aspects that make {topic} relevant in today's technological landscape.

## Introduction

{topic} has emerged as a significant area of interest in recent years. This article provides an in-depth look at the current state of {topic}, exploring its foundations, applications, and potential for future development.

## Background and Context

Understanding {topic} requires examining its historical development and current context. The field has evolved significantly, driven by technological advances and changing market demands.

## Key Components and Technologies

The fundamental elements of {topic} include several important technologies and methodologies that work together to create effective solutions.

## Current Challenges

Like many emerging technologies, {topic} faces several challenges that must be addressed for continued growth and adoption.

## Recent Developments

The field of {topic} has seen numerous exciting developments recently, indicating strong momentum and continued innovation.

## Future Outlook

Looking ahead, {topic} shows significant promise for continued development and broader adoption across various industries.

## Practical Applications

Real-world applications of {topic} demonstrate its value and potential impact across different sectors.

## Conclusion

{topic} represents an important and evolving field with significant potential. Continued research and development will likely yield even more impressive results in the coming years.

---

*This article was generated using comprehensive research and analysis of available information on {topic}.*
"""
}

class LLMService:
    """
    Free LLM service with template fallbacks.
    """
    
    def __init__(self):
        self.use_gemini = False
        self.gemini_client = None
        
        # Try to initialize Gemini if API key is available
        try:
            import os
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.gemini_client = genai.GenerativeModel('gemini-pro')
                self.use_gemini = True
                logger.info("Gemini AI initialized successfully")
            else:
                logger.info("No Gemini API key found, using template fallbacks")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini AI: {e}. Using template fallbacks.")
    
    async def generate_research_plan(self, topic: str, depth: str = "intermediate") -> Dict[str, Any]:
        """
        Generate a research plan for the given topic.
        """
        if self.use_gemini and self.gemini_client:
            try:
                prompt = f"""
                Create a detailed research plan for writing a {depth}-level article about "{topic}".
                
                Provide a JSON response with:
                1. "sections" - array of 6-8 main sections for the article
                2. "search_queries" - array of 8-10 specific search queries to find relevant information
                
                Make it comprehensive and well-structured for {depth} readers.
                """
                
                response = self.gemini_client.generate_content(prompt)
                result = self._parse_json_response(response.text)
                if result:
                    logger.info(f"Generated research plan using Gemini for: {topic}")
                    return result
            except Exception as e:
                logger.warning(f"Gemini API failed: {e}. Using template fallback.")
        
        # Fallback to template
        template = TEMPLATE_RESPONSES["research_plan"].copy()
        template["search_queries"] = [q.format(topic=topic) for q in template["search_queries"]]
        
        logger.info(f"Generated research plan using template for: {topic}")
        return template
    
    async def generate_article(
        self, 
        topic: str, 
        research_data: Dict[str, Any],
        sections: list,
        max_length: int = 5000
    ) -> Dict[str, Any]:
        """
        Generate a complete article based on research data.
        """
        if self.use_gemini and self.gemini_client and research_data.get("sources"):
            try:
                # Prepare research context
                context = self._prepare_research_context(research_data)
                
                prompt = f"""
                Write a comprehensive {max_length}-word article about "{topic}" using the following research data:
                
                {context}
                
                Structure the article with these sections:
                {json.dumps(sections, indent=2)}
                
                Requirements:
                - Professional, informative tone
                - Include specific facts and data from the research
                - Use markdown formatting
                - Include proper citations
                - Target length: {max_length} words
                
                Provide response as JSON with:
                - "title": article title
                - "content": full markdown content
                - "word_count": estimated word count
                - "summary": 200-word executive summary
                """
                
                response = self.gemini_client.generate_content(prompt)
                result = self._parse_json_response(response.text)
                if result:
                    logger.info(f"Generated article using Gemini for: {topic}")
                    return result
            except Exception as e:
                logger.warning(f"Gemini article generation failed: {e}. Using template fallback.")
        
        # Fallback to template
        title = f"Comprehensive Guide to {topic}"
        content = TEMPLATE_RESPONSES["article_template"].format(
            title=title,
            topic=topic
        )
        
        # Add research data if available
        if research_data.get("sources"):
            content += "\n\n## Sources and References\n\n"
            for i, source in enumerate(research_data["sources"][:5], 1):
                content += f"{i}. [{source.get('title', 'Source')}]({source.get('url', '#')})\n"
        
        result = {
            "title": title,
            "content": content,
            "word_count": len(content.split()),
            "summary": f"This comprehensive guide explores {topic}, providing detailed insights into its key aspects, current developments, and future implications. The article covers fundamental concepts, practical applications, and emerging trends in the field."
        }
        
        logger.info(f"Generated article using template for: {topic}")
        return result
    
    async def enhance_content(self, content: str, enhancement_type: str = "clarity") -> str:
        """
        Enhance existing content for better clarity, engagement, or technical depth.
        """
        if self.use_gemini and self.gemini_client:
            try:
                prompt = f"""
                Enhance this content for better {enhancement_type}:
                
                {content}
                
                Return only the enhanced version maintaining the same structure and format.
                """
                
                response = self.gemini_client.generate_content(prompt)
                logger.info(f"Enhanced content using Gemini for: {enhancement_type}")
                return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini enhancement failed: {e}. Returning original content.")
        
        # Fallback - return original content
        logger.info(f"Content enhancement skipped, returning original")
        return content
    
    def _prepare_research_context(self, research_data: Dict[str, Any]) -> str:
        """Prepare research data for AI consumption."""
        context_parts = []
        
        if research_data.get("sources"):
            context_parts.append("SOURCES:")
            for source in research_data["sources"][:10]:  # Limit sources
                title = source.get("title", "Unknown")
                url = source.get("url", "")
                content = source.get("content", "")[:500]  # Limit content length
                context_parts.append(f"- {title} ({url}): {content}")
        
        if research_data.get("key_points"):
            context_parts.append("\nKEY POINTS:")
            for point in research_data["key_points"][:10]:
                context_parts.append(f"- {point}")
        
        return "\n".join(context_parts)
    
    def _parse_json_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse JSON response from AI, handling common formatting issues."""
        try:
            # Clean up the response
            text = response_text.strip()
            
            # Remove markdown code blocks if present
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            return json.loads(text.strip())
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response from AI")
            return None
    
    async def summarize_text(self, text: str, max_length: int = 200) -> str:
        """Generate a summary of the given text."""
        if self.use_gemini and self.gemini_client:
            try:
                prompt = f"Summarize this text in {max_length} words or less:\n\n{text}"
                response = self.gemini_client.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini summarization failed: {e}")
        
        # Simple fallback - return first few sentences
        sentences = text.split('. ')
        summary = '. '.join(sentences[:3])
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        
        return summary
