import sqlite3
from typing import Optional, Tuple, List
from src.posts.models.PostModel import Post  # Assuming the Post model is stored in this location


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
            Description TEXT,
            imagePath TEXT,
            AuthorityName TEXT NOT NULL
        );
        """
        try:
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
            print("Post table created successfully.")
        except sqlite3.Error as e:
            print(f"Error creating Post table: {e}")
        finally:
            conn.close()

    @staticmethod
    def create_entry(post: Post) -> Tuple[int, Optional[Post]]:
        """Insert a new post into the Post table."""
        conn = PostService.get_connection_instance()
        insert_query = """
        INSERT INTO Post (PostID, Description, imagePath, AuthorityName)
        VALUES (?, ?, ?, ?);
        """
        try:
            cursor = conn.cursor()
            cursor.execute(insert_query, (post.post_id, post.description, post.image_path, post.authority_name))
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
    def update_entry(post_id: str, new_description: Optional[str] = None, new_image_path: Optional[str] = None, new_authority_name: Optional[str] = None) -> int:
        """Update fields of an existing post by post_id."""
        conn = PostService.get_connection_instance()
        update_fields = []
        params = []

        if new_description:
            update_fields.append("Description = ?")
            params.append(new_description)
        if new_image_path:
            update_fields.append("imagePath = ?")
            params.append(new_image_path)
        if new_authority_name:
            update_fields.append("AuthorityName = ?")
            params.append(new_authority_name)

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
            description=result[1],
            image_path=result[2],
            authority_name=result[3]
        )
