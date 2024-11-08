# from argon2 import PasswordHasher
# import jwt
# from datetime import datetime, timedelta
# from config import JWT_SECRET
# from src.users.models.UserModels import (
#     UserRegister,
#     UserCreate,
#     UserRead,
#     User,
#     UserLogin,
#     StatusResponse,
# )
# import sqlite3


# # ============== Service class for Auth model ===============
# class AuthService:
#     def __init__(self, conn: sqlite3.Connection):
#         self.conn = conn
#         self.ph: PasswordHasher = PasswordHasher()

#     def register(self, username: str, password: str, email: str):
#         """Register a new user.
#         takes in username, password, email.
#         need to hash password before storing in database.
#         returns status code"""
#         # check if username is already taken
#         query = "SELECT * FROM User WHERE userName = ?"
#         cursor = self.conn.cursor()
#         cursor.execute(query, (username.lower(),))
#         result = cursor.fetchone()
#         if result:
#             return (400, None)  # Bad Request user already exists
#         # check if email is already taken
#         query = "SELECT * FROM User WHERE emailAddress = ?"
#         cursor = self.conn.cursor()
#         cursor.execute(query, (email,))
#         result = cursor.fetchone()
#         if result:
#             return (400, None)  # Bad Request email already exists
#         # insert new user into database
#         hashed_password = self.ph.hash(password)
#         print("poop")
#         new_user = User(
#             userName=username.lower(),
#             passwordHash=hashed_password,
#             emailAddress=email,
#             loginStatus=False,
#             points=0,
#             notificationPreference="email",
#             notificationEnabled=True,
#             isAuthority=False,
#             isModerator=False,
#         )
#         insert_query = """
#         INSERT INTO User (userID, userName, passwordHash, emailAddress, loginStatus, points,
#                           notificationPreference, notificationEnabled, isAuthority, isModerator)
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
#         """
#         try:
#             cursor = self.conn.cursor()
#             cursor.execute(
#                 insert_query,
#                 (
#                     str(new_user.userID),
#                     new_user.userName,
#                     new_user.passwordHash,
#                     new_user.emailAddress,
#                     new_user.loginStatus,
#                     new_user.points,
#                     new_user.notificationPreference,
#                     new_user.notificationEnabled,
#                     new_user.isAuthority,
#                     new_user.isModerator,
#                 ),
#             )
#             self.conn.commit()
#             return (201, UserRead(**new_user.__dict__))  # Created
#         except sqlite3.IntegrityError as e:
#             print(e)
#             return (400, None)  # Bad request: userID already exists
#         except sqlite3.Error as e:
#             print(e)
#             return (500, None)  # Internal server error

#     def login(self, username: str, password: str):
#         """Login a user.
#         takes in password, compares with stored hash. returns JWT"""
#         query = "SELECT * FROM User WHERE userName = ?"
#         cursor = self.conn.cursor()
#         cursor.execute(query, (username,))
#         result = cursor.fetchone()
#         print(result)
#         if result:
#             # get the username and password from the database
#             user_id = result[0]
#             username = result[1]
#             password_hash = result[2]
#             isAuthority = result[8]
#             isModerator = result[9]
#             print(password_hash, password)
#             if self.ph.verify(password_hash, password):
#                 # create a new JWT token
#                 # to return jwt token and user_id
#                 token = jwt.encode(
#                     {
#                         "username": username,
#                         "user_id": user_id,
#                         "isAuthority": isAuthority,
#                         "isModerator": isModerator,
#                         "expiration": int(
#                             (datetime.now() + timedelta(hours=24)).timestamp()
#                         ),
#                     },
#                     JWT_SECRET,
#                     algorithm="HS256",
#                 )
#                 print({"token": token, "user_id": user_id})
#                 return 200, {"token": token, "user_id": user_id, "isAuthority": isAuthority,
#                         "isModerator": isModerator,}
#             else:
#                 return 401, None  # Unauthorized
#         else:
#             return 404, None  # Not Found

