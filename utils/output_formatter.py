"""
Output formatting utilities for structured results
"""
import json
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime


class OutputFormatter:
    """Formats agent outputs into structured JSON and display tables"""
    
    @staticmethod
    def validate_summary(summary_data: Dict[str, Any]) -> bool:
        """Validate summary output structure"""
        required_fields = ["summary", "key_decisions", "constraints"]
        return all(field in summary_data for field in required_fields)
    
    @staticmethod
    def validate_actions(actions_data: List[Dict[str, Any]]) -> bool:
        """Validate action items output structure"""
        if not isinstance(actions_data, list):
            return False
        
        required_fields = ["task", "owner", "deadline", "dependencies"]
        for action in actions_data:
            if not all(field in action for field in required_fields):
                return False
        return True
    
    @staticmethod
    def validate_risks(risks_data: Dict[str, Any]) -> bool:
        """Validate risks output structure"""
        required_fields = ["open_questions", "assumptions", "risks"]
        return all(field in risks_data for field in required_fields)
    
    @staticmethod
    def format_summary_for_display(summary_data: Dict[str, Any]) -> str:
        """Format summary data for Streamlit display"""
        output = []
        
        if "summary" in summary_data:
            output.append("### Summary\n")
            output.append(summary_data["summary"])
            output.append("\n")
        
        if "key_decisions" in summary_data and summary_data["key_decisions"]:
            output.append("\n### Key Decisions\n")
            for i, decision in enumerate(summary_data["key_decisions"], 1):
                output.append(f"{i}. {decision}")
            output.append("\n")
        
        if "constraints" in summary_data and summary_data["constraints"]:
            output.append("\n### Critical Constraints\n")
            for i, constraint in enumerate(summary_data["constraints"], 1):
                output.append(f"{i}. {constraint}")
        
        return "\n".join(output)
    
    @staticmethod
    def format_actions_as_dataframe(actions_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert action items to pandas DataFrame for table display"""
        if not actions_data:
            return pd.DataFrame(columns=["Task", "Owner", "Deadline", "Dependencies"])
        
        formatted_actions = []
        for action in actions_data:
            formatted_actions.append({
                "Task": action.get("task", "N/A"),
                "Owner": action.get("owner", "Not specified"),
                "Deadline": action.get("deadline", "Not specified"),
                "Dependencies": ", ".join(action.get("dependencies", [])) if action.get("dependencies") else "None"
            })
        
        return pd.DataFrame(formatted_actions)
    
    @staticmethod
    def format_risks_for_display(risks_data: Dict[str, Any]) -> str:
        """Format risks data for Streamlit display"""
        output = []
        
        if "open_questions" in risks_data and risks_data["open_questions"]:
            output.append("### 🤔 Open Questions\n")
            for i, question in enumerate(risks_data["open_questions"], 1):
                output.append(f"{i}. {question}")
            output.append("\n")
        
        if "assumptions" in risks_data and risks_data["assumptions"]:
            output.append("\n### 📋 Assumptions\n")
            for i, assumption in enumerate(risks_data["assumptions"], 1):
                output.append(f"{i}. {assumption}")
            output.append("\n")
        
        if "risks" in risks_data and risks_data["risks"]:
            output.append("\n### ⚠️ Identified Risks\n")
            for risk in risks_data["risks"]:
                severity = risk.get("severity", "medium").upper()
                severity_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(severity, "🟡")
                output.append(f"\n**{severity_emoji} {risk.get('title', 'Untitled Risk')}** ({severity})")
                output.append(f"\n{risk.get('description', 'No description')}")
        
        return "\n".join(output)
    
    @staticmethod
    def aggregate_results(
        summary_data: Dict[str, Any],
        actions_data: List[Dict[str, Any]],
        risks_data: Dict[str, Any],
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Aggregate all agent results into a single structured output"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "summary": summary_data,
            "actions": actions_data,
            "risks": risks_data,
        }
        
        if metadata:
            result["metadata"] = metadata
        
        return result
    
    @staticmethod
    def export_to_json(data: Dict[str, Any], filepath: str = None) -> str:
        """Export results to JSON format"""
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_str)
        
        return json_str
    
    @staticmethod
    def export_actions_to_csv(actions_data: List[Dict[str, Any]], filepath: str = None) -> str:
        """Export action items to CSV format"""
        df = OutputFormatter.format_actions_as_dataframe(actions_data)
        
        if filepath:
            df.to_csv(filepath, index=False)
            return filepath
        else:
            return df.to_csv(index=False)
    
    @staticmethod
    def create_summary_stats(
        summary_data: Dict[str, Any],
        actions_data: List[Dict[str, Any]],
        risks_data: Dict[str, Any]
    ) -> Dict[str, int]:
        """Create summary statistics for display"""
        return {
            "total_actions": len(actions_data),
            "total_risks": len(risks_data.get("risks", [])),
            "total_open_questions": len(risks_data.get("open_questions", [])),
            "total_assumptions": len(risks_data.get("assumptions", [])),
            "key_decisions": len(summary_data.get("key_decisions", [])),
        }
