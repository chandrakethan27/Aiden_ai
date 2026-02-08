"""
Context-Aware Summary Agent
Generates concise summaries while preserving intent, constraints, and critical decisions
"""
from openai import OpenAI
from typing import Dict, Any, List
import json
import os


class SummaryAgent:
    """Agent responsible for generating context-aware summaries"""
    
    SYSTEM_MESSAGE = """You are a Summary Agent specialized in analyzing documents and creating concise, context-aware summaries.

Your task is to:
1. Read the provided document carefully
2. Extract the main intent and purpose
3. Identify all critical decisions mentioned or implied
4. Note any constraints, limitations, or requirements
5. Generate a concise summary (150-200 words) that preserves all essential information

You MUST respond with a valid JSON object in this exact format:
{
    "summary": "A concise summary of the document preserving intent and key points",
    "key_decisions": ["Decision 1", "Decision 2", ...],
    "constraints": ["Constraint 1", "Constraint 2", ...],
    "intent": "The primary purpose or goal of this document"
}

Focus on:
- What is being discussed or decided
- Why it matters (intent)
- What limitations or requirements exist
- What decisions have been made or need to be made

Be precise and factual. Do not add information not present in the document."""
    
    def __init__(self, llm_config: Dict[str, Any]):
        """
        Initialize the Summary Agent
        
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
        self.temperature = llm_config.get("temperature", 0.5)
        self.max_tokens = llm_config.get("max_tokens", 4096)
    
    def process_document(self, document_text: str) -> Dict[str, Any]:
        """
        Process a document and generate a summary
        
        Args:
            document_text: The document text to summarize
            
        Returns:
            Dictionary with summary, key decisions, and constraints
        """
        prompt = f"""Please analyze the following document and provide a structured summary:

DOCUMENT:
{document_text}

Remember to respond with a valid JSON object containing: summary, key_decisions, constraints, and intent."""
        
        try:
            print(f"[Summary Agent] Making API call to model: {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_MESSAGE},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            content = response.choices[0].message.content
            print(f"[Summary Agent] Received response: {content[:200]}...")
            result = self._extract_json(content)
            print(f"[Summary Agent] Parsed result: {result}")
            return result
            
        except Exception as e:
            error_msg = str(e)
            print(f"[Summary Agent] ERROR: {error_msg}")
            
            # Check for Rate Limit Error or 404
            if "429" in error_msg or "Rate limit" in error_msg:
                return {
                    "summary": "⚠️ System Error: API Rate Limit Exceeded. Please switch models.",
                    "key_decisions": [],
                    "constraints": ["API Quota Reached"],
                    "intent": "Error: Rate Limit"
                }
            
            if "404" in error_msg:
                return {
                    "summary": "⚠️ System Error: Model Not Found (404). The selected model is unavailable.",
                    "key_decisions": [],
                    "constraints": ["Model Unavailable"],
                    "intent": "Error: Model 404"
                }

            import traceback
            traceback.print_exc()
            return {
                "summary": f"Error processing document: {error_msg}",
                "key_decisions": [],
                "constraints": [],
                "intent": "Error occurred"
            }
    
    def process_chunks(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process multiple document chunks and synthesize a summary
        
        Args:
            chunks: List of document chunks with text
            
        Returns:
            Synthesized summary from all chunks
        """
        if len(chunks) == 1:
            return self.process_document(chunks[0]["text"])
        
        # Process each chunk
        chunk_summaries = []
        for chunk in chunks:
            summary = self.process_document(chunk["text"])
            chunk_summaries.append(summary)
        
        # Synthesize all chunk summaries
        synthesis_prompt = f"""You have analyzed a long document in {len(chunks)} parts. 
Here are the summaries from each part:

{json.dumps(chunk_summaries, indent=2)}

Please create a final synthesized summary that:
1. Combines insights from all parts
2. Removes redundancy
3. Preserves all unique key decisions and constraints
4. Maintains the overall intent

Respond with a valid JSON object in the same format."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_MESSAGE},
                    {"role": "user", "content": synthesis_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            content = response.choices[0].message.content
            return self._extract_json(content)
            
        except Exception as e:
            # Fallback: merge all chunk summaries
            return self._merge_summaries(chunk_summaries)
    
    def _extract_json(self, content: str) -> Dict[str, Any]:
        """Extract and parse JSON from response"""
        print(f"[Summary Agent] _extract_json called with content length: {len(content)}")
        print(f"[Summary Agent] Content preview: {content[:300]}")
        
        try:
            # Look for JSON in code blocks
            if "```json" in content:
                print("[Summary Agent] Found ```json marker")
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            elif "```" in content:
                print("[Summary Agent] Found ``` marker")
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            else:
                # Try to find JSON object directly
                print("[Summary Agent] No code blocks, looking for JSON object")
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                json_str = content[json_start:json_end]
            
            print(f"[Summary Agent] Extracted JSON string: {json_str[:200]}")
            result = json.loads(json_str)
            print(f"[Summary Agent] Successfully parsed JSON: {result}")
            
            # Ensure all required fields exist
            if "summary" not in result:
                result["summary"] = "Summary not available"
            if "key_decisions" not in result:
                result["key_decisions"] = []
            if "constraints" not in result:
                result["constraints"] = []
            if "intent" not in result:
                result["intent"] = "Intent not specified"
            
            print(f"[Summary Agent] Returning result with {len(result.get('key_decisions', []))} decisions")
            return result
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"[Summary Agent] JSON parsing failed: {str(e)}")
            # Fallback: create a basic summary from the content
            return {
                "summary": content[:500] if len(content) > 500 else content,
                "key_decisions": [],
                "constraints": [],
                "intent": "Unable to parse structured response"
            }
    
    def _merge_summaries(self, summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple summaries into one"""
        all_decisions = []
        all_constraints = []
        
        for s in summaries:
            all_decisions.extend(s.get("key_decisions", []))
            all_constraints.extend(s.get("constraints", []))
        
        return {
            "summary": " ".join([s.get("summary", "") for s in summaries])[:500],
            "key_decisions": list(set(all_decisions)),
            "constraints": list(set(all_constraints)),
            "intent": summaries[0].get("intent", "Unknown") if summaries else "Unknown"
        }
