# schema.py
from pydantic import BaseModel
from typing import List, Optional

class Option(BaseModel):
    key: str  # e.g., "A", "B", "C", "D"
    text: str

class Question(BaseModel):
    question_number: Optional[str] = None
    question_text: str
    options: List[Option] = []
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None

class QuestionPaper(BaseModel):
    title: Optional[str] = "Question Paper"
    questions: List[Question]