from argon2 import PasswordHasher
import jwt
from datetime import datetime, timedelta
import uuid
from config import JWT_SECRET
from src.users.models.UserModels import (
    UserCreate,
    UserRead,
    User,
)
from src.users.models.UnverifiedUsers import UnverifiedUser
import sqlite3
import yagmail
import os
from config import EMAIL_USER, EMAIL_PASSWORD, FRONTEND_URL
# ============== Service class for Auth model ===============
class AuthService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.ph: PasswordHasher = PasswordHasher()
        self.yag = yagmail.SMTP(EMAIL_USER, EMAIL_PASSWORD)

    def register(self, username: str, password: str, email: str):
        """Register a new unverified user and send a verification email."""
        # Check if username or email is already taken
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM User WHERE userName = ?", (username.lower(),))
        if cursor.fetchone():
            return 400, None  # Username already exists
        cursor.execute("SELECT * FROM User WHERE emailAddress = ?", (email,))

        # also check in the UnverifiedUser table
        cursor.execute("SELECT * FROM UnverifiedUser WHERE emailAddress = ?", (email,))
        if cursor.fetchone():
            return 400, None  # Email already exists in the UnverifiedUser table

        # also check in the User table
        cursor.execute("SELECT * FROM User WHERE emailAddress = ?", (email,))
        if cursor.fetchone():
            return 400, None  # Email already exists in the User table

        # Hash the password and create an unverified user entry
        hashed_password = self.ph.hash(password)
        unverified_user = UnverifiedUser.create_unverified(username.lower(), hashed_password, email)

        print("poop2")
        insert_query = """
        INSERT INTO UnverifiedUser (userID, userName, passwordHash, emailAddress, loginStatus, points,
                                    notificationPreference, notificationEnabled, isAuthority, isModerator, verificationKey)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        try:
            cursor.execute(
                insert_query,
                (
                    str(unverified_user.userID),
                    unverified_user.userName,
                    unverified_user.passwordHash,
                    unverified_user.emailAddress,
                    unverified_user.loginStatus,
                    unverified_user.points,
                    unverified_user.notificationPreference,
                    unverified_user.notificationEnabled,
                    unverified_user.isAuthority,
                    unverified_user.isModerator,
                    unverified_user.verificationKey,
                ),
            )
            self.conn.commit()
            self.send_verification_email(email, unverified_user.userName, unverified_user.verificationKey)
            return 200, {"message": "Verification email sent!"}
        except sqlite3.IntegrityError:
            return 400, None  # Duplicate entry
        except sqlite3.Error as e:
            print(e)
            return 500, None  # Internal server error

    def send_verification_email(self, email: str, username: str, verification_key: str) -> None:
        """Send verification email with a unique verification link."""
        subject = "Please Confirm Your Email to Complete Registration"
        verification_link = f"{FRONTEND_URL}/verify/{verification_key}"
        
        # Use an HTML email template for a more professional look
        body = f"""
        <html>
        <body>
            <p>Hello {username},</p>
            
            <p>Thank you for signing up with us! We’re excited to have you on board.</p>
            
            <p>To complete your registration, please confirm your email address by clicking the button below:</p>
            
            <p style="text-align: center;">
                <a href="{verification_link}" style="padding: 10px 20px; color: white; background-color: #4CAF50; text-decoration: none; border-radius: 5px;">
                    Confirm Email Address
                </a>
            </p>
            
            <p>If the button doesn’t work, copy and paste this link into your browser:</p>
            <p><a href="{verification_link}">{verification_link}</a></p>
            
            <p>Confirming your email helps us keep your account secure and ensures you’ll receive important updates.</p>
            
            <p>If you have any questions or didn’t sign up for this account, please reach out to our support team.</p>
            
            <p>Thank you,<br>
            The {os.getenv("COMPANY_NAME", "Your Company")} Team</p>
        </body>
        </html>
        """
        
        self.yag.send(to=email, subject=subject, contents=body)


    def verify_user(self, verification_key: str):
        """Verify an unverified user and move them to the main User table."""
        cursor = self.conn.cursor()
        query = "SELECT * FROM UnverifiedUser WHERE verificationKey = ?"
        cursor.execute(query, (verification_key,))
        user_data = cursor.fetchone()

        if not user_data:
            return 404, {"message": "Invalid or expired verification key."}

        # Map data to UnverifiedUser model
        verified_user = UserCreate(
            userID=user_data[0],
            userName=user_data[1],
            passwordHash=user_data[2],
            emailAddress=user_data[3],
            loginStatus=user_data[4],
            points=user_data[5],
            notificationPreference=user_data[6],
            notificationEnabled=user_data[7],
            isAuthority=user_data[8],
            isModerator=user_data[9],
            verificationKey=user_data[10],
        )

        # Convert to Verified User (UserCreate) using to_verified_user method
        # verified_user = unverified_user.to_verified_user()

        # Insert into the main User table and delete from UnverifiedUser table
        insert_query = """
        INSERT INTO User (userID, userName, passwordHash, emailAddress, loginStatus, points,
                          notificationPreference, notificationEnabled, isAuthority, isModerator)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        try:
            cursor.execute(
                insert_query,
                (
                    str(verified_user.userID),
                    verified_user.userName,
                    verified_user.passwordHash,
                    verified_user.emailAddress,
                    verified_user.loginStatus,
                    verified_user.points,
                    verified_user.notificationPreference,
                    verified_user.notificationEnabled,
                    verified_user.isAuthority,
                    verified_user.isModerator,
                ),
            )
            cursor.execute("DELETE FROM UnverifiedUser WHERE verificationKey = ?", (verification_key,))
            self.conn.commit()
            return 200, {"message": "User verified successfully."}
        except sqlite3.Error as e:
            print(f"Error verifying user: {e}")
            return 500, {"message": "Error verifying user."}

    def login(self, username: str, password: str):
        """Login a user by verifying password and returning a JWT if successful."""
        query = "SELECT * FROM User WHERE userName = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if result:
            user_id = result[0]
            password_hash = result[2]
            isAuthority = result[8]
            isModerator = result[9]
            if self.ph.verify(password_hash, password):
                token = jwt.encode(
                    {
                        "username": username,
                        "user_id": user_id,
                        "isAuthority": isAuthority,
                        "isModerator": isModerator,
                        "expiration": int((datetime.now() + timedelta(hours=24)).timestamp()),
                    },
                    JWT_SECRET,
                    algorithm="HS256",
                )
                return 200, {"token": token, "user_id": user_id, "isAuthority": isAuthority, "isModerator": isModerator}
            else:
                return 401, None  # Unauthorized
        else:
            return 404, None  # User not found