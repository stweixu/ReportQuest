import sqlite3
import time
import uuid
from src.reports.models.ReportModels import Report
from src.reports.services.OllamaAsync import OllamaChat
from src.reports.services.ReportService import ReportService
import asyncio

class PointsService:
    def __init__(self, conn: sqlite3.Connection, db_file: str = "database/users.db"):
        # Initialize the connection to the database
        self.conn = conn
        self.ollama = OllamaChat("llama3.2")
    
    def create_user(self, user_id: str) -> None:
        """Create the user in the User table with initial points set to 0 if it doesn't exist."""
        query = """
        INSERT INTO User (userID, userName, passwordHash, emailAddress, loginStatus, points,
                          notificationPreference, notificationEnabled, isAuthority, isModerator)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (user_id, "defaultUser", "", "", False, 0, "email", False, False, False))
        self.conn.commit()

    def check_user_exists(self, user_id: str) -> bool:
        """Check if a user exists in the User table. Create the user if they do not exist."""
        query = "SELECT userID FROM User WHERE userID = ?;"
        cursor = self.conn.cursor()
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        if result:
            return True
        else:
            self.create_user(user_id)
            return False

    def get_point_from_user_id(self, user_id: str) -> int:
        """Retrieve points for a specific user from the User table."""
        query = "SELECT points FROM User WHERE userID = ?;"
        cursor = self.conn.cursor()
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return 0

    def update_point_for_user_id(self, user_id: str, points: int, report_id: str) -> int:
        """Update points for a user in the User table and update the last update time."""
        # Ensure user exists before updating points
        if not self.check_user_exists(user_id):
            return 404  # Not Found

        query = "UPDATE User SET points = ? WHERE userID = ?;"
        cursor = self.conn.cursor()
        cursor.execute(query, (points, user_id))
        self.conn.commit()

        # Update points in the report
        report_service = ReportService(sqlite3.connect("database/reports.db"))
        report_service.update_report_points(report_id, points)
        if cursor.rowcount == 0:
            return 404  # Not Found
        return 200  # OK

    @staticmethod
    async def calculate_points(ratings: list[int]) -> int:
        """Calculate points based on rating factors."""
        return 2 * ratings[0] + 5 * ratings[1] + 3 * ratings[2]

    async def evaluate_points(self, user_id: str, image_path: str, text_description: str) -> int:
        """Evaluate points based on image and description analysis."""
        result = await self.ollama.analyse_image_and_text(image_path, "What is this image?", text_description)
        print(result["title"])
        if result["ratings"][0] < 5:
            return 0
        addable_points = await self.calculate_points(result["ratings"])
        return addable_points

    async def evaluate_and_add_points(self, report: Report) -> None:
        """Evaluate points and add them to the user based on report details."""
        print(f"Evaluating points for user_id: {report.user_id}")
        points = self.get_point_from_user_id(report.user_id)
        
        # Create a ReportService instance and create the report
        report_service = ReportService(sqlite3.connect("database/reports.db"))
        status_code, report = report_service.create_report(report)
        if status_code != 201:
            print("Failed to create report")
            return
        print(f"Report created with report ID {report.report_id}")

        # Evaluate new points
        new_points = await self.evaluate_points(report.user_id, report.image_path, report.description)
        if new_points:
            points += new_points
            self.update_point_for_user_id(report.user_id, points, report.report_id)

        # Identify the relevant authority
        result = await self.ollama.get_relevant_authority_ollama(report.description)
        print(f"Relevant authority: {result}")
        lat, long = report.location.split(",")
        nearest = await self.ollama.find_nearest_authority(float(lat), float(long), result)
        print(nearest)
        return

    async def wipe_clean(self) -> int:
        """Clear all data from the User table's points-related fields, retaining user info."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE User SET points = 0;")
            self.conn.commit()
            return 200  # OK
        except sqlite3.Error as e:
            print(f"Error wiping data from the User table's points: {e}")
            return 500  # Internal Server Error
