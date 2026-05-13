import json
from typing import Any, Dict, List
from langchain.agents import Tool, initialize_agent, AgentType
from langchain_groq import ChatGroq
from config import get_settings
from agent.tools import DatabaseTools


class DatabaseAgent:
    def __init__(self):
        self.settings = get_settings()
        self.llm = ChatGroq(
            model_name="llama-3.3-70b-versatile",
            temperature=0,
            api_key=self.settings.groq_api_key,
        )
        self.tools = self._create_tools()
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False,
        )

    def _create_tools(self) -> List[Tool]:
        return [
            Tool(
                name="query_students",
                func=lambda **kwargs: json.dumps(DatabaseTools.query_students(**kwargs)),
                description="Query students by name, major, or GPA range. "
                "Use this when user asks about students.",
            ),
            Tool(
                name="query_courses",
                func=lambda **kwargs: json.dumps(DatabaseTools.query_courses(**kwargs)),
                description="Query courses by name, instructor, or credits range. "
                "Use this when user asks about courses.",
            ),
            Tool(
                name="query_transactions",
                func=lambda **kwargs: json.dumps(DatabaseTools.query_transactions(**kwargs)),
                description="Query transactions by student, course, type, or status. "
                "Use this when user asks about transactions or enrollments.",
            ),
            Tool(
                name="get_student_courses",
                func=lambda student_id: json.dumps(DatabaseTools.get_student_courses(student_id)),
                description="Get all courses for a specific student.",
            ),
            Tool(
                name="get_course_students",
                func=lambda course_id: json.dumps(DatabaseTools.get_course_students(course_id)),
                description="Get all students enrolled in a specific course.",
            ),
            Tool(
                name="get_student_transaction_summary",
                func=lambda student_id: json.dumps(DatabaseTools.get_student_transaction_summary(student_id)),
                description="Get transaction summary and statistics for a student.",
            ),
            Tool(
                name="get_course_statistics",
                func=lambda course_id: json.dumps(DatabaseTools.get_course_statistics(course_id)),
                description="Get enrollment statistics and details for a course.",
            ),
        ]

    def run(self, query: str) -> str:
        try:
            result = self.agent.run(query)
            return result
        except Exception as e:
            return f"Error processing query: {str(e)}"
