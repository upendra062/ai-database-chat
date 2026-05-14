import json
from typing import List
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
            max_iterations=5,
            max_execution_time=25,
            early_stopping_method="generate",
            handle_parsing_errors=True,
            agent_kwargs={
                "prefix": (
                    "You are a helpful database assistant. You can query students, courses, "
                    "and transactions. For greetings or general questions, respond naturally "
                    "without using any tools. Only use tools when the user asks about "
                    "database data."
                )
            },
        )

    def _create_tools(self) -> List[Tool]:
        return [
            Tool(
                name="query_students",
                func=lambda x: json.dumps(DatabaseTools.query_students()),
                description="Query all students from the database. Use when user asks about students.",
            ),
            Tool(
                name="query_courses",
                func=lambda x: json.dumps(DatabaseTools.query_courses()),
                description="Query all courses from the database. Use when user asks about courses.",
            ),
            Tool(
                name="query_transactions",
                func=lambda x: json.dumps(DatabaseTools.query_transactions()),
                description="Query transactions/enrollments. Use when user asks about transactions or enrollments.",
            ),
            Tool(
                name="get_student_courses",
                func=lambda student_id: json.dumps(DatabaseTools.get_student_courses(student_id)),
                description="Get all courses for a specific student. Input: student_id.",
            ),
            Tool(
                name="get_course_students",
                func=lambda course_id: json.dumps(DatabaseTools.get_course_students(course_id)),
                description="Get all students enrolled in a specific course. Input: course_id.",
            ),
            Tool(
                name="get_student_transaction_summary",
                func=lambda student_id: json.dumps(DatabaseTools.get_student_transaction_summary(student_id)),
                description="Get transaction summary for a student. Input: student_id.",
            ),
            Tool(
                name="get_course_statistics",
                func=lambda course_id: json.dumps(DatabaseTools.get_course_statistics(course_id)),
                description="Get enrollment statistics for a course. Input: course_id.",
            ),
        ]

    def run(self, query: str) -> str:
        try:
            result = self.agent.run(query)
            return result
        except Exception as e:
            return f"Error processing query: {str(e)}"
