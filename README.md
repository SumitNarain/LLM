# 🩺 Conversational Medical Assistant Agent

This project implements a structured, conversational AI agent designed to perform comprehensive patient history-taking. The agent guides the user through a sequential interview process (PC, HPI, PMH, etc.), synthesizes the information in real-time, and concludes by generating a final, structured JSON management plan, including the differential diagnosis and initial therapeutic recommendations.

The agent leverages the capabilities of modern LLMs (specifically `gpt-4o-mini`) combined with Pydantic schemas for reliable, structured output at every step.

## ✨ Features

* **Structured Interview Flow:** Follows a fixed, clinical sequence: Presenting Complaint (PC) → History of Presenting Complaint (HPI) → Past Medical History (PMH) → Medications (MEDS) → Social History (SH) → Family History (FH) → DONE.
* **Real-time History Synthesis:** Maintains a running, synthesized patient narrative in the `physician_note` field.
* **Clean Conversation:** Separates the running history from the next question, providing a clear, single question to the user at each turn.
* **Structured Final Output:** Upon completion of the history, the agent generates a comprehensive `ManagementPlanOutput` JSON object, including a primary working diagnosis, diagnostic plan, and therapeutic plan.
* **Modular Design:** Code is structured across multiple files (`main.py`, `medical_agent.py`, `models/`) for improved maintainability.

## 🚀 Getting Started

### Prerequisites

1.  **Python 3.9+**
2.  **OpenAI API Key:** Required for model access.
3.  **Required Libraries:** (Install from `requirements.txt`)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/SumitNarain/LLM.git
    cd LLM/OpenAICall
    ```

2.  **Set up the Virtual Environment (Recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Take .env.template file and convert to .env and population env variables there
    ```ini
    # .env
    OPENAI_API_KEY="sk-..." 
    ```

### How to Run

Execute the main script from your terminal:

```bash
python main.py