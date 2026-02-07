"""
Document Orchestrator
Central coordination layer for managing multi-agent document processing
"""
from typing import Dict, Any, List, Callable
from .summary_agent import SummaryAgent
from .action_agent import ActionAgent
from .risk_agent import RiskAgent
from utils.document_processor import DocumentProcessor
from utils.config import Config


class DocumentOrchestrator:
    """Orchestrates the multi-agent document processing workflow"""
    
    def __init__(self, config: Config):
        """
        Initialize the orchestrator with all agents
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.document_processor = DocumentProcessor(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap
        )
        
        # Initialize agents with appropriate configurations
        self.summary_agent = SummaryAgent(config.get_agent_config("summary"))
        self.action_agent = ActionAgent(config.get_agent_config("action"))
        self.risk_agent = RiskAgent(config.get_agent_config("risk"))
        
        # Processing state
        self.current_status = {}
    
    def process_document(
        self, 
        document_text: str,
        progress_callback: Callable[[str, str], None] = None
    ) -> Dict[str, Any]:
        """
        Process a document through all agents with coordination
        
        Args:
            document_text: The document text to process
            progress_callback: Optional callback for progress updates (agent_name, status)
            
        Returns:
            Dictionary with results from all agents
        """
        # Step 1: Process and chunk the document
        self._update_status("preprocessing", "processing", progress_callback)
        processed_doc = self.document_processor.process_document(document_text)
        chunks = processed_doc["chunks"]
        
        # Step 2: Summary Agent (runs first to provide context)
        self._update_status("summary", "processing", progress_callback)
        if len(chunks) == 1:
            summary_result = self.summary_agent.process_document(chunks[0]["text"])
        else:
            summary_result = self.summary_agent.process_chunks(chunks)
        self._update_status("summary", "complete", progress_callback)
        
        # Step 3: Action Agent (uses summary as context)
        self._update_status("action", "processing", progress_callback)
        context = {
            "summary": summary_result.get("summary", ""),
            "intent": summary_result.get("intent", ""),
            "key_decisions": summary_result.get("key_decisions", [])
        }
        
        if len(chunks) == 1:
            action_result = self.action_agent.process_document(chunks[0]["text"], context)
        else:
            action_result = self.action_agent.process_chunks(chunks, context)
        self._update_status("action", "complete", progress_callback)
        
        # Step 4: Risk Agent (uses summary and actions as context)
        self._update_status("risk", "processing", progress_callback)
        risk_context = {
            **context,
            "action_items": action_result
        }
        
        if len(chunks) == 1:
            risk_result = self.risk_agent.process_document(chunks[0]["text"], risk_context)
        else:
            risk_result = self.risk_agent.process_chunks(chunks, risk_context)
        self._update_status("risk", "complete", progress_callback)
        
        # Aggregate results
        return {
            "summary": summary_result,
            "actions": action_result,
            "risks": risk_result,
            "metadata": {
                "document_length": processed_doc["metadata"]["total_words"],
                "total_tokens": processed_doc["metadata"]["total_tokens"],
                "num_chunks": processed_doc["num_chunks"],
                "chunking_required": processed_doc["requires_chunking"]
            }
        }
    
    def _update_status(
        self, 
        agent_name: str, 
        status: str, 
        callback: Callable[[str, str], None] = None
    ):
        """Update processing status and call callback if provided"""
        self.current_status[agent_name] = status
        if callback:
            callback(agent_name, status)
    
    def get_status(self) -> Dict[str, str]:
        """Get current processing status of all agents"""
        return self.current_status.copy()
    
    def validate_configuration(self) -> tuple[bool, str]:
        """
        Validate that the orchestrator is properly configured
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.config.validate():
            return False, "Invalid configuration: Missing API key or model settings"
        
        return True, ""
