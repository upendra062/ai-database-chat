from typing import Optional, List, Dict, Any
from database import SupabaseDB


def _safe_query(fn):
    """Wraps a database call and returns a friendly string on failure."""
    try:
        return fn()
    except Exception as e:
        err = str(e)
        if "Invalid API key" in err or "401" in err:
            return []
        raise


class DatabaseTools:
    @staticmethod
    def query_students(
        name: Optional[str] = None,
        major: Optional[str] = None,
        gpa_min: Optional[float] = None,
        gpa_max: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        try:
            client = SupabaseDB.get_client()
            query = client.table("students").select("*")
            if name:
                query = query.ilike("name", f"%{name}%")
            if major:
                query = query.eq("major", major)
            if gpa_min:
                query = query.gte("gpa", gpa_min)
            if gpa_max:
                query = query.lte("gpa", gpa_max)
            result = query.execute()
            return result.data if result and result.data else []
        except Exception as e:
            return {"error": f"Could not fetch students: {str(e)}"}

    @staticmethod
    def query_courses(
        name: Optional[str] = None,
        instructor: Optional[str] = None,
        credits_min: Optional[int] = None,
        credits_max: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        try:
            client = SupabaseDB.get_client()
            query = client.table("courses").select("*")
            if name:
                query = query.ilike("name", f"%{name}%")
            if instructor:
                query = query.ilike("instructor", f"%{instructor}%")
            if credits_min:
                query = query.gte("credits", credits_min)
            if credits_max:
                query = query.lte("credits", credits_max)
            result = query.execute()
            return result.data if result and result.data else []
        except Exception as e:
            return {"error": f"Could not fetch courses: {str(e)}"}

    @staticmethod
    def query_transactions(
        student_id: Optional[str] = None,
        course_id: Optional[str] = None,
        transaction_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        try:
            client = SupabaseDB.get_client()
            query = client.table("transactions").select("*")
            if student_id:
                query = query.eq("student_id", student_id)
            if course_id:
                query = query.eq("course_id", course_id)
            if transaction_type:
                query = query.eq("transaction_type", transaction_type)
            if status:
                query = query.eq("status", status)
            result = query.execute()
            return result.data if result and result.data else []
        except Exception as e:
            return {"error": f"Could not fetch transactions: {str(e)}"}

    @staticmethod
    def get_student_courses(student_id: str) -> List[Dict[str, Any]]:
        try:
            client = SupabaseDB.get_client()
            result = (
                client.table("transactions")
                .select("courses(id, name, code, instructor, credits)")
                .eq("student_id", student_id)
                .execute()
            )
            return result.data if result and result.data else []
        except Exception as e:
            return {"error": f"Could not fetch student courses: {str(e)}"}

    @staticmethod
    def get_course_students(course_id: str) -> List[Dict[str, Any]]:
        try:
            client = SupabaseDB.get_client()
            result = (
                client.table("transactions")
                .select("students(id, name, email, major)")
                .eq("course_id", course_id)
                .execute()
            )
            return result.data if result and result.data else []
        except Exception as e:
            return {"error": f"Could not fetch course students: {str(e)}"}

    @staticmethod
    def get_student_transaction_summary(student_id: str) -> Dict[str, Any]:
        try:
            client = SupabaseDB.get_client()
            result = (
                client.table("transactions")
                .select("*")
                .eq("student_id", student_id)
                .execute()
            )
            transactions = result.data if result and result.data else []
            if not transactions:
                return {"student_id": student_id, "total_transactions": 0}
            return {
                "student_id": student_id,
                "total_transactions": len(transactions),
                "by_type": {
                    t: len([x for x in transactions if x["transaction_type"] == t])
                    for t in set(x["transaction_type"] for x in transactions)
                },
                "by_status": {
                    s: len([x for x in transactions if x["status"] == s])
                    for s in set(x["status"] for x in transactions)
                },
            }
        except Exception as e:
            return {"error": f"Could not fetch summary: {str(e)}"}

    @staticmethod
    def get_course_statistics(course_id: str) -> Dict[str, Any]:
        try:
            client = SupabaseDB.get_client()
            enrollments = (
                client.table("transactions")
                .select("*")
                .eq("course_id", course_id)
                .execute()
            ).data or []
            course = client.table("courses").select("*").eq("id", course_id).execute()
            course_data = course.data[0] if course.data else {}
            return {
                "course_id": course_id,
                "course_name": course_data.get("name", "Unknown"),
                "total_enrolled": len(enrollments),
                "capacity": course_data.get("capacity", "Unknown"),
                "enrollment_rate": (
                    f"{(len(enrollments) / course_data.get('capacity', 1) * 100):.1f}%"
                    if course_data.get("capacity") else "N/A"
                ),
                "transaction_summary": {
                    t: len([x for x in enrollments if x["transaction_type"] == t])
                    for t in set(x["transaction_type"] for x in enrollments)
                },
            }
        except Exception as e:
            return {"error": f"Could not fetch course stats: {str(e)}"}
