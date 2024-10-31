# RewardService.py
import sqlite3
from typing import List, Optional, Tuple
from src.rewards.models.RewardModel import Reward  # Adjust import based on your project structure

class RewardService:
    def __init__(self, conn : sqlite3.Connection):
        self.conn = conn
        self.create_reward_table()

    def create_reward_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS Reward (
            RewardID TEXT PRIMARY KEY,
            Description TEXT NOT NULL,
            PointsRequired INTEGER NOT NULL,
            Validity INTEGER,
            Availability INTEGER NOT NULL,
            UserID TEXT
        );
        """
        cursor = self.conn.cursor()
        cursor.execute(create_table_query)
        self.conn.commit()

    def create_reward(self, reward: Reward) -> int:
        insert_query = """
        INSERT INTO Reward (RewardID, Description, PointsRequired, Validity, Availability, UserID)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                insert_query,
                (
                    reward.rewardID,
                    reward.description,
                    reward.pointsRequired,
                    reward.validity,
                    reward.availability,
                    reward.userID,
                ),
            )
            self.conn.commit()
            return 201  # Created
        except sqlite3.IntegrityError:
            return 400  # RewardID already exists
        except sqlite3.Error as e:
            print(f"Error inserting reward: {e}")
            return 500  # Internal Server Error

    def read_all_rewards(self) -> Tuple[int, List[Reward]]:
        select_query = "SELECT * FROM Reward;"
        cursor = self.conn.cursor()
        cursor.execute(select_query)
        results = cursor.fetchall()

        rewards = [
            Reward(
                rewardID=result[0],
                description=result[1],
                pointsRequired=result[2],
                validity=result[3],
                availability=result[4],
                userID=result[5],
            )
            for result in results
        ]
        return 200, rewards

    def read_reward(self, reward_id: str) -> Tuple[int, Optional[Reward]]:
        select_query = "SELECT * FROM Reward WHERE RewardID = ?;"
        cursor = self.conn.cursor()
        cursor.execute(select_query, (reward_id,))
        result = cursor.fetchone()
        if result:
            reward = Reward(
                rewardID=result[0],
                description=result[1],
                pointsRequired=result[2],
                validity=result[3],
                availability=result[4],
                userID=result[5],
            )
            return 200, reward
        else:
            return 404, None  # Not Found

    def update_reward_availability(self, reward_id: str, availability: int) -> int:
        update_query = "UPDATE Reward SET Availability = ? WHERE RewardID = ?;"
        cursor = self.conn.cursor()
        cursor.execute(update_query, (availability, reward_id))
        self.conn.commit()
        return 200 if cursor.rowcount > 0 else 404

    def delete_reward(self, reward_id: str) -> int:
        delete_query = "DELETE FROM Reward WHERE RewardID = ?;"
        cursor = self.conn.cursor()
        cursor.execute(delete_query, (reward_id,))
        self.conn.commit()
        return 200 if cursor.rowcount > 0 else 404

    def close_connection(self):
        if self.conn:
            self.conn.close()
            print("Database connection closed.")
