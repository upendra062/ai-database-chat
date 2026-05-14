import re
import json
from typing import List
from langchain.agents import Tool, initialize_agent, AgentType
from langchain_groq import ChatGroq
from config import get_settings
from agent.tools import DatabaseTools
from memory import MemoryStore


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
                    "You are Rocky AI, a helpful assistant for a university database system. "
                    "You can query students, courses, and transactions. "
                    "For greetings or general questions NOT about the database, respond naturally WITHOUT using any tools. "
                    "Only use tools when the user explicitly asks about students, courses, transactions, or enrollment data. "
                    "Always give a clean, concise, friendly final answer."
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
                description="Query transactions/enrollments. Use when user asks about transactions.",
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
                func=lambda student_id: json.dumps(
                    DatabaseTools.get_student_transaction_summary(student_id)
                ),
                description="Get transaction summary for a student. Input: student_id.",
            ),
            Tool(
                name="get_course_statistics",
                func=lambda course_id: json.dumps(
                    DatabaseTools.get_course_statistics(course_id)
                ),
                description="Get enrollment statistics for a course. Input: course_id.",
            ),
        ]

    def _clean_response(self, response: str) -> str:
        patterns = [
            r'Question:.*?(?=\nFinal Answer:|\Z)',
            r'Thought:.*?(?=\nAction:|\nFinal Answer:|\Z)',
            r'Action:\s*None\s*',
            r'Action Input:\s*None\s*',
            r'Observation:.*?(?=\nThought:|\nFinal Answer:|\Z)',
            r'> Finished chain\.',
        ]
        cleaned = response
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL | re.IGNORECASE)

        final_match = re.search(r'Final Answer:\s*(.*)', cleaned, re.DOTALL | re.IGNORECASE)
        if final_match:
            cleaned = final_match.group(1).strip()

        cleaned = cleaned.strip()
        return cleaned if cleaned else response.strip()

    def run(self, query: str, session_id: str = "default") -> str:
        try:
            # Load conversation history from Supabase
            history = MemoryStore.load(session_id)
            history_text = MemoryStore.format_for_prompt(history)

            # Prepend history context to the query
            if history_text:
                full_query = f"{history_text}\n\nCurrent question: {query}"
            else:
                full_query = query

            result = self.agent.run(full_query)
            cleaned = self._clean_response(result)

            # Persist this turn to Supabase
            MemoryStore.save(session_id, "user", query)
            MemoryStore.save(session_id, "assistant", cleaned)

            return cleaned
        except Exception as e:
            return f"I encountered an error: {str(e)}"
