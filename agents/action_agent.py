"""
Action & Dependency Extraction Agent
Extracts actionable tasks with dependencies, owners, and deadlines
"""
from openai import OpenAI
from typing import Dict, Any, List
import json
import re


class ActionAgent:
    """Agent responsible for extracting action items with metadata"""
    
    SYSTEM_MESSAGE = """You are an Action Extraction Agent specialized in identifying actionable tasks from documents.

Your task is to:
1. Read the document carefully
2. Identify all explicit and implicit action items
3. Extract or infer task owners (people or roles responsible)
4. Extract or infer deadlines (dates, timeframes, or relative timing)
5. Identify dependencies between tasks (what must be done before what)
6. Structure each action item with complete metadata

You MUST respond with a valid JSON array of action items in this exact format:
[
    {
        "task": "Clear description of what needs to be done",
        "owner": "Person/role responsible (or 'Not specified')",
        "deadline": "Specific date or timeframe (or 'Not specified')",
        "dependencies": ["Task ID or description of prerequisite tasks"],
        "priority": "high|medium|low",
        "status": "pending|in-progress|blocked"
    }
]

Guidelines:
- Extract ONLY actionable items (things that need to be done)
- Be specific and clear in task descriptions
- If owner/deadline not mentioned, use "Not specified"
- Dependencies can be empty array [] if task is independent
- Infer priority from context (urgency, importance, consequences)
- Status is usually "pending" unless document indicates otherwise
- Include both explicit tasks ("John will do X") and implicit ones ("We need to verify Y")

Be thorough but precise. Do not invent tasks not implied by the document."""
    
    def __init__(self, llm_config: Dict[str, Any]):
        """
        Initialize the Action Agent
        
        Args:
            llm_config: LLM configuration with API key and model settings
        """
        config = llm_config["config_list"][0]
        
        # Initialize OpenAI client with optional base_url for OpenRouter
        client_kwargs = {"api_key": config["api_key"]}
        if "base_url" in config:
            client_kwargs["base_url"] = config["base_url"]
        
        self.client = OpenAI(**client_kwargs)
        self.model = config["model"]
        self.temperature = llm_config.get("temperature", 0.3)
        self.max_tokens = llm_config.get("max_tokens", 4096)
    
    def process_document(self, document_text: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Process a document and extract action items
        
        Args:
            document_text: The document text to analyze
            context: Optional context from other agents (e.g., summary)
            
        Returns:
            List of action items with metadata
        """
        prompt = f"""
Analyze the following document and identify actionable tasks:

DOCUMENT:
{document_text}

Extract specifically:
- Actionable tasks
- Owners (defaults to 'Unassigned')
- deadlines
- Dependencies
- Priority (high/medium/low)

LIMIT TO THE TOP 5 MOST CRITICAL ACTIONS ONLY.
KEEP DESCRIPTIONS SHORT (under 15 words).
Focus on high-impact items to ensure the response fits within limits.

Remember to respond with a valid JSON array of action items."""
        
        if context:
            prompt += f"""

ADDITIONAL CONTEXT (from summary):
{json.dumps(context, indent=2)}

Use this context to better understand the document's intent and identify implicit actions."""
        
        prompt += "\n\nRemember to respond with a valid JSON array of action items."
        
        try:
            print(f"[Action Agent] Making API call to model: {self.model}")
            print(f"[Action Agent] Prompt length: {len(prompt)} characters")
            print(f"[Action Agent] Context provided: {bool(context)}")
            print(f"[Action Agent] Temperature: {self.temperature}, Max tokens: {self.max_tokens}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_MESSAGE},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            print(f"[Action Agent] Response object: {response}")
            print(f"[Action Agent] Finish reason: {response.choices[0].finish_reason}")
            
            content = response.choices[0].message.content
            print(f"[Action Agent] Content type: {type(content)}")
            print(f"[Action Agent] Content is None: {content is None}")
            print(f"[Action Agent] Received response: {content[:200] if content else 'EMPTY/NULL'}...")
            
            result = self._extract_json(content if content else "[]")
            print(f"[Action Agent] Parsed {len(result)} action items")
            return result
            
        except Exception as e:
            print(f"[Action Agent] ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def process_chunks(self, chunks: List[Dict[str, Any]], context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Process multiple document chunks and combine action items
        
        Args:
            chunks: List of document chunks with text
            context: Optional context from other agents
            
        Returns:
            Combined list of action items from all chunks
        """
        all_actions = []
        
        for chunk in chunks:
            actions = self.process_document(chunk["text"], context)
            all_actions.extend(actions)
        
        # Deduplicate similar actions
        deduplicated = self._deduplicate_actions(all_actions)
        
        return deduplicated
    
    def _deduplicate_actions(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate or very similar action items"""
        if len(actions) <= 1:
            return actions
        
        unique_actions = []
        seen_tasks = set()
        
        for action in actions:
            task_lower = action.get("task", "").lower().strip()
            
            # Simple deduplication based on task similarity
            if task_lower and task_lower not in seen_tasks:
                seen_tasks.add(task_lower)
                unique_actions.append(action)
        
        return unique_actions
    
    def _extract_json(self, content: str) -> List[Dict[str, Any]]:
        """Extract and parse JSON response"""
        print(f"[Action Agent] _extract_json called with content length: {len(content)}")
        print(f"[Action Agent] Content preview: {content[:300]}")
        
        try:
            # Look for JSON in code blocks
            if "```json" in content:
                print("[Action Agent] Found ```json marker")
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            elif "```" in content:
                print("[Action Agent] Found ``` marker")
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            else:
                # Try to find JSON array directly
                print("[Action Agent] No code blocks, looking for JSON array")
                json_start = content.find("[")
                json_end = content.rfind("]") + 1
                json_str = content[json_start:json_end]
            
            print(f"[Action Agent] Extracted JSON string: {json_str[:200]}")
            result = json.loads(json_str)
            print(f"[Action Agent] Successfully parsed JSON, type: {type(result)}")
            
            # Ensure it's a list
            if not isinstance(result, list):
                print(f"[Action Agent] Converting single object to list")
                result = [result]
            
            # Validate and normalize each action item
            normalized = []
            for action in result:
                if isinstance(action, dict):
                    normalized.append({
                        "task": action.get("task", "Unspecified task"),
                        "owner": action.get("owner", "Not specified"),
                        "deadline": action.get("deadline", "Not specified"),
                        "dependencies": action.get("dependencies", []),
                        "priority": action.get("priority", "medium"),
                        "status": action.get("status", "pending")
                    })
            
            print(f"[Action Agent] Returning {len(normalized)} normalized actions")
            return normalized
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"[Action Agent] JSON parsing failed: {str(e)}")
            return []
