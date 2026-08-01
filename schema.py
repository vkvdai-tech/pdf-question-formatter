# schema.py
from pydantic import BaseModel, Field
from typing import List, Optional, Any

class BaseCatchAllModel(BaseModel):
    """
    Base model that prevents AttributeError by returning None 
    for any property accessed by pdf_generator.py that isn't defined.
    """
    def __getattr__(self, item: str) -> Any:
        return None


class Option(BaseCatchAllModel):
    label: Optional[str] = Field(default="A", description="Option label, e.g., A, B, C, D")
    text: Optional[str] = Field(default="", description="The text content of the option")
    is_correct: Optional[bool] = False

    # Property fallbacks
    @property
    def key(self) -> str:
        return self.label or "A"

    @property
    def option_text(self) -> str:
        return self.text or ""


class Question(BaseCatchAllModel):
    question_number: Optional[str] = None
    question_type: Optional[str] = "MCQ"
    question_text: str
    options: List[Option] = []
    correct_answer: Optional[str] = None
    solution: Optional[str] = None
    explanation: Optional[str] = None
    marks: Optional[str] = None
    negative_marks: Optional[str] = None  # <-- Explicitly added
    positive_marks: Optional[str] = None
    difficulty: Optional[str] = None
    topic: Optional[str] = None

    # Property fallbacks
    @property
    def number(self) -> Optional[str]:
        return self.question_number or ""

    @property
    def text(self) -> str:
        return self.question_text or ""

    @property
    def answer(self) -> Optional[str]:
        return self.correct_answer or ""


class QuestionPaper(BaseCatchAllModel):
    title: Optional[str] = "Question Paper"
    instructions: Optional[List[str]] = []
    questions: List[Question] = []