import os
import random
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")


def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def create_tables(client: Client):
    print("Creating tables...")

    client.sql("""
    CREATE TABLE IF NOT EXISTS students (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        major TEXT,
        gpa NUMERIC(3,2)
    );
    """).execute()

    client.sql("""
    CREATE TABLE IF NOT EXISTS courses (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name TEXT NOT NULL,
        code TEXT UNIQUE NOT NULL,
        instructor TEXT,
        credits INTEGER,
        capacity INTEGER
    );
    """).execute()

    client.sql("""
    CREATE TABLE IF NOT EXISTS transactions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        student_id UUID NOT NULL REFERENCES students(id),
        course_id UUID NOT NULL REFERENCES courses(id),
        transaction_type TEXT,
        amount NUMERIC(10,2),
        status TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        description TEXT
    );
    """).execute()

    print("✓ Tables created")


def seed_students(client: Client, count: int = 100):
    print(f"Seeding {count} students...")

    majors = [
        "Computer Science",
        "Business",
        "Engineering",
        "Mathematics",
        "Physics",
        "Chemistry",
        "Biology",
        "Economics",
        "Psychology",
    ]

    first_names = [
        "Alice", "Bob", "Charlie", "Diana", "Emma", "Frank", "Grace", "Henry",
        "Isabella", "Jack", "Katherine", "Leo", "Maria", "Nathan", "Olivia",
        "Peter", "Quinn", "Rachel", "Samuel", "Tina",
    ]

    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
        "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    ]

    students = []
    for i in range(count):
        student_id = str(uuid.uuid4())
        first = random.choice(first_names)
        last = random.choice(last_names)
        name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}{i}@university.edu"
        major = random.choice(majors)
        gpa = round(random.uniform(2.0, 4.0), 2)
        enrollment_date = datetime.now() - timedelta(days=random.randint(30, 730))

        students.append({
            "id": student_id,
            "name": name,
            "email": email,
            "enrollment_date": enrollment_date.isoformat(),
            "major": major,
            "gpa": float(gpa),
        })

    client.table("students").insert(students).execute()
    print(f"✓ {count} students seeded")
    return students


def seed_courses(client: Client, count: int = 50):
    print(f"Seeding {count} courses...")

    course_names = [
        "Introduction to Python", "Data Structures", "Web Development",
        "Machine Learning", "Database Systems", "Operating Systems",
        "Algorithms", "Artificial Intelligence", "Cloud Computing",
        "Software Engineering", "Advanced Java", "Mobile Development",
        "Cybersecurity", "Calculus I", "Linear Algebra", "Physics I",
        "Chemistry I", "Biology I", "Business Management", "Economics",
        "Marketing", "Finance", "Accounting", "Statistics", "Discrete Math",
        "Computer Networks", "Compiler Design", "Graphics Programming",
        "Theory of Computation", "Parallel Computing",
    ]

    professors = [
        "Dr. Smith", "Prof. Johnson", "Dr. Williams", "Prof. Brown", "Dr. Jones",
        "Prof. Garcia", "Dr. Miller", "Prof. Davis", "Dr. Rodriguez", "Prof. Martinez",
    ]

    courses = []
    for i in range(count):
        course_id = str(uuid.uuid4())
        name = random.choice(course_names)
        code = f"CS{random.randint(100, 500)}"
        instructor = random.choice(professors)
        credits = random.choice([3, 4, 5])
        capacity = random.choice([20, 30, 40, 50])

        courses.append({
            "id": course_id,
            "name": name,
            "code": code,
            "instructor": instructor,
            "credits": credits,
            "capacity": capacity,
        })

    client.table("courses").insert(courses).execute()
    print(f"✓ {count} courses seeded")
    return courses


def seed_transactions(client: Client, students: list, courses: list, count: int = 850):
    print(f"Seeding {count} transactions...")

    transaction_types = ["enrollment", "payment", "grade_submission", "course_drop"]
    statuses = ["pending", "completed", "failed"]

    transactions = []
    for i in range(count):
        transaction_id = str(uuid.uuid4())
        student = random.choice(students)
        course = random.choice(courses)
        transaction_type = random.choice(transaction_types)
        status = random.choice(statuses)

        amount = None
        if transaction_type == "payment":
            amount = round(random.uniform(500, 5000), 2)

        timestamp = datetime.now() - timedelta(days=random.randint(0, 365))

        descriptions = {
            "enrollment": f"Enrolled in {course['code']}",
            "payment": f"Tuition payment for {course['code']}",
            "grade_submission": f"Grade submitted for {course['code']}",
            "course_drop": f"Dropped {course['code']}",
        }

        transactions.append({
            "id": transaction_id,
            "student_id": student["id"],
            "course_id": course["id"],
            "transaction_type": transaction_type,
            "amount": amount,
            "status": status,
            "timestamp": timestamp.isoformat(),
            "description": descriptions[transaction_type],
        })

    client.table("transactions").insert(transactions).execute()
    print(f"✓ {count} transactions seeded")


def main():
    print("Starting database seeding...\n")

    client = get_supabase_client()

    try:
        create_tables(client)
        students = seed_students(client, 100)
        courses = seed_courses(client, 50)
        seed_transactions(client, students, courses, 850)

        total_records = 100 + 50 + 850
        print(f"\n✓ Database seeding complete! Total records: {total_records}")

    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        raise


if __name__ == "__main__":
    main()
