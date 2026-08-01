# schema.py
from pydantic import BaseModel, Field
from typing import List, Optional, Any

class Option(BaseModel):
    label: Optional[str] = Field(default="A", description="Option label, e.g., A, B, C, D")
    text: Optional[str] = Field(default="", description="The text content of the option")
    is_correct: Optional[bool] = False

    def __getattr__(self, name: str) -> Any:
        if name == "key":
            return self.label or "A"
        if name in ("option_text", "value"):
            return self.text or ""
        return None


class Question(BaseModel):
    question_number: Optional[str] = None
    question_type: Optional[str] = "MCQ"
    question_text: str = ""
    options: List[Option] = []
    correct_answer: Optional[str] = None
    solution: Optional[str] = None
    explanation: Optional[str] = None
    marks: Optional[str] = None
    positive_marks: Optional[str] = None
    negative_marks: Optional[str] = None
    difficulty: Optional[str] = None
    topic: Optional[str] = None

    def __getattr__(self, name: str) -> Any:
        if name == "number":
            return self.question_number or ""
        if name == "text":
            return self.question_text or ""
        if name == "answer":
            return self.correct_answer or ""
        # Catch any other attribute requested by pdf_generator.py safely
        return None


class QuestionPaper(BaseModel):
    title: Optional[str] = "Question Paper"
    instructions: Optional[List[str]] = []
    questions: List[Question] = []

    def __getattr__(self, name: str) -> Any:
        return None