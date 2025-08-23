"""
Enhanced backend for article generation with AI integration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import uuid
import os
from datetime import datetime
from typing import Dict, Any
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Content Creation API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo
jobs_storage = {}

# Initialize AI services
gemini_available = False
gemini_model = None
try:
    import google.generativeai as genai
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv(dotenv_path="../.env")
    
    api_key = os.getenv('GEMINI_API_KEY')
    model_name = os.getenv('GEMINI_MODEL', 'gemini-pro')
    
    # Map model names to correct ones
    model_mapping = {
        'gemini-2.5-pro': 'gemini-1.5-pro',  # Map to available model
        'gemini-2.0-pro': 'gemini-1.5-pro',
        'gemini-pro': 'gemini-pro'
    }
    
    actual_model = model_mapping.get(model_name, 'gemini-pro')
    
    if api_key:
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel(actual_model)
        gemini_available = True
        logger.info(f"✅ Gemini AI initialized successfully")
        logger.info(f"   Requested model: {model_name}")
        logger.info(f"   Using model: {actual_model}")
    else:
        logger.info("ℹ️  No Gemini API key found - using template fallbacks")
except Exception as e:
    logger.warning(f"⚠️  Gemini AI initialization failed: {e}")
    logger.info("ℹ️  Using template fallbacks")

class ArticleRequest(BaseModel):
    topic: str
    desired_depth: str = "intermediate"
    max_length: int = 5000
    include_visuals: bool = True

async def generate_article_with_ai(topic: str, depth: str) -> Dict[str, Any]:
    """Generate article using AI or templates."""
    
    if gemini_available and gemini_model:
        try:
            logger.info(f"🤖 Generating article with Gemini AI for: {topic}")
            
            prompt = f"""
            Write a comprehensive, professional technical article about "{topic}" for {depth} readers.
            
            Requirements:
            - 2000-3000 words
            - Include practical examples and use cases
            - Use proper markdown formatting with headers
            - Include an executive summary
            - Be technically accurate and informative
            - Target audience: {depth} level
            
            Structure:
            1. Executive Summary
            2. Introduction  
            3. Key Concepts
            4. Technical Implementation
            5. Best Practices
            6. Real-world Applications
            7. Challenges and Solutions
            8. Future Outlook
            9. Conclusion
            
            Write in markdown format.
            """
            
            response = gemini_model.generate_content(prompt)
            if response and response.text:
                content = response.text
                
                logger.info(f"✅ Successfully generated AI article for: {topic}")
                return {
                    "title": f"Complete Guide to {topic}",
                    "content": content,
                    "summary": f"This comprehensive guide explores {topic}, providing detailed insights for {depth} readers with practical examples and real-world applications.",
                    "word_count": len(content.split()),
                    "generation_method": "gemini_ai",
                    "ai_powered": True
                }
            else:
                logger.warning("⚠️ Gemini returned empty response, using template fallback")
            
        except Exception as e:
            logger.warning(f"⚠️ Gemini AI generation failed: {e}. Using template fallback.")
    else:
        logger.info(f"ℹ️ Gemini not available, using template for: {topic}")
    
    # Template fallback
    logger.info(f"📝 Generating article with template for: {topic}")
    
    article_content = f"""# Complete Guide to {topic}

## Executive Summary

This comprehensive guide explores {topic}, providing insights into its key concepts, applications, and future potential. Through detailed analysis, we examine how {topic} impacts various industries and what developments we can expect in the coming years.

## Introduction

{topic} has become increasingly important in today's technological landscape. This article provides a thorough exploration of the subject, designed for {depth} readers who want to understand both the fundamentals and practical applications.

## Key Concepts

Understanding {topic} requires familiarity with several fundamental concepts:

### Core Principles
- **Foundation**: The underlying principles that define {topic}
- **Architecture**: How different components work together
- **Methodology**: Best practices and approaches
- **Standards**: Industry standards and guidelines

### Technical Components
- **Implementation**: Practical implementation strategies
- **Tools and Technologies**: Essential tools and platforms
- **Integration**: How to integrate with existing systems
- **Performance**: Optimization and performance considerations

## Technical Implementation

### Getting Started
To begin working with {topic}, you'll need to understand the basic setup and configuration requirements. This includes:

1. **Environment Setup**: Preparing your development environment
2. **Prerequisites**: Required knowledge and tools
3. **Installation**: Step-by-step installation process
4. **Configuration**: Essential configuration settings

### Implementation Strategy
A successful implementation of {topic} typically follows these phases:

1. **Planning Phase**: Requirements analysis and design
2. **Development Phase**: Core implementation and testing
3. **Deployment Phase**: Production deployment and monitoring
4. **Maintenance Phase**: Ongoing support and optimization

## Best Practices

### Design Principles
- **Scalability**: Design for growth and increased load
- **Maintainability**: Write clean, documented code
- **Security**: Implement proper security measures
- **Performance**: Optimize for speed and efficiency

### Common Patterns
- **Modular Design**: Break complex systems into manageable modules
- **Error Handling**: Implement comprehensive error handling
- **Testing**: Include unit, integration, and performance tests
- **Documentation**: Maintain clear, up-to-date documentation

## Real-world Applications

{topic} has practical applications across numerous industries:

### Business Operations
- **Process Automation**: Streamlining business processes
- **Data Analysis**: Extracting insights from data
- **Decision Support**: Supporting strategic decision-making
- **Efficiency Gains**: Improving operational efficiency

### Technology Development
- **Software Development**: Building robust applications
- **System Integration**: Connecting disparate systems
- **Platform Development**: Creating scalable platforms
- **Innovation**: Enabling new technological capabilities

### Industry-Specific Uses
- **Healthcare**: Improving patient care and outcomes
- **Finance**: Enhancing financial services and security
- **Education**: Supporting learning and knowledge transfer
- **Manufacturing**: Optimizing production processes

## Challenges and Solutions

### Common Challenges
1. **Complexity**: Managing system complexity
2. **Scalability**: Handling growth and increased demand
3. **Integration**: Connecting with legacy systems
4. **Security**: Protecting against threats
5. **Performance**: Maintaining optimal performance

### Proven Solutions
1. **Modular Architecture**: Use microservices and modular design
2. **Cloud Infrastructure**: Leverage cloud scalability
3. **API Design**: Create well-designed APIs for integration
4. **Security Frameworks**: Implement comprehensive security
5. **Performance Monitoring**: Continuous performance optimization

## Implementation Considerations

### Technical Requirements
- **Hardware**: Minimum and recommended hardware specifications
- **Software**: Required software dependencies and versions
- **Network**: Network requirements and considerations
- **Storage**: Data storage and backup requirements

### Resource Planning
- **Team Skills**: Required expertise and training needs
- **Timeline**: Realistic project timelines and milestones
- **Budget**: Cost considerations and resource allocation
- **Risk Management**: Identifying and mitigating risks

## Future Outlook

The future of {topic} looks promising with several exciting developments:

### Emerging Trends
- **Automation**: Increased automation and AI integration
- **Cloud-Native**: Shift towards cloud-native architectures
- **Edge Computing**: Distributed processing capabilities
- **AI/ML Integration**: Enhanced intelligence and learning

### Market Evolution
- **Adoption Rates**: Increasing adoption across industries
- **Standardization**: Development of industry standards
- **Tool Ecosystem**: Growing ecosystem of tools and platforms
- **Community Growth**: Expanding developer and user communities

### Innovation Areas
- **Performance**: Continued performance improvements
- **Usability**: Enhanced user experience and accessibility
- **Integration**: Better integration capabilities
- **Scalability**: Improved scalability and efficiency

## Getting Started

### Learning Path
1. **Fundamentals**: Master the basic concepts
2. **Hands-on Practice**: Build practical projects
3. **Advanced Topics**: Explore advanced features
4. **Community Engagement**: Join communities and forums

### Resources
- **Documentation**: Official documentation and guides
- **Tutorials**: Step-by-step tutorials and examples
- **Community**: Forums, discussions, and support groups
- **Training**: Formal training and certification programs

## Conclusion

{topic} represents a significant opportunity for organizations and individuals looking to improve their capabilities and outcomes. With proper understanding and implementation, it can provide substantial benefits and competitive advantages.

Key takeaways:
- Start with a solid understanding of fundamentals
- Follow best practices and proven patterns
- Plan for scalability and maintainability
- Stay updated with emerging trends and developments
- Engage with the community for support and learning

As the field continues to evolve, staying informed about developments and best practices will be essential for maximizing the value and potential of {topic}. The investment in learning and implementing {topic} will likely yield significant returns in terms of efficiency, capability, and competitive advantage.

---

*This article provides a comprehensive overview of {topic} for {depth} readers. For the most current information and specific implementation details, please consult the latest documentation and community resources.*
"""

    return {
        "title": f"Complete Guide to {topic}",
        "content": article_content,
        "summary": f"This comprehensive guide explores {topic}, covering key concepts, implementation strategies, best practices, and real-world applications for {depth} readers.",
        "word_count": len(article_content.split()),
        "generation_method": "template",
        "ai_powered": False
    }

@app.get("/")
def read_root():
    return {"message": "Content Creation API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/v1/jobs")
async def create_job(request: ArticleRequest):
    job_id = str(uuid.uuid4())
    
    logger.info(f"🚀 Creating job {job_id} for topic: {request.topic}")
    
    # Generate article using AI or templates
    article_data = await generate_article_with_ai(request.topic, request.desired_depth)
    
    job_data = {
        "job_id": job_id,
        "topic": request.topic,
        "status": "completed",
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "result": {
            "success": True,
            "article": article_data,
            "metadata": {
                "topic": request.topic,
                "depth": request.desired_depth,
                "generation_method": article_data["generation_method"],
                "ai_powered": article_data.get("ai_powered", False),
                "generated_at": datetime.utcnow().isoformat()
            }
        }
    }
    
    jobs_storage[job_id] = job_data
    
    logger.info(f"✅ Job {job_id} completed successfully")
    
    return {
        "job_id": job_id,
        "status": "completed",
        "topic": request.topic,
        "created_at": job_data["created_at"],
        "estimated_completion": "Completed"
    }

@app.get("/v1/jobs/{job_id}")
def get_job(job_id: str):
    if job_id in jobs_storage:
        return jobs_storage[job_id]
    else:
        return {"error": "Job not found", "job_id": job_id}

@app.get("/v1/jobs")
def list_jobs():
    return {
        "jobs": list(jobs_storage.values()),
        "total": len(jobs_storage),
        "has_more": False
    }

if __name__ == "__main__":
    print("Starting Content Creation API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
