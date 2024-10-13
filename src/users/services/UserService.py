import sqlite3
import uuid
from typing import Literal, Optional, Tuple, List
from pydantic import BaseModel, Field

# ========= pydantic models for FASTAPI requests ============
class UserCreate(BaseModel):
    userID: uuid.UUID = Field(default_factory=uuid.uuid4)
    userName: str
    passwordHash: str
    emailAddress: str
    loginStatus: bool
    points: int
    notificationPreference: Literal['email', 'sms', 'push']
    notificationEnabled: bool
    isAuthority: bool
    isModerator: bool

class UserRead(BaseModel):
    userID: uuid.UUID
    userName: str
    emailAddress: str
    loginStatus: bool
    points: int
    notificationEnabled: bool
    isAuthority: bool
    isModerator: bool


# ============== Entity class for the User model ===============
class User:
    def __init__(self, 
                 userName: str, 
                 passwordHash: str, 
                 emailAddress: str, 
                 loginStatus: bool, 
                 points: int, 
                 notificationPreference: Literal['email', 'sms', 'push'], 
                 notificationEnabled: bool, 
                 isAuthority: bool, 
                 isModerator: bool,
                 userID: uuid.UUID = None):
        self.userID: uuid.UUID = userID if userID else uuid.uuid4()
        self.userName: str = userName
        self.passwordHash: str = passwordHash
        self.emailAddress: str = emailAddress
        self.loginStatus: bool = loginStatus
        self.points: int = points
        self.notificationPreference: Literal['email', 'sms', 'push'] = notificationPreference
        self.notificationEnabled: bool = notificationEnabled
        self.isAuthority: bool = isAuthority
        self.isModerator: bool = isModerator

    def __repr__(self) -> str:
        return (f"User(userID={self.userID}, userName={self.userName}, email={self.emailAddress}, "
                f"loginStatus={self.loginStatus}, points={self.points}, "
                f"notificationEnabled={self.notificationEnabled}, isAuthority={self.isAuthority}, "
                f"isModerator={self.isModerator})")


# ============== Service class for the User model ===============
# ============== Used to interact with database ================
class UserService:
    def __init__(self, db_file: str = 'database/users.db'):
        """Initialize the UserService with a connection to the SQLite database."""
        self.conn = sqlite3.connect(db_file)
        # self.create_user_table()

    def create_user_table(self):
        """Create the User table if it doesn't exist."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS User (
            userID TEXT PRIMARY KEY,
            userName TEXT NOT NULL,
            passwordHash TEXT NOT NULL,
            emailAddress TEXT NOT NULL,
            loginStatus BOOLEAN NOT NULL,
            points INTEGER NOT NULL,
            notificationPreference TEXT CHECK(notificationPreference IN ('email', 'sms', 'push')),
            notificationEnabled BOOLEAN NOT NULL,
            isAuthority BOOLEAN NOT NULL,
            isModerator BOOLEAN NOT NULL
        );
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(create_table_query)
            self.conn.commit()
            print("User table created successfully.")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def create_user(self, user: User) -> Tuple[int, Optional[UserRead]]:
        """Insert a new user into the User table."""
        insert_query = """
        INSERT INTO User (userID, userName, passwordHash, emailAddress, loginStatus, points,
                          notificationPreference, notificationEnabled, isAuthority, isModerator)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(insert_query, (str(user.userID), user.userName, user.passwordHash, user.emailAddress,
                                          user.loginStatus, user.points, user.notificationPreference,
                                          user.notificationEnabled, user.isAuthority, user.isModerator))
            self.conn.commit()
            return 201, UserRead(**user.__dict__)  # Created
        except sqlite3.IntegrityError:
            return 400, None  # Bad request: userID already exists
        except sqlite3.Error as e:
            return 500, None  # Internal server error

    def read_all_users(self) -> Tuple[int, List[UserRead]]:
        """Fetch all users from the User table."""
        select_query = "SELECT * FROM User;"
        cursor = self.conn.cursor()
        cursor.execute(select_query)
        results = cursor.fetchall()
        
        users = [
            UserRead(
                userID=uuid.UUID(result[0]),  # Ensure proper UUID conversion
                userName=result[1],
                emailAddress=result[3],
                loginStatus=bool(result[4]),  # Ensure boolean conversion
                points=result[5],
                notificationEnabled=bool(result[7]),  # Ensure boolean conversion
                isAuthority=bool(result[8]),  # Ensure boolean conversion
                isModerator=bool(result[9])  # Ensure boolean conversion
            )
            for result in results
        ]
        return 200, users  # OK

    def read_user(self, user_id: uuid.UUID) -> Tuple[int, Optional[UserRead]]:
        """Fetch a user's details from the User table by userID."""
        select_query = "SELECT * FROM User WHERE userID = ?;"
        cursor = self.conn.cursor()
        cursor.execute(select_query, (str(user_id),))
        result = cursor.fetchone()
        if result:
            user = UserRead(
                userID=uuid.UUID(result[0]),
                userName=result[1],
                emailAddress=result[3],
                loginStatus=bool(result[4]),
                points=result[5],
                notificationEnabled=bool(result[7]),
                isAuthority=bool(result[8]),
                isModerator=bool(result[9])
            )
            return 200, user  # OK
        else:
            return 404, None  # Not Found

    def update_user_points(self, user_id: uuid.UUID, points: int) -> int:
        """Update a user's points in the User table."""
        update_query = "UPDATE User SET points = ? WHERE userID = ?;"
        cursor = self.conn.cursor()
        cursor.execute(update_query, (points, str(user_id)))
        self.conn.commit()
        if cursor.rowcount == 0:
            return 404  # Not Found
        return 200  # OK

    def delete_user(self, user_id: uuid.UUID) -> int:
        """Delete a user from the User table by userID."""
        delete_query = "DELETE FROM User WHERE userID = ?;"
        cursor = self.conn.cursor()
        cursor.execute(delete_query, (str(user_id),))
        self.conn.commit()
        if cursor.rowcount == 0:
            return 404  # Not Found
        return 200  # OK

    def wipeClean(self) -> int:
        """Delete all data from the User table, keeping the table structure intact."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM User;")  # This will delete all rows from the User table
            self.conn.commit()
            return 200  # OK
        except sqlite3.Error as e:
            print(f"Error wiping data from the User table: {e}")
            return 500  # Internal Server Error

    def close_connection(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")
