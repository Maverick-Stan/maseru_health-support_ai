# Maseru Health Support AI

## Data Science + Multi-Agent Mental Health Support System

Maseru Health Support AI is a Streamlit and Google ADK application that combines a multi-agent conversational assistant with a production-style risk detection engine. The system evaluates user messages with both machine learning and rule-based safety logic, then exposes explainable risk metadata through a minimal admin dashboard.

The project demonstrates how a prompt-based chatbot can be upgraded into a structured data science system with classification, feature engineering, model artifacts, decision thresholds, false-negative awareness, and escalation workflows.

> Important: This project is an educational prototype. It is not a medical device and does not provide diagnosis, treatment, or emergency services.

![User App Screenshot](Assets/app.jpg)

## What This Project Demonstrates

- Text classification for mental health risk detection
- TF-IDF feature engineering
- Logistic Regression probability scoring
- Rule-based critical keyword detection
- Hybrid decision logic combining ML + rules
- Recall-focused risk classification to reduce false negatives
- Explainable outputs for admin review
- Multi-agent orchestration with Google ADK
- Streamlit user and admin interfaces
- Modular, interview-friendly project structure

## Core Enhancement

The original system was a prompt-based mental health support chatbot. This upgraded version adds a data science layer that evaluates each user message before the conversational agent responds.

The risk engine returns:

- `risk_level`: LOW, MEDIUM, or HIGH
- `probability`: model confidence that the message is `at_risk`
- `reason`: why the decision was made
- `matched_keywords`: critical phrases detected by rules

If a message is HIGH risk, the system displays an escalation banner:

```text
You are not alone. Please consider visiting a nearby clinic or speaking to a professional.
```

## System Architecture

```text
User Message
    |
    v
Preprocessing
    |
    v
TF-IDF Vectorizer + Logistic Regression Model
    |
    v
Rule-Based Critical Keyword Check
    |
    v
Decision Engine
    |
    +--> LOW    -> Normal agent flow
    +--> MEDIUM -> Supportive tone adjustment
    +--> HIGH   -> Escalation agent + safety banner
```

## Multi-Agent Design

The system keeps the existing Google ADK agents and adds risk-aware routing around them.

| Agent | Role |
| --- | --- |
| `GreetingAgent` | Welcomes the user and sets expectations |
| `ConversationAgent` | Gently explores emotional and physical wellbeing |
| `SuggestionAgent` | Provides safe, non-clinical wellbeing suggestions |
| `HealthSupportCoordinator` | Coordinates the conversation flow |
| `EscalationAgent` | Responds calmly when HIGH risk is detected |

No existing agents were removed. The risk engine is integrated into the current flow instead of replacing it.

## Risk Detection Engine

The project uses a hybrid safety approach:

### 1. Machine Learning Classifier

- Dataset labels: `safe`, `at_risk`
- Features: TF-IDF unigrams and bigrams
- Model: Logistic Regression
- Output: probability of the `at_risk` class
- Saved artifacts:
  - `models/model.pkl`
  - `models/vectorizer.pkl`

### 2. Rule-Based Escalation

Some phrases should not rely only on model probability. The rules module checks for critical language such as:

- `kill myself`
- `can't go on`
- `end it all`
- `want to die`

If a critical keyword is found, the system immediately assigns HIGH risk with the reason `keyword_trigger`.

### 3. Decision Logic

The decision engine applies explainable thresholds:

| Condition | Risk Level | Reason |
| --- | --- | --- |
| Critical keyword detected | HIGH | `keyword_trigger` |
| Model probability > 0.70 | HIGH | `model_high_confidence` |
| Model probability between 0.40 and 0.70 | MEDIUM | `model_moderate` |
| Model probability < 0.40 | LOW | `model_low_confidence` |

This design prioritizes recall because false negatives are the highest-risk failure mode in this domain.

## Admin Dashboard

The admin page gives a clean, minimal view of the risk engine output.

It displays:

- Risk Level
- Confidence Score
- Reason
- Matched Keywords
- Escalation banner only for HIGH risk

Run it with:

```powershell
streamlit run app/streamlit_admin_app.py --server.port 8502
```

## User App

The user-facing chat app remains simple and supportive. The risk engine runs in the background, while the visible experience stays focused on conversation.

Run it with:

