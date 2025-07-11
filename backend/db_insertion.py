import random
from datetime import datetime, timedelta
from faker import Faker

from db import SessionLocal, engine
from models import Base, Admin, Student, Quiz, Submission, QuizScore
from datetime import datetime, timedelta
from random import choice, randint, uniform




Base.metadata.create_all(bind=engine)
session = SessionLocal()
fake = Faker()

# -------------------- Admins --------------------
admins = [
    Admin(name="Alice", email="alice@dumroo.ai", grade_scope="6,7,8", class_scope="A", region_scope="North"),
    Admin(name="Bob", email="bob@dumroo.ai", grade_scope="9,10", class_scope="A", region_scope="South"),
    Admin(name="Charlie", email="charlie@dumroo.ai", grade_scope="6,7,8", class_scope="B", region_scope="South")
]
session.add_all(admins)
session.commit()

# -------------------- Students --------------------
students = []
grades_all = ["6", "7", "8", "9", "10"]
class_region_pairs = [("A", "North"), ("A", "South"), ("B", "South")]

for grade in grades_all:
    for class_name, region in class_region_pairs:
        for _ in range(randint(25, 30)):
            student = Student(
                name=fake.name(),
                grade=grade,
                class_name=class_name,
                region=region
            )
            students.append(student)

session.add_all(students)
session.commit()

# -------------------- Quizzes --------------------
subjects = ["Math", "Science", "English"]
quizzes = []

for grade in grades_all:
    for class_name, region in class_region_pairs:
        for _ in range(3):  # Past quizzes
            quizzes.append(
                Quiz(
                    subject=choice(subjects),
                    grade=grade,
                    class_name=class_name,
                    region=region,
                    scheduled_date=datetime.now().date() - timedelta(days=randint(5, 20))
                )
            )
        for _ in range(2):  # Future quizzes
            quizzes.append(
                Quiz(
                    subject=choice(subjects),
                    grade=grade,
                    class_name=class_name,
                    region=region,
                    scheduled_date=datetime.now().date() + timedelta(days=randint(1, 10))
                )
            )

session.add_all(quizzes)
session.commit()

# -------------------- Submissions --------------------
submissions = []

for student in students:
    for i in range(2):  # Each student gets 2 assignments
        submissions.append(
            Submission(
                student_id=student.id,
                homework_title=f"Assignment {i+1}",
                submitted=choice([True, False]),
                submission_date=datetime.now().date() - timedelta(days=randint(1, 5))
            )
        )

session.add_all(submissions)
session.commit()

# -------------------- Quiz Scores (for past quizzes only) --------------------
scores = []
completed_quizzes = [q for q in quizzes if q.scheduled_date < datetime.now().date()]

for quiz in completed_quizzes:
    eligible_students = [
        s for s in students if
        s.grade == quiz.grade and s.class_name == quiz.class_name and s.region == quiz.region
    ]
    for student in eligible_students:
        scores.append(
            QuizScore(
                student_id=student.id,
                quiz_id=quiz.id,
                score=round(uniform(40, 100), 2)
            )
        )

session.add_all(scores)
session.commit()
session.close()

print("✅ Populated with ~400+ students, 75+ quizzes, and proper scores/submissions.")
