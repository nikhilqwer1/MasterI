import os
from typing import List
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv(override=True)

class DiagnosticReport(BaseModel):
    score_percentage: float
    mastered_concepts: List[str]
    weak_concepts: List[str]
    recommended_revision_plan: str
    suggested_next_topic: str

def generate_diagnostic_report(topic: str, answers_summary: str) -> DiagnosticReport:
    api_key = os.getenv("GROQ_API_KEY")
    
    llm = ChatGroq(
        model_name="llama-3.1-8b-instant",
        temperature=0.1,
        groq_api_key=api_key
    )
    structured_llm = llm.with_structured_output(DiagnosticReport)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Analyze student assessment performance and produce a diagnostic feedback report with identified weak areas and revision next-steps."),
        ("human", "Topic: {topic}\nStudent Answers & Results:\n{summary}")
    ])
    chain = prompt | structured_llm
    return chain.invoke({"topic": topic, "summary": answers_summary})