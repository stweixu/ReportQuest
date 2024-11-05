import sqlite3
from typing import List, Tuple, Optional
from src.reports.models.ReportModels import Report  # Assuming the Report model is stored here
from src.users.services.UserService import UserService


class ReportService:
    def __init__(self, conn: sqlite3.Connection):
        """Initialize the ReportService with a connection to the SQLite database."""
        self.conn = conn

    def create_report_table(self):
        """Create the Report table if it doesn't exist."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS Report (
            UserID TEXT NOT NULL,
            Severity INTEGER NOT NULL,
            Status TEXT CHECK(Status IN ('Pending', 'In Progress', 'Resolved')),
            ReportID TEXT PRIMARY KEY,
            Description TEXT,
            imagePath TEXT,
            title TEXT,
            Datetime INTEGER NOT NULL,
            Location TEXT NOT NULL
        );
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(create_table_query)
            self.conn.commit()
            print("Report table created successfully.")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def create_report(self, report: Report) -> Tuple[int, Optional[Report]]:
        """Insert a new report into the Report table."""
        insert_query = """
        INSERT INTO Report (UserID, Severity, Status, ReportID, Description, imagePath, title, Datetime, Location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                insert_query,
                (
                    report.user_id,
                    report.severity,
                    report.status,
                    report.report_id,
                    report.description,
                    report.image_path,
                    report.title,
                    report.datetime,
                    report.location,
                ),
            )
            self.conn.commit()
            return 201, report  # Created
        except sqlite3.IntegrityError as e:
            print(e)
            return 400, None  # Bad request: report_id already exists
        except sqlite3.Error as e:
            print(f"Error inserting report: {e}")
            return 500, None  # Internal server error

    def read_report_by_user_id(self, user_id: str) -> Tuple[int, List[Report]]:
        """Fetch all reports from the Report table by user ID."""
        query = "SELECT * FROM Report WHERE UserID = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        reports = [Report(**self._parse_report(result)) for result in results]
        return 200, reports  # OK

    def get_top_k_reports_by_severity(
        self, k: int, resolved: bool = False
    ) -> Tuple[int, List[Report]]:
        """Fetch top k reports from the Report table by severity."""
        query = "SELECT * FROM Report ORDER BY Severity DESC LIMIT ?"
        if not resolved:
            query = "SELECT * FROM Report WHERE Status = 'Pending' ORDER BY Severity DESC LIMIT ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (k,))
        results = cursor.fetchall()
        reports = [Report(**self._parse_report(result)) for result in results]
        return 200, reports  # OK

    def read_report_by_id(self, report_id: str) -> Tuple[int, Optional[Report]]:
        """Fetch a report by ReportID."""
        query = "SELECT * FROM Report WHERE ReportID = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (report_id,))
        result = cursor.fetchone()
        if result:
            return 200, Report(**self._parse_report(result))  # OK
        else:
            return 404, None  # Not Found

    def search_reports_by_description(
        self, description: str
    ) -> Tuple[int, List[Report]]:
        """Search reports by description using wildcards."""
        query = "SELECT * FROM Report WHERE Description LIKE ?"
        wildcard_description = f"%{description}%"
        cursor = self.conn.cursor()
        cursor.execute(query, (wildcard_description,))
        results = cursor.fetchall()
        reports = [Report(**self._parse_report(result)) for result in results]
        return 200, reports  # OK

    def search_reports_by_title(self, title: str) -> Tuple[int, List[Report]]:
        """Search reports by title using wildcards."""
        query = "SELECT * FROM Report WHERE title LIKE ?"
        wildcard_title = f"%{title}%"
        cursor = self.conn.cursor()
        cursor.execute(query, (wildcard_title,))
        results = cursor.fetchall()
        reports = [Report(**self._parse_report(result)) for result in results]
        return 200, reports  # OK

    def delete_report_by_id(self, report_id: str) -> int:
        """Delete a report from the Report table by ReportID."""
        delete_query = "DELETE FROM Report WHERE ReportID = ?"
        cursor = self.conn.cursor()
        cursor.execute(delete_query, (report_id,))
        self.conn.commit()
        if cursor.rowcount == 0:
            return 404  # Not Found
        return 200  # OK

    def _parse_report(self, result: Tuple) -> dict:
        """Helper method to parse a database row into a Report dictionary."""
        return {
            "user_id": result[0],
            "severity": result[1],
            "status": result[2],
            "report_id": result[3],
            "description": result[4],
            "image_path": result[5],
            "title": result[6],
            "datetime": result[7],
            "location": result[8],
        }

    def close_connection(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

    def update_report_points(self, report_id: str, points: int) -> int:
        """Update the points of a report in the database."""
        update_query = "UPDATE Report SET Severity = ? WHERE ReportID = ?"
        cursor = self.conn.cursor()
        cursor.execute(update_query, (points, report_id))
        self.conn.commit()
        return 200

    def check_user_exists(self, user_id: str) -> bool:
        """Check if a user exists in the database using UserService."""
        return UserService(sqlite3.connect("database/users.db")).check_user_exists(user_id)
