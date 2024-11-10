import sqlite3
import time
from typing import Optional, Tuple, List
import uuid
from src.posts.services.AuthorityService import AuthorityService
from src.posts.models.PostModel import (
    Post,
)  # Assuming the Post model is stored in this location


class PostService:
    @staticmethod
    def get_connection_instance() -> sqlite3.Connection:
        """Establish a new connection to the database."""
        return sqlite3.connect("database/posts.db")

    @staticmethod
    def create_post_table():
        """Create the Post table if it doesn't exist."""
        conn = PostService.get_connection_instance()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS Post (
            PostID TEXT PRIMARY KEY,
            Title TEXT,
            Description TEXT,
            imagePath TEXT,
            AuthorityName TEXT NOT NULL,
            UserName TEXT,
            UserID TEXT
        );
        """
        try:
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
            print("Post table created successfully with updated schema.")
        except sqlite3.Error as e:
            print(f"Error creating Post table: {e}")
        finally:
            conn.close()

    @staticmethod
    def create_entry(post: Post) -> Tuple[int, Optional[Post]]:
        """Insert a new post into the Post table."""
        conn = PostService.get_connection_instance()
        insert_query = """
        INSERT INTO Post (PostID, Title, Description, imagePath, AuthorityName, UserName, UserID, time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        try:
            cursor = conn.cursor()
            cursor.execute(
                insert_query,
                (
                    post.post_id,
                    post.title,
                    post.description,
                    post.image_path,
                    post.authority_name,
                    post.user_name,
                    post.user_id,
                    post.time,
                ),
            )
            conn.commit()
            return 201, post  # Created
        except sqlite3.IntegrityError as e:
            print(e)
            return 400, None  # Bad request: post_id already exists
        except sqlite3.Error as e:
            print(f"Error inserting post: {e}")
            return 500, None  # Internal server error
        finally:
            conn.close()

    @staticmethod
    def update_entry(
        post_id: str,
        new_title: Optional[str] = None,
        new_description: Optional[str] = None,
        new_image_path: Optional[str] = None,
        new_authority_name: Optional[str] = None,
        new_user_id: Optional[str] = None,
    ) -> int:
        """Update fields of an existing post by post_id."""
        conn = PostService.get_connection_instance()
        update_fields = []
        params = []

        if new_title:
            update_fields.append("Title = ?")
            params.append(new_title)
        if new_description:
            update_fields.append("Description = ?")
            params.append(new_description)
        if new_image_path:
            update_fields.append("imagePath = ?")
            params.append(new_image_path)
        if new_authority_name:
            update_fields.append("AuthorityName = ?")
            params.append(new_authority_name)
        if new_user_id:
            update_fields.append("UserID = ?")
            params.append(new_user_id)

        if not update_fields:
            print("No fields to update.")
            return 400  # Bad request

        params.append(post_id)
        update_query = f"UPDATE Post SET {', '.join(update_fields)} WHERE PostID = ?;"

        try:
            cursor = conn.cursor()
            cursor.execute(update_query, tuple(params))
            conn.commit()
            if cursor.rowcount == 0:
                return 404  # Not Found
            return 200  # OK
        except sqlite3.Error as e:
            print(f"Error updating post: {e}")
            return 500  # Internal server error
        finally:
            conn.close()

    @staticmethod
    def delete_entry(post_id: str) -> int:
        """Delete a post from the Post table by post_id."""
        conn = PostService.get_connection_instance()
        delete_query = "DELETE FROM Post WHERE PostID = ?;"
        try:
            cursor = conn.cursor()
            cursor.execute(delete_query, (post_id,))
            conn.commit()
            if cursor.rowcount == 0:
                return 404  # Not Found
            return 200  # OK
        except sqlite3.Error as e:
            print(f"Error deleting post: {e}")
            return 500  # Internal server error
        finally:
            conn.close()

    @staticmethod
    def read_entry(post_id: str) -> Tuple[int, Optional[Post]]:
        """Fetch a post by post_id."""
        conn = PostService.get_connection_instance()
        query = "SELECT * FROM Post WHERE PostID = ?;"
        try:
            cursor = conn.cursor()
            cursor.execute(query, (post_id,))
            result = cursor.fetchone()
            if result:
                post = PostService.parse_entry(result)
                return 200, post  # OK
            else:
                return 404, None  # Not Found
        except sqlite3.Error as e:
            print(f"Error reading post: {e}")
            return 500, None  # Internal server error
        finally:
            conn.close()

    @staticmethod
    def read_all_entries() -> Tuple[int, List[Post]]:
        """Fetch all posts from the Post table."""
        conn = PostService.get_connection_instance()
        query = "SELECT * FROM Post;"
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            posts = [PostService.parse_entry(row) for row in results]
            return 200, posts  # OK
        except sqlite3.Error as e:
            print(f"Error reading all posts: {e}")
            return 500, []  # Internal server error
        finally:
            conn.close()

    @staticmethod
    def parse_entry(result: Tuple) -> Post:
        """Convert a database row into a Post instance."""
        return Post(
            post_id=result[0],
            title=result[1],
            description=result[2],
            image_path=result[3],
            authority_name=result[4],
            user_name=result[5],
            user_id=result[6],
            time=result[7],
        )

    @staticmethod
    def get_user_name(user_id: str) -> Optional[str]:
        """Fetch the user name from the user.db based on the user_id."""
        conn = sqlite3.connect("database/users.db")
        query = "SELECT UserName FROM User WHERE UserID = ?;"
        try:
            cursor = conn.cursor()
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            if result:
                return result[0]  # UserName
            return None  # User not found
        except sqlite3.Error as e:
            print(f"Error retrieving user name: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def create_post_with_authority(
        user_id: str, post: Post
    ) -> Tuple[int, Optional[Post]]:
        """Create a new post using the authority name and user name retrieved from their respective databases."""
        # Use AuthorityService to fetch the authority name associated with the user_id
        status_code, authority = AuthorityService.read_entry(user_id)
        if status_code != 200 or not authority:
            print(f"No authority found with user_id: {user_id}")
            return 404, None  # Not Found

        # Retrieve the authority name from the Authority entry
        authority_name = authority.authority_name

        # Retrieve the user name from the Users database
        user_name = PostService.get_user_name(user_id)
        if not user_name:
            print(f"No user found with user_id: {user_id}")
            return 404, None  # Not Found

        # Update the post object with a generated post_id, authority name, user name, and user_id
        post_id = str(uuid.uuid4())  # Generate a unique post_id
        post = Post(
            post_id=post_id,
            title=post.title,
            description=post.description,
            image_path=post.image_path,
            authority_name=authority_name,
            user_name=user_name,
            user_id=user_id,
            time=int(time.time()),
        )

        # Insert the post into the Post database
        conn = PostService.get_connection_instance()
        insert_query = """
        INSERT INTO Post (PostID, Title, Description, imagePath, AuthorityName, UserName, UserID, time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        try:
            cursor = conn.cursor()
            cursor.execute(
                insert_query,
                (
                    post.post_id,
                    post.title,
                    post.description,
                    post.image_path,
                    post.authority_name,
                    post.user_name,
                    post.user_id,
                    post.time,
                ),
            )
            conn.commit()
            print(f"Post created successfully with post_id: {post_id}")
            return 201, post  # Created
        except sqlite3.IntegrityError as e:
            print(f"Error: post_id already exists - {e}")
            return 400, None  # Bad request
        except sqlite3.Error as e:
            print(f"Error inserting post: {e}")
            return 500, None  # Internal server error
        finally:
            conn.close()
