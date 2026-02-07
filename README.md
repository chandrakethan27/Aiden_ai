# Multi-Agent Document Intelligence System

An advanced AI-powered system that processes long, unstructured documents using specialized autonomous agents to extract structured insights.

## 🎯 Overview

This system uses **three specialized AI agents** coordinated through a central orchestration layer to analyze documents and produce:
- **Context-aware summaries** with key decisions and constraints
- **Actionable tasks** with owners, deadlines, and dependencies
- **Risk analysis** including open questions and assumptions

Built with [AutoGen](https://github.com/microsoft/autogen) for multi-agent coordination and [Streamlit](https://streamlit.io/) for the user interface.

## ✨ Features

### 🔍 Summary Agent
- Generates concise summaries while preserving document intent
- Extracts key decisions and critical constraints
- Handles long documents via intelligent chunking
- Maintains context across document sections

### ✅ Action Agent
- Identifies explicit and implicit action items
- Extracts task metadata (owners, deadlines, dependencies)
- Structures tasks in machine-readable format
- Deduplicates similar actions

### ⚠️ Risk Agent
- Identifies potential risks and challenges
- Flags unresolved questions and missing data
- Detects assumptions (explicit and implicit)
- Categorizes risks by severity and type

### 🎨 Modern UI
- Clean, intuitive Streamlit interface
- Real-time processing status updates
- Tabbed results display
- Export to JSON and CSV

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (or compatible LLM provider)

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd SecondTry
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   MODEL_NAME=gpt-4-turbo-preview
   ```

### Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📖 Usage

1. **Input Document**
   - Paste text directly into the text area, OR
   - Upload a TXT or MD file

2. **Process**
   - Click "🚀 Process Document"
   - Watch real-time status updates for each agent

3. **Review Results**
   - **Summary Tab**: View document summary with key decisions
   - **Actions Tab**: See structured action items in table format
   - **Risks Tab**: Review identified risks and open questions
   - **Raw JSON Tab**: Access complete structured output

4. **Export**
   - Download complete results as JSON
   - Export action items as CSV

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Streamlit UI (app.py)           │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│    Document Orchestrator                │
│    - Coordinates agent workflow         │
│    - Manages context sharing            │
│    - Handles document chunking          │
└────────┬────────────────────────────────┘
         │
         ├──────────┬──────────┬──────────┐
         ▼          ▼          ▼          ▼
    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
    │Summary │ │Action  │ │ Risk   │ │Document│
    │ Agent  │ │ Agent  │ │ Agent  │ │Processor│
    └────────┘ └────────┘ └────────┘ └────────┘
```

### Agent Coordination Flow

1. **Document Processing**: Text is cleaned and chunked if needed
2. **Summary Agent**: Analyzes document first to provide context
3. **Action Agent**: Uses summary context to identify tasks
4. **Risk Agent**: Uses summary + actions to identify risks
5. **Results Aggregation**: All outputs combined into structured format

## 📁 Project Structure

```
SecondTry/
├── agents/
│   ├── summary_agent.py      # Context-aware summary generation
│   ├── action_agent.py        # Action item extraction
│   ├── risk_agent.py          # Risk and issue identification
│   └── orchestrator.py        # Central coordination
├── utils/
│   ├── config.py              # Configuration management
│   ├── document_processor.py  # Document chunking
│   └── output_formatter.py    # Result formatting
├── examples/
│   └── sample_document.txt    # Sample meeting transcript
├── app.py                     # Streamlit application
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
└── README.md                  # This file
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `MODEL_NAME` | LLM model to use | `gpt-4-turbo-preview` |
| `MAX_TOKENS` | Maximum tokens per request | `4096` |
| `TEMPERATURE` | Model temperature | `0.7` |

### Agent-Specific Settings

The system automatically adjusts temperature for each agent:
- **Summary Agent**: 0.5 (more focused)
- **Action Agent**: 0.3 (very precise)
- **Risk Agent**: 0.7 (more creative)

### Document Processing

- **Chunk Size**: 3000 tokens
- **Chunk Overlap**: 200 tokens
- **Encoding**: cl100k_base (GPT-4)

## 🧪 Testing

Try the system with the included sample document:

```bash
# The sample document is in examples/sample_document.txt
# It's a realistic meeting transcript with ~600 words
```

Expected outputs:
- **Summary**: Concise overview of the product launch meeting
- **Actions**: 6+ action items with owners and deadlines
- **Risks**: Multiple identified risks including timeline, budget, and technical concerns

## 🔧 Troubleshooting

### "Missing API configuration" error
- Ensure `.env` file exists and contains `OPENAI_API_KEY`
- Verify the API key is valid

### Agents returning empty results
- Check that the document is at least 100 characters
- Verify API key has sufficient credits
- Check console for detailed error messages

### Chunking issues with long documents
- Adjust `chunk_size` in `utils/config.py`
- Increase `chunk_overlap` for better context preservation

## 🛠️ Advanced Usage

### Using Azure OpenAI

Add to `.env`:
```
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_DEPLOYMENT=your_deployment
```

### Using Local Models (Ollama)

Add to `.env`:
```
USE_LOCAL_MODEL=true
LOCAL_MODEL_BASE_URL=http://localhost:11434
LOCAL_MODEL_NAME=llama2
```

## 📊 Output Format

### Summary
```json
{
  "summary": "Concise summary text",
  "key_decisions": ["Decision 1", "Decision 2"],
  "constraints": ["Constraint 1", "Constraint 2"],
  "intent": "Primary purpose"
}
```

### Actions
```json
[
  {
    "task": "Task description",
    "owner": "Person/role",
    "deadline": "Date or timeframe",
    "dependencies": ["Prerequisite tasks"],
    "priority": "high|medium|low",
    "status": "pending|in-progress|blocked"
  }
]
```

### Risks
```json
{
  "open_questions": ["Question 1", "Question 2"],
  "assumptions": ["Assumption 1", "Assumption 2"],
  "missing_data": ["Missing info 1", "Missing info 2"],
  "risks": [
    {
      "title": "Risk title",
      "description": "Detailed description",
      "severity": "high|medium|low",
      "type": "technical|resource|timeline|scope|dependency|other",
      "mitigation": "Suggested mitigation"
    }
  ]
}
```

## 🤝 Contributing

This project was built for the AidenAI Hackathon 2026. Feel free to extend it with:
- Additional agent types
- Support for more document formats (PDF, DOCX)
- Enhanced visualization of dependencies
- Integration with project management tools

## 📝 License

MIT License - feel free to use and modify as needed.

## 🙏 Acknowledgments

- Built with [AutoGen](https://github.com/microsoft/autogen) by Microsoft
- UI powered by [Streamlit](https://streamlit.io/)
- Developed for AidenAI Hackathon 2026
