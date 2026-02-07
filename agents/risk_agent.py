"""
Risk & Open-Issues Agent
Identifies unresolved questions, missing data, assumptions, and potential risks
"""
from openai import OpenAI
from typing import Dict, Any, List
import json


class RiskAgent:
    """Agent responsible for identifying risks and open issues"""
    
    SYSTEM_MESSAGE = """You are a Risk Analysis Agent specialized in identifying potential problems, gaps, and uncertainties in documents.

Your task is to:
1. Identify all unresolved questions or unclear points
2. Detect missing information or data gaps
3. Identify assumptions being made (explicit or implicit)
4. Flag potential risks, challenges, or concerns
5. Categorize risks by severity and type

You MUST respond with a valid JSON object in this exact format:
{
    "open_questions": [
        "Question or unclear point that needs resolution"
    ],
    "assumptions": [
        "Assumption being made (what is taken for granted)"
    ],
    "missing_data": [
        "Information that is needed but not provided"
    ],
    "risks": [
        {
            "title": "Brief risk title",
            "description": "Detailed description of the risk",
            "severity": "high|medium|low",
            "type": "technical|resource|timeline|scope|dependency|other",
            "mitigation": "Suggested mitigation if obvious, or 'To be determined'"
        }
    ]
}

Guidelines for identifying risks:
- HIGH severity: Could cause project failure, major delays, or significant issues
- MEDIUM severity: Could cause moderate problems or delays
- LOW severity: Minor concerns or nice-to-have clarifications

Types of risks:
- technical: Technology, implementation, or architecture concerns
- resource: People, budget, or capacity issues
- timeline: Schedule or deadline concerns
- scope: Unclear or changing requirements
- dependency: Reliance on external factors
- other: Any other type of risk

Look for:
- Questions that remain unanswered
- Decisions that haven't been made yet
- Information referenced but not provided
- Implicit assumptions about how things will work
- Potential bottlenecks or challenges
- Dependencies on uncertain factors
- Conflicting requirements or constraints

Be thorough and think critically. It's better to flag potential issues than miss them."""
    
    def __init__(self, llm_config: Dict[str, Any]):
        """
        Initialize the Risk Agent
        
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
        self.temperature = llm_config.get("temperature", 0.7)
        self.max_tokens = llm_config.get("max_tokens", 4096)
    
    def process_document(
        self, 
        document_text: str, 
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process a document and identify risks and open issues
        
        Args:
            document_text: The document text to analyze
            context: Optional context from other agents (summary, actions)
            
        Returns:
            Dictionary with open questions, assumptions, and risks
        """
        prompt = f"""Please analyze the following document and identify all risks, open questions, and assumptions:

DOCUMENT:
{document_text}
"""
        
        if context:
            prompt += f"""
ADDITIONAL CONTEXT:
{json.dumps(context, indent=2)}

Use this context to identify risks related to the summary insights and action items.
"""
        
        prompt += """
Extract specifically:
1. Potential risks (severity: high/medium/low)
2. Open questions/ambiguities
3. Missing information
4. Key assumptions made

LIMIT TO THE TOP 5 MOST CRITICAL RISKS ONLY. BE CONCISE.
Focus on high-impact items to ensure the response fits within limits.

Remember to respond with a valid JSON object containing open_questions, assumptions, missing_data, and risks."""
        
        try:
            print(f"[Risk Agent] Making API call to model: {self.model}")
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
            print(f"[Risk Agent] Received response: {content[:200]}...")
            result = self._extract_json(content)
            print(f"[Risk Agent] Parsed result with {len(result.get('risks', []))} risks")
            return result
            
        except Exception as e:
            print(f"[Risk Agent] ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "open_questions": [],
                "assumptions": [],
                "missing_data": [],
                "risks": []
            }
    
    def process_chunks(
        self, 
        chunks: List[Dict[str, Any]], 
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process multiple document chunks and combine risk analysis
        
        Args:
            chunks: List of document chunks with text
            context: Optional context from other agents
            
        Returns:
            Combined risk analysis from all chunks
        """
        all_questions = []
        all_assumptions = []
        all_missing_data = []
        all_risks = []
        
        for chunk in chunks:
            result = self.process_document(chunk["text"], context)
            all_questions.extend(result.get("open_questions", []))
            all_assumptions.extend(result.get("assumptions", []))
            all_missing_data.extend(result.get("missing_data", []))
            all_risks.extend(result.get("risks", []))
        
        # Deduplicate
        return {
            "open_questions": list(set(all_questions)),
            "assumptions": list(set(all_assumptions)),
            "missing_data": list(set(all_missing_data)),
            "risks": self._deduplicate_risks(all_risks)
        }
    
    def _deduplicate_risks(self, risks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate risks based on title similarity"""
        if len(risks) <= 1:
            return risks
        
        unique_risks = []
        seen_titles = set()
        
        for risk in risks:
            title_lower = risk.get("title", "").lower().strip()
            if title_lower and title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_risks.append(risk)
        
        return unique_risks
    
    def _extract_json(self, content: str) -> Dict[str, Any]:
        """Extract and parse JSON response"""
        print(f"[Risk Agent] _extract_json called with content length: {len(content)}")
        print(f"[Risk Agent] Content preview: {content[:300]}")
        
        try:
            # Look for JSON in code blocks
            if "```json" in content:
                print("[Risk Agent] Found ```json marker")
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            elif "```" in content:
                print("[Risk Agent] Found ``` marker")
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            else:
                # Try to find JSON object directly
                print("[Risk Agent] No code blocks, looking for JSON object")
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                json_str = content[json_start:json_end]
            
            print(f"[Risk Agent] Extracted JSON string: {json_str[:200]}")
            result = json.loads(json_str)
            print(f"[Risk Agent] Successfully parsed JSON")
            
            # Ensure all required fields exist
            if "open_questions" not in result:
                result["open_questions"] = []
            if "assumptions" not in result:
                result["assumptions"] = []
            if "missing_data" not in result:
                result["missing_data"] = []
            if "risks" not in result:
                result["risks"] = []
            
            # Validate risk objects
            validated_risks = []
            for risk in result["risks"]:
                if isinstance(risk, dict):
                    validated_risks.append({
                        "title": risk.get("title", "Untitled Risk"),
                        "description": risk.get("description", "No description"),
                        "severity": risk.get("severity", "medium"),
                        "type": risk.get("type", "other"),
                        "mitigation": risk.get("mitigation", "To be determined")
                    })
            result["risks"] = validated_risks
            
            print(f"[Risk Agent] Returning result with {len(result['risks'])} risks, {len(result['open_questions'])} questions")
            return result
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"[Risk Agent] JSON parsing failed: {str(e)}")
            return {
                "open_questions": [],
                "assumptions": [],
                "missing_data": [],
                "risks": []
            }
