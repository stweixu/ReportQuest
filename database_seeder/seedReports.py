import time
from typing import Optional, List, Tuple
from pydantic import BaseModel
import sqlite3
import uuid
from faker import Faker
import random

class Report(BaseModel):
    user_id: str
    severity: int
    status: str
    report_id: str
    description: Optional[str]
    image_path: Optional[str]
    title: Optional[str]
    datetime: int
    location: str  # Ensure this is included if required

# Database connection
conn = sqlite3.connect("database/reports.db")

def create_report(report: Report) -> Tuple[int, Optional[Report]]:
    """Insert a new report into the Report table."""
    insert_query = """
        INSERT INTO Report (UserID, Severity, Status, ReportID, Description, imagePath, title, Datetime, Location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
    try:
        cursor = conn.cursor()
        cursor.execute(
            insert_query,
            (
                report.user_id,
                report.severity,
                report.status,
                report.report_id,
                report.description,
                report.image_path,
                report.title,  # No longer including UEN and assigned_authority_uen
                report.datetime,
                report.location
            ),
        )
        conn.commit()
        return 201, report  # Created
    except sqlite3.IntegrityError as e:
        print(e)
        return 400, None  # Bad request: report_id already exists
    except sqlite3.Error as e:
        print(f"Error inserting report: {e}")
        return 500, None  # Internal server error

fake: Faker = Faker()

predefined_uuids = [
    uuid.UUID("123e4567-e89b-12d3-a456-426614174000"),
    uuid.UUID("123e4567-e89b-12d3-a456-426614174001"),
    uuid.UUID("123e4567-e89b-12d3-a456-426614174002"),
    uuid.UUID("123e4567-e89b-12d3-a456-426614174003"),
    uuid.UUID("123e4567-e89b-12d3-a456-426614174004"),
    uuid.UUID("123e4567-e89b-12d3-a456-426614174005"),
]

def generate_fake_reports(num_reports: int) -> List[Report]:
    """Generate a list of fake Report entries."""
    reports = []
    status_options = ["Pending", "In Progress", "Resolved"]

    for i in range(num_reports):
        report = Report(
            user_id=str(predefined_uuids[i % len(predefined_uuids)]),
            severity=fake.random_int(min=1, max=10),
            status=random.choice(status_options),
            report_id=str(uuid.uuid4()),
            description=fake.sentence(nb_words=10),
            image_path=fake.file_path(extension="jpg"),
            title=fake.catch_phrase(),
            datetime=int(time.time()),  # Add a datetime field if required
            location=f"{random.randint(1, 100)}.{random.randint(1, 100)},{random.randint(1, 100)}.{random.randint(1, 100)}"  # Add a location field if required
        )
        reports.append(report)

    return reports

# Generate 10 fake report entries
fake_reports = generate_fake_reports(10)

for report in fake_reports:
    status_code, _ = create_report(report)
    if status_code == 201:
        print(f"Successfully inserted report: {report.report_id}")
    else:
        print(f"Failed to insert report: {report.report_id}")

# Close the database connection
conn.close()