```powershell
streamlit run application.py --server.port 8501
```

Alternative structured entry point:

```powershell
streamlit run app/streamlit_user_app.py --server.port 8501
```

## Project Structure

```text
.
+-- app/
|   +-- streamlit_admin_app.py
|   +-- streamlit_user_app.py
+-- data/
|   +-- generate_dataset.py
|   +-- mental_health_dataset.csv
+-- models/
|   +-- model.pkl
|   +-- vectorizer.pkl
+-- src/
|   +-- preprocessing.py
|   +-- feature_engineering.py
|   +-- classifier.py
|   +-- rules.py
|   +-- decision_engine.py
|   +-- response_generator.py
+-- application.py
+-- maseru_health_agent.py
+-- requirements.txt
+-- README.md
```

## Data Science Pipeline

### Dataset

The dataset is generated by `data/generate_dataset.py` and saved to:

```text
data/mental_health_dataset.csv
```

Example samples:

| Text | Label |
| --- | --- |
| `I feel hopeless` | `at_risk` |
| `I can't go on` | `at_risk` |
| `I want to end it` | `at_risk` |
| `I am tired of everything` | `at_risk` |
| `I feel okay today` | `safe` |

### Preprocessing

Implemented in `src/preprocessing.py`:

- Lowercasing
- Punctuation removal
- URL/email/noise removal
- Whitespace normalization
- Tokenization

### Feature Engineering

Implemented in `src/feature_engineering.py`:

- TF-IDF vectorization
- Unigrams and bigrams
- Pickle-based vectorizer persistence

### Model Training

Implemented in `src/classifier.py`:

- Logistic Regression
- Balanced class weights
- Recall-oriented evaluation threshold
- Prints precision, recall, and F1 score
- Saves model and vectorizer artifacts

Train the model:

```powershell
python -m src.classifier
```

Generate the dataset:

```powershell
python data/generate_dataset.py
```

## Example Risk Outputs

```python
evaluate_risk("I want to die")
```

```python
{
    "risk_level": "HIGH",
    "probability": 0.66,
    "reason": "keyword_trigger",
    "matched_keywords": ["want to die"]
}
```

```python
evaluate_risk("I want to end it")
```

```python
{
    "risk_level": "HIGH",
    "probability": 0.81,
    "reason": "model_high_confidence",
    "matched_keywords": []
}
```

```python
evaluate_risk("I feel okay today")
```

```python
{
    "risk_level": "LOW",
    "probability": 0.24,
    "reason": "model_low_confidence",
    "matched_keywords": []
}
```

## Tech Stack

- Python
- Streamlit
- Google ADK
- LiteLLM
- scikit-learn
- pandas
- TF-IDF
- Logistic Regression
- Pickle model persistence

## Installation

```powershell
pip install -r requirements.txt
```

If using OpenAI through LiteLLM:

```powershell
setx OPENAI_API_KEY "YOUR_OPENAI_KEY"
```

Then restart your terminal before running the app.

## Running the Full Project

1. Install dependencies:

```powershell
pip install -r requirements.txt
```

2. Generate the dataset:

```powershell
python data/generate_dataset.py
```

3. Train the model:

```powershell
python -m src.classifier
```

4. Start the user app:

```powershell
streamlit run application.py --server.port 8501
```

5. Start the admin app:

```powershell
streamlit run app/streamlit_admin_app.py --server.port 8502
```

## Why This Is Recruiter-Relevant

This project shows more than chatbot prompting. It demonstrates the ability to design an end-to-end applied ML system:

- Build and persist a labeled dataset
- Preprocess unstructured text
- Engineer TF-IDF features
- Train and evaluate a classifier
- Tune decision thresholds around real-world risk
- Combine ML with deterministic business rules
- Explain model decisions to non-technical users
- Integrate ML into an agent-based application
- Build separate user and admin interfaces
- Keep the implementation modular and maintainable

## Future Improvements

- Expand the dataset with expert-reviewed examples
- Add model calibration and threshold validation
- Track longitudinal risk trends by session
- Add role-based admin authentication
- Store assessments in a database
- Add evaluation tests for false negatives
- Replace the demo classifier with a validated clinical safety model

## Disclaimer

This application is for educational and portfolio purposes only. It should not be used as a replacement for professional mental health support, emergency care, or clinical judgment.
