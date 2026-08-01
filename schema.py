# schema.py
from pydantic import BaseModel, Field
from typing import List, Optional

class Option(BaseModel):
    label: Optional[str] = Field(default="A", description="Option label, e.g., A, B, C, D")
    text: Optional[str] = Field(default="", description="The text content of the option")
    is_correct: Optional[bool] = False

    # Fallbacks so legacy code referencing 'key' or 'option_text' won't crash
    @property
    def key(self) -> str:
        return self.label or "A"

    @property
    def option_text(self) -> str:
        return self.text or ""


class Question(BaseModel):
    question_number: Optional[str] = None
    question_type: Optional[str] = "MCQ"
    question_text: str
    options: List[Option] = []
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    marks: Optional[str] = None

    # Fallbacks for question naming variations
    @property
    def number(self) -> Optional[str]:
        return self.question_number

    @property
    def text(self) -> str:
        return self.question_text


class QuestionPaper(BaseModel):
    title: Optional[str] = "Question Paper"
    instructions: Optional[List[str]] = []
    questions: List[Question]