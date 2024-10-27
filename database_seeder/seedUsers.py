from typing import Literal
import uuid
import sqlite3


class User:
    def __init__(
        self,
        userName: str,
        passwordHash: str,
        emailAddress: str,
        loginStatus: bool,
        points: int,
        notificationPreference: Literal["email", "sms", "push"],
        notificationEnabled: bool,
        isAuthority: bool,
        isModerator: bool,
        userID: uuid.UUID = None,
    ):
        self.userID: uuid.UUID = userID if userID else uuid.uuid4()
        self.userName: str = userName
        self.passwordHash: str = passwordHash
        self.emailAddress: str = emailAddress
        self.loginStatus: bool = loginStatus
        self.points: int = points
        self.notificationPreference: Literal["email", "sms", "push"] = (
            notificationPreference
        )
        self.notificationEnabled: bool = notificationEnabled
        self.isAuthority: bool = isAuthority
        self.isModerator: bool = isModerator

    def __repr__(self) -> str:
        return (
            f"User(userID={self.userID}, userName={self.userName}, email={self.emailAddress}, "
            f"loginStatus={self.loginStatus}, points={self.points}, "
            f"notificationEnabled={self.notificationEnabled}, isAuthority={self.isAuthority}, "
            f"isModerator={self.isModerator})"
        )


conn = sqlite3.connect("database/users.db")


def create_user(user: User) -> None:
    """Insert a new user into the User table."""
    insert_query = """
    INSERT INTO User (userID, userName, passwordHash, emailAddress, loginStatus, points,
                      notificationPreference, notificationEnabled, isAuthority, isModerator)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            insert_query,
            (
                str(user.userID),
                user.userName,
                user.passwordHash,
                user.emailAddress,
                user.loginStatus,
                user.points,
                user.notificationPreference,
                user.notificationEnabled,
                user.isAuthority,
                user.isModerator,
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(e)
        return 400, None  # Bad request: userID already exists
    except sqlite3.Error as e:
        print(f"Error inserting user: {e}")
        return 500, None  # Internal server error


from argon2 import PasswordHasher

# Initialize the Argon2 PasswordHasher
ph = PasswordHasher()

# Dummy users based on the image members
# Predefined UUIDs for reproducible seeding
predefined_uuids = [
    uuid.UUID("123e4567-e89b-12d3-a456-426614174000"),
    uuid.UUID("123e4567-e89b-12d3-a456-426614174001"),
    uuid.UUID("123e4567-e89b-12d3-a456-426614174002"),
    uuid.UUID("123e4567-e89b-12d3-a456-426614174003"),
    uuid.UUID("123e4567-e89b-12d3-a456-426614174004"),
    uuid.UUID("123e4567-e89b-12d3-a456-426614174005"),
]

# Dummy users with explicit UUIDs for reproducibility
dummy_users = [
    User(
        userName="jingxiang1",
        passwordHash=ph.hash("password1"),
        emailAddress="jingxiang@example.com",
        loginStatus=False,
        points=0,
        notificationPreference="email",
        notificationEnabled=True,
        isAuthority=False,
        isModerator=False,
        userID=predefined_uuids[0],
    ),
    User(
        userName="jinjie1",
        passwordHash=ph.hash("password1"),
        emailAddress="jj@example.com",
        loginStatus=False,
        points=0,
        notificationPreference="sms",
        notificationEnabled=True,
        isAuthority=False,
        isModerator=False,
        userID=predefined_uuids[1],
    ),
    User(
        userName="yunle1",
        passwordHash=ph.hash("password1"),
        emailAddress="yunle@example.com",
        loginStatus=False,
        points=0,
        notificationPreference="push",
        notificationEnabled=True,
        isAuthority=False,
        isModerator=False,
        userID=predefined_uuids[2],
    ),
    User(
        userName="weixu",
        passwordHash=ph.hash("password1"),
        emailAddress="weixu@example.com",
        loginStatus=False,
        points=0,
        notificationPreference="email",
        notificationEnabled=True,
        isAuthority=False,
        isModerator=False,
        userID=predefined_uuids[3],
    ),
    User(
        userName="amogh1",
        passwordHash=ph.hash("password1"),
        emailAddress="amogh.sriman@example.com",
        loginStatus=False,
        points=0,
        notificationPreference="sms",
        notificationEnabled=True,
        isAuthority=True,
        isModerator=False,
        userID=predefined_uuids[4],
    ),
    User(
        userName="maxwell1",
        passwordHash=ph.hash("password1"),
        emailAddress="maxwell@example.com",
        loginStatus=False,
        points=0,
        notificationPreference="sms",
        notificationEnabled=True,
        isAuthority=True,
        isModerator=False,
        userID=predefined_uuids[5],
    ),
]

# Insert each dummy user into the database
for user in dummy_users:
    create_user(user)

conn.close()
