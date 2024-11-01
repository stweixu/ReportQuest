from argon2 import PasswordHasher
import jwt
from datetime import datetime, timedelta
from config import JWT_SECRET
from src.users.models.UserModels import (
    UserRegister,
    UserCreate,
    UserRead,
    User,
    UserLogin,
    StatusResponse,
)
import sqlite3


# ============== Service class for Auth model ===============
class AuthService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.ph: PasswordHasher = PasswordHasher()

    def register(self, username: str, password: str, email: str):
        """Register a new user.
        takes in username, password, email.
        need to hash password before storing in database.
        returns status code"""
        # check if username is already taken
        query = "SELECT * FROM User WHERE userName = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (username.lower(),))
        result = cursor.fetchone()
        if result:
            return (400, None)  # Bad Request user already exists
        # check if email is already taken
        query = "SELECT * FROM User WHERE emailAddress = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        if result:
            return (400, None)  # Bad Request email already exists
        # insert new user into database
        hashed_password = self.ph.hash(password)
        print("poop")
        new_user = User(
            userName=username.lower(),
            passwordHash=hashed_password,
            emailAddress=email,
            loginStatus=False,
            points=0,
            notificationPreference="email",
            notificationEnabled=True,
            isAuthority=False,
            isModerator=False,
        )
        insert_query = """
        INSERT INTO User (userID, userName, passwordHash, emailAddress, loginStatus, points,
                          notificationPreference, notificationEnabled, isAuthority, isModerator)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                insert_query,
                (
                    str(new_user.userID),
                    new_user.userName,
                    new_user.passwordHash,
                    new_user.emailAddress,
                    new_user.loginStatus,
                    new_user.points,
                    new_user.notificationPreference,
                    new_user.notificationEnabled,
                    new_user.isAuthority,
                    new_user.isModerator,
                ),
            )
            self.conn.commit()
            return (201, UserRead(**new_user.__dict__))  # Created
        except sqlite3.IntegrityError as e:
            print(e)
            return (400, None)  # Bad request: userID already exists
        except sqlite3.Error as e:
            print(e)
            return (500, None)  # Internal server error

    def login(self, username: str, password: str):
        """Login a user.
        takes in password, compares with stored hash. returns JWT"""
        query = "SELECT * FROM User WHERE userName = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        print(result)
        if result:
            # get the username and password from the database
            user_id = result[0]
            username = result[1]
            password_hash = result[2]
            isAuthority = result[8]
            isModerator = result[9]
            print(password_hash, password)
            if self.ph.verify(password_hash, password):
                # create a new JWT token
                # to return jwt token and user_id
                token = jwt.encode(
                    {
                        "username": username,
                        "user_id": user_id,
                        "isAuthority": isAuthority,
                        "isModerator": isModerator,
                        "expiration": int(
                            (datetime.now() + timedelta(hours=24)).timestamp()
                        ),
                    },
                    JWT_SECRET,
                    algorithm="HS256",
                )
                print({"token": token, "user_id": user_id})
                return 200, {"token": token, "user_id": user_id}
            else:
                return 401, None  # Unauthorized
        else:
            return 404, None  # Not Found
