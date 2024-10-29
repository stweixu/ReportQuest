import sqlite3
import time
from src.reports.services.OllamaAsync import OllamaChat
import asyncio


class PointsService:
    def __init__(self, conn: sqlite3.Connection, db_file: str = "database/points.db"):
        # initialize the connection to the database
        self.conn = conn
        self.ollama = OllamaChat("llama3.2")
        # create the points table if it doesn't exist
        pass

    def create_user(self, user_id: str) -> None:
        # create the user in the points db and table
        print(user_id, user_id == None)
        query = "INSERT INTO Points (UserID, points, LastUpdated) VALUES (?, ?, ?);"
        cursor = self.conn.cursor()
        cursor.execute(query, (user_id, 0, int(time.time())))
        self.conn.commit()
        return

    def check_user_exists(self, user_id: str) -> bool:
        # look up the points db and table
        # return True if the user exists, False otherwise
        query = "SELECT UserID FROM Points WHERE UserID = ?;"
        cursor = self.conn.cursor()
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        if result:
            return True
        else:
            # create the user if it doesn't exist
            self.create_user(user_id)
            return False

    def get_point_from_user_id(self, user_id: str) -> int:
        # look up the points db and table
        # return the points
        query = "SELECT points FROM Points WHERE UserID = ?;"
        cursor = self.conn.cursor()
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return 0

    def update_point_for_user_id(self, user_id: str, points: int) -> int:
        # look up the points db and table
        # check user exists
        self.check_user_exists(user_id)
        # update the points and the last updated time
        print(points, user_id)
        print(int(time.time()))
        query = "UPDATE Points SET points = ?, LastUpdated = ? WHERE UserID = ?;"
        cursor = self.conn.cursor()
        cursor.execute(query, (points, int(time.time()), user_id))
        self.conn.commit()
        if cursor.rowcount == 0:
            return 404  # Not Found
        return 200  # OK

    @staticmethod
    async def calculate_points(ratings: list[int]) -> None:
        # calculate the points based on the ratings
        # return the points
        return 2 * ratings[0] + 5 * ratings[1] + 3 * ratings[2]

    async def evalute_points(
        self, user_id: str, image_path: str, text_description: str
    ) -> int:
        # get the title from the image and text description
        result = await self.ollama.analyse_image_and_text(
            image_path, "What is this image?", text_description
        )
        print(result["title"])
        # relevance of the title not high enough, reject, add to manual moderator queue
        if result["ratings"][0] < 5:
            # add to moderator queue
            return 0
        addable_points = await self.calculate_points(result["ratings"])
        return addable_points

    async def evaluate_and_add_points(
        self, user_id: str, image_path: str, text_description: str
    ) -> None:
        # get the points from the user_id
        print("thinking....")
        points = self.get_point_from_user_id(user_id)
        # add the points to the user_id
        new_points = await self.evalute_points(user_id, image_path, text_description)
        if new_points:
            points += new_points
            self.update_point_for_user_id(user_id, points)
        return

    async def wipeClean(self) -> int:
        # delete all data from the points table, keeping the table structure intact
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "DELETE FROM Points;"
            )  # This will delete all rows from the Points table
            self.conn.commit()
            return 200  # OK
        except sqlite3.Error as e:
            print(f"Error wiping data from the Points table: {e}")
            return 500  # Internal Server Error


# tests
# async def main():
#     ps = PointsService(sqlite3.connect("database/points.db"))
#     # ps.create_user("123e4567-e89b-12d3-a456-426614174000")
#     print(ps.get_point_from_user_id("123e4567-e89b-12d3-a456-426614174000"))
#     ps.update_point_for_user_id("123e4567-e89b-12d3-a456-426614174000", 10)
#     print(ps.get_point_from_user_id("123e4567-e89b-12d3-a456-426614174000"))
#     res_task = asyncio.create_task(
#         ps.evaluate_and_add_points(
#             "123e4567-e89b-12d3-a456-426614174000",
#             "images/image.png",
#             "Man falling over, with crutches. He is wearing a blue shirt and black pants. The man is sitting on a bench and is looking down at the ground. There are trees in the background.",
#         )
#     )

#     await asyncio.sleep(30)
#     res = await res_task
#     print(res)


# if __name__ == "__main__":
#     asyncio.run(main())
