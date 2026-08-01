# schema.py
from pydantic import BaseModel, Field
from typing import List, Optional

class Option(BaseModel):
    """Represents an individual option in a multiple-choice question."""
    label: str = Field(description="Option identifier, e.g., 'Option 1', 'a', 'A'")
    text: str = Field(description="The actual text content of the option")
    is_correct: bool = Field(description="True if this option is marked as correct, False otherwise")

class QuestionItem(BaseModel):
    """Represents a single extracted question with its choices and metadata."""
    question_number: int = Field(description="Sequential question number")
    question_text: str = Field(description="The cleaned text of the question, removing duplicates or pipe artifacts")
    question_type: str = Field(default="multiple_Choice", description="Type of question, e.g., multiple_Choice")
    options: List[Option] = Field(description="List of all options for this question")
    solution: Optional[str] = Field(default=None, description="Detailed solution or explanation if available")
    marks: Optional[float] = Field(default=1.0, description="Marks awarded for correct answer")
    negative_marks: Optional[float] = Field(default=0.33, description="Negative marks for incorrect answer")

class QuestionPaper(BaseModel):
    """The master container holding all extracted questions from the PDF."""
    title: Optional[str] = Field(default="Question Bank", description="Extracted or generated title for the document")
    questions: List[QuestionItem] = Field(description="List of all processed questions")