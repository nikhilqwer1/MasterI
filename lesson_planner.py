import os
from typing import List, Literal
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv(override=True)

class Scene(BaseModel):
    scene_id: int
    title: str = Field(description="Scene heading")
    avatar_speech: str = Field(description="Teacher dialogue in requested language")
    visual_type: Literal["bullet_points", "code", "formula", "diagram_description"]
    visual_content: str = Field(description="Visual content for chalkboard")

class Checkpoint(BaseModel):
    checkpoint_id: int
    trigger_after_scene_id: int
    question: str
    options: List[str]
    correct_answer: str
    explanation_on_fail: str

class LessonPlan(BaseModel):
    lesson_title: str
    target_level: str
    language: str
    scenes: List[Scene]
    checkpoints: List[Checkpoint]

def generate_structured_lesson(topic: str, context: str, level: str, time_mins: int, language: str) -> LessonPlan:
    api_key = os.getenv("GROQ_API_KEY")
    
    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        temperature=0.2,
        groq_api_key=api_key
    )
    structured_llm = llm.with_structured_output(LessonPlan)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a human-like interactive AI Teacher.
Design a structured teaching session. Break the topic into 3-4 scenes.
Add checkpoint questions to check student understanding.
Strictly adhere to the requested language (English, Hindi, or Hinglish)."""),
        ("human", """Topic: {topic}
Learner Level: {level}
Available Time: {time_mins} mins
Language: {language}

Reference Material:
{context}""")
    ])

    chain = prompt | structured_llm
    return chain.invoke({
        "topic": topic,
        "level": level,
        "time_mins": time_mins,
        "language": language,
        "context": context if context else "Use accurate domain fundamentals."
    })