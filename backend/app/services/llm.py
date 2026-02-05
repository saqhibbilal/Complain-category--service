"""LLM service for Mistral API integration."""
from typing import Dict, List, Optional
from mistralai import Mistral
from app.config import settings
import logging
import time

logger = logging.getLogger(__name__)

# Initialize Mistral client
_client: Optional[Mistral] = None


def get_mistral_client() -> Mistral:
    """Get or initialize Mistral client (singleton pattern)."""
    global _client
    if _client is None:
        if not settings.MISTRAL_API_KEY:
            raise ValueError("MISTRAL_API_KEY is not set in environment variables")
        
        logger.info(f"Initializing Mistral client with model: {settings.MISTRAL_MODEL}")
        _client = Mistral(api_key=settings.MISTRAL_API_KEY)
        logger.info("Mistral client initialized successfully")
    return _client


def categorize_complaint(
    complaint_text: str,
    similar_complaints: Optional[List[str]] = None
) -> Dict[str, str]:
    """
    Categorize a complaint using Mistral API with RAG context.
    
    Args:
        complaint_text: The complaint text to categorize
        similar_complaints: List of similar complaint texts for context (RAG)
        
    Returns:
        Dictionary with product, sub_product, issue, sub_issue
    """
    client = get_mistral_client()
    
    # Build prompt with RAG context
    prompt = build_categorization_prompt(complaint_text, similar_complaints)
    
    try:
        response = client.chat.complete(
            model=settings.MISTRAL_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at categorizing consumer financial complaints. "
                               "Analyze the complaint and return ONLY a JSON object with keys: "
                               "product, sub_product, issue, sub_issue. "
                               "Use the provided similar complaints as reference for consistency."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower temperature for more consistent categorization
            response_format={"type": "json_object"}
        )
        
        # Parse response
        result = response.choices[0].message.content
        import json
        categories = json.loads(result)
        
        return {
            "product": categories.get("product", ""),
            "sub_product": categories.get("sub_product", ""),
            "issue": categories.get("issue", ""),
            "sub_issue": categories.get("sub_issue", "")
        }
        
    except Exception as e:
        logger.error(f"Error categorizing complaint: {e}")
        raise


def validate_category(
    complaint_text: str,
    product: str,
    sub_product: str
) -> bool:
    """
    Validate if the existing category is appropriate for the complaint.
    
    Args:
        complaint_text: The complaint text
        product: Existing product category
        sub_product: Existing sub-product category
        
    Returns:
        True if category is valid, False otherwise
    """
    client = get_mistral_client()
    
    prompt = f"""Review this consumer complaint and validate if the assigned categories are appropriate.

Complaint: {complaint_text[:500]}

Assigned Categories:
- Product: {product}
- Sub-product: {sub_product}

Respond with ONLY a JSON object: {{"is_valid": true/false, "reason": "brief explanation"}}
"""
    
    try:
        response = client.chat.complete(
            model=settings.MISTRAL_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a quality assurance expert for complaint categorization. "
                               "Return ONLY valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result.get("is_valid", False)
        
    except Exception as e:
        logger.error(f"Error validating category: {e}")
        # Default to True if validation fails (don't block processing)
        return True


def generate_summary(complaint_text: str) -> str:
    """
    Generate a concise summary of the complaint.
    
    Args:
        complaint_text: The complaint text
        
    Returns:
        Concise summary string
    """
    client = get_mistral_client()
    
    prompt = f"""Summarize this consumer complaint in 2-3 sentences, focusing on the main issue and impact.

Complaint:
{complaint_text[:2000]}

Summary:"""
    
    try:
        response = client.chat.complete(
            model=settings.MISTRAL_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at summarizing consumer complaints concisely."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=150
        )
        
        summary = response.choices[0].message.content.strip()
        return summary
        
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        # Return a simple fallback summary
        return complaint_text[:200] + "..." if len(complaint_text) > 200 else complaint_text


def build_categorization_prompt(
    complaint_text: str,
    similar_complaints: Optional[List[str]] = None
) -> str:
    """Build the prompt for categorization with RAG context."""
    prompt_parts = []
    
    if similar_complaints:
        prompt_parts.append("Here are similar complaints for reference:")
        for i, similar in enumerate(similar_complaints[:3], 1):  # Use top 3 similar
            prompt_parts.append(f"\nSimilar Complaint {i}:\n{similar[:300]}")
        prompt_parts.append("\n---\n")
    
    prompt_parts.append(f"Complaint to categorize:\n{complaint_text[:2000]}")
    prompt_parts.append("\n\nCategorize this complaint. Return JSON with: product, sub_product, issue, sub_issue")
    
    return "\n".join(prompt_parts)
