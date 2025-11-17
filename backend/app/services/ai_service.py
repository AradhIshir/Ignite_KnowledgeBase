"""AI service for question-answering using OpenAI and Supabase."""
import os
import logging
from typing import List, Dict, Any, Optional
from supabase import Client

from app.utils.ai_summarization import call_openai_api

logger = logging.getLogger(__name__)


def search_relevant_articles(
    supabase: Client,
    question: str,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Search for articles relevant to the user's question.
    
    Args:
        supabase: Supabase client instance
        question: User's question
        limit: Maximum number of articles to return
        
    Returns:
        List of relevant articles with id, summary, topics, and key_points
    """
    try:
        logger.info(f"Searching articles for question: {question[:50]}...")
        
        # Extract potential keywords from the question (remove common stop words)
        question_lower = question.lower()
        stop_words = {'what', 'is', 'the', 'of', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'about', 'tell', 'me', 'show', 'status', 'latest', 'updates', 'information'}
        question_words = [word.strip() for word in question_lower.split() if word.strip() and word not in stop_words]
        keywords = [word for word in question_words if len(word) > 2]  # Lower threshold to 2
        
        # If no keywords after filtering, use all words longer than 2 chars
        if not keywords:
            keywords = [word.strip() for word in question_lower.split() if len(word.strip()) > 2]
        
        logger.info(f"Extracted keywords: {keywords}")
        
        # Get more articles to search through (increase limit significantly)
        query = supabase.table('knowledge_items').select(
            'id, summary, topics, key_points, raw_text, source, created_at'
        ).order('created_at', desc=True).limit(50)  # Get more articles to search
        
        # Execute query
        logger.debug("Executing Supabase query...")
        response = query.execute()
        articles = response.data if response.data else []
        logger.info(f"Found {len(articles)} articles from database")
        
        # Score and filter articles based on relevance
        scored_articles = []
        for article in articles:
            score = 0
            summary = (article.get('summary') or '').lower()
            topics = article.get('topics') or []
            key_points = article.get('key_points') or []
            
            # Check if any keyword appears in summary
            for keyword in keywords:
                if keyword in summary:
                    score += 2
                # Check if keyword appears in topics
                if topics:
                    if isinstance(topics, list):
                        if any(keyword in str(topic).lower() for topic in topics):
                            score += 3
                    elif isinstance(topics, str):
                        if keyword in topics.lower():
                            score += 3
                # Check if keyword appears in key_points
                if key_points:
                    if isinstance(key_points, list):
                        if any(keyword in str(point).lower() for point in key_points):
                            score += 2
                    elif isinstance(key_points, str):
                        if keyword in key_points.lower():
                            score += 2
            
            # Also check if question words appear in summary
            question_words = set(question_lower.split())
            summary_words = set(summary.split())
            common_words = question_words.intersection(summary_words)
            if len(common_words) > 0:
                score += len(common_words)
            
            if score > 0:
                scored_articles.append((score, article))
        
        # Sort by score (descending) and return top results
        scored_articles.sort(key=lambda x: x[0], reverse=True)
        result = [article for _, article in scored_articles[:limit]]
        logger.info(f"Returning {len(result)} relevant articles (from {len(scored_articles)} scored articles)")
        
        # Log top scores for debugging
        if scored_articles:
            top_scores = [score for score, _ in scored_articles[:5]]
            logger.info(f"Top 5 scores: {top_scores}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error searching articles: {str(e)}", exc_info=True)
        return []


def format_articles_for_prompt(articles: List[Dict[str, Any]]) -> str:
    """
    Format articles into a context string for the OpenAI prompt.
    
    Args:
        articles: List of article dictionaries
        
    Returns:
        Formatted string with article summaries
    """
    if not articles:
        return "No relevant articles found in the knowledge base."
    
    formatted = []
    for i, article in enumerate(articles, 1):
        summary = article.get('summary', 'No summary available')
        topics = article.get('topics', [])
        key_points = article.get('key_points', [])
        raw_text = article.get('raw_text', '')
        source = article.get('source', 'Unknown')
        
        article_text = f"=== Article {i} ===\n"
        article_text += f"Title/Summary: {summary}\n"
        
        if topics:
            if isinstance(topics, list):
                topics_str = ', '.join(str(t) for t in topics)
            else:
                topics_str = str(topics)
            article_text += f"Topics/Keywords: {topics_str}\n"
        
        if key_points:
            if isinstance(key_points, list):
                article_text += f"Key Points:\n"
                for j, kp in enumerate(key_points, 1):
                    article_text += f"  {j}. {kp}\n"
            else:
                article_text += f"Key Points: {key_points}\n"
        
        # Include a snippet of raw_text if available (first 300 chars to keep prompt shorter)
        if raw_text:
            raw_text_snippet = raw_text[:300] if len(raw_text) > 300 else raw_text
            article_text += f"Content: {raw_text_snippet}...\n" if len(raw_text) > 300 else f"Content: {raw_text_snippet}\n"
        
        article_text += f"Source: {source}\n"
        article_text += f"Article ID: {article.get('id')}\n"
        
        formatted.append(article_text)
    
    return "\n\n".join(formatted)


def generate_ai_answer(
    question: str,
    articles: List[Dict[str, Any]]
) -> Optional[str]:
    """
    Generate an AI-powered answer using OpenAI.
    
    Args:
        question: User's question
        articles: List of relevant articles
        
    Returns:
        AI-generated answer or None if generation fails
    """
    # Format articles for context
    articles_context = format_articles_for_prompt(articles)
    
    # Create system message
    system_message = (
        "You are an AI assistant for a team knowledge base application. "
        "Your task is to find articles matching the user's question and provide a formatted list with links. "
        "Always provide article titles and links in Markdown format. "
        "If no articles match, respond with exactly: 'I do not have information for this.'"
    )
    
    # Create user prompt with article URLs
    article_list_with_urls = []
    for i, article in enumerate(articles, 1):
        article_id = article.get('id')
        article_url = get_article_url(article_id)
        summary = article.get('summary', 'No title')
        topics = article.get('topics', [])
        key_points = article.get('key_points', [])
        
        article_info = f"Article {i}:\n"
        article_info += f"Title: {summary}\n"
        article_info += f"URL: {article_url}\n"
        
        if topics:
            topics_str = ', '.join(topics) if isinstance(topics, list) else str(topics)
            article_info += f"Topics/Keywords: {topics_str}\n"
        
        if key_points:
            if isinstance(key_points, list) and len(key_points) > 0:
                article_info += f"Key Points: {', '.join(str(kp) for kp in key_points[:3])}\n"  # First 3 key points
            else:
                article_info += f"Key Points: {key_points}\n"
        
        article_list_with_urls.append(article_info)
    
    articles_context_with_urls = "\n\n".join(article_list_with_urls)
    
    # Create user prompt
    prompt = f"""You are an AI assistant for a team knowledge base application.

Your tasks:

1. Receive a user's natural language question containing a keyword (e.g., "What is the status of Dashboard?").
2. Search the provided list of articles (including titles, summaries, and keywords) for matches related to the user's keyword or topic.
3. Output a concise response:
   - List the titles of all matching articles (1–2 lines per article).
   - For each article, provide a clickable link (URL) to view the full article.
   - Optionally add a one-line summary or highlight for each suggested article.

Format your answer with Markdown links:
- `[Article Title](Article URL) — Summary or status`

Here are the available articles:

{articles_context_with_urls}

User question: "{question}"

Provide a relevant results list. If articles match the question, format them as Markdown links. If no articles match, respond with exactly: 'I do not have information for this.'"""
    
    # Call OpenAI API with increased timeout
    logger.info(f"Calling OpenAI API with {len(articles)} articles, prompt length: {len(prompt)}")
    answer = call_openai_api(
        prompt=prompt,
        system_message=system_message,
        model='gpt-4o-mini',
        temperature=0.3,
        max_tokens=250,
        timeout=45  # Increased timeout
    )
    
    if answer:
        logger.info(f"OpenAI API returned answer (length: {len(answer)})")
    else:
        logger.warning("OpenAI API returned None - check logs for errors")
    
    return answer


def get_article_url(article_id: str, base_url: str = "http://localhost:3000") -> str:
    """
    Generate a URL for an article.
    
    Args:
        article_id: Article ID
        base_url: Base URL of the frontend application
        
    Returns:
        Full URL to the article
    """
    return f"{base_url}/app/items/{article_id}"


def is_rejection_answer(answer: str) -> bool:
    """
    Check if the answer is a rejection message (irrelevant or no information).
    
    Args:
        answer: The AI-generated answer
        
    Returns:
        True if the answer is a rejection, False otherwise
    """
    if not answer:
        return False
    
    answer_lower = answer.lower().strip()
    
    # Check for irrelevant question response
    irrelevant_phrases = [
        'please ask a relevant question',
        'ask a relevant question',
        'irrelevant question',
        'not relevant'
    ]
    
    # Check for no information response
    no_info_phrases = [
        'i do not have information',
        'do not have information',
        'no information',
        'information not found',
        'no relevant information'
    ]
    
    # Check if answer contains rejection phrases
    for phrase in irrelevant_phrases:
        if phrase in answer_lower:
            return True
    
    for phrase in no_info_phrases:
        if phrase in answer_lower:
            return True
    
    return False


def normalize_rejection_answer(answer: str) -> str:
    """
    Normalize rejection answers to standard messages.
    
    Args:
        answer: The AI-generated answer
        
    Returns:
        Normalized rejection message or original answer
    """
    if not answer:
        return answer
    
    answer_lower = answer.lower().strip()
    
    # Check for irrelevant question response
    irrelevant_phrases = [
        'please ask a relevant question',
        'ask a relevant question',
        'irrelevant question',
        'not relevant'
    ]
    
    # Check for no information response
    no_info_phrases = [
        'i do not have information',
        'do not have information',
        'no information',
        'information not found',
        'no relevant information'
    ]
    
    # Normalize to standard messages
    for phrase in irrelevant_phrases:
        if phrase in answer_lower:
            return 'Please ask a relevant question.'
    
    for phrase in no_info_phrases:
        if phrase in answer_lower:
            return 'I do not have information for this.'
    
    return answer


def process_ai_question(
    supabase: Client,
    question: str
) -> Dict[str, Any]:
    """
    Process an AI question: search articles, generate answer, and return results.
    
    Args:
        supabase: Supabase client instance
        question: User's question
        
    Returns:
        Dictionary with answer, relevant_articles, and article_links
    """
    try:
        logger.info(f"Processing AI question: {question[:50]}...")
        
        # Search for relevant articles (limit to top 3 for faster processing)
        articles = search_relevant_articles(supabase, question, limit=3)
        
        # If no articles found, return appropriate message
        if not articles:
            logger.info("No articles found, returning 'no information' message")
            return {
                'answer': 'I do not have information for this.',
                'relevant_articles': [],
                'article_links': []
            }
        
        # Generate AI answer with fallback
        logger.info("Generating AI answer...")
        answer = generate_ai_answer(question, articles)
        
        if not answer:
            logger.warning("AI answer generation returned None, using fallback")
            # Fallback: Create markdown-formatted answer from articles
            if articles:
                answer_lines = []
                for i, article in enumerate(articles, 1):
                    article_id = article.get('id')
                    article_url = get_article_url(article_id)
                    summary = article.get('summary', 'Untitled Article')
                    topics = article.get('topics', [])
                    key_points = article.get('key_points', [])
                    
                    # Create markdown link
                    link_text = f"[{summary}]({article_url})"
                    
                    # Add summary/status
                    status_parts = []
                    if topics:
                        topics_str = ', '.join(topics) if isinstance(topics, list) else str(topics)
                        status_parts.append(f"Topics: {topics_str}")
                    if key_points and isinstance(key_points, list) and len(key_points) > 0:
                        status_parts.append(f"Key point: {key_points[0]}")
                    
                    status = " — " + ". ".join(status_parts) if status_parts else ""
                    answer_lines.append(f"{link_text}{status}")
                
                answer = "\n".join(answer_lines)
            else:
                answer = (
                    "I couldn't generate an answer at this time. "
                    "Please try rephrasing your question or check back later."
                )
        else:
            # Normalize rejection answers
            answer = normalize_rejection_answer(answer)
            logger.info(f"AI answer generated: {answer[:100]}...")
        
        # Check if answer is a rejection
        is_rejection = is_rejection_answer(answer)
        
        # Always create article links if we have articles (the AI response may contain markdown links)
        article_links = []
        if articles:
            for article in articles:
                article_links.append({
                    'id': article.get('id'),
                    'title': article.get('summary', 'Untitled Article'),
                    'url': get_article_url(article.get('id'))
                })
        
        logger.info("Successfully processed AI question")
        return {
            'answer': answer,
            'relevant_articles': [
                {
                    'id': article.get('id'),
                    'title': article.get('summary', 'Untitled Article'),
                    'topics': article.get('topics', []),
                    'source': article.get('source', 'Unknown')
                }
                for article in articles
            ] if not is_rejection else [],
            'article_links': article_links
        }
    except Exception as e:
        logger.error(f"Error processing AI question: {str(e)}", exc_info=True)
        raise

