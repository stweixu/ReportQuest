from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash

# Create a PasswordHasher instance
ph = PasswordHasher()

# The Argon2id hash you're trying to verify
stored_hash = "$argon2id$v=19$m=65536,t=3,p=4$haDXYnYOJBWqfjW7BKvwOA$REcoN5pQmYi1ADrfTgbkAsctnaFVgvqmuDfB3/kJf80"
password = "aij1"

# Attempt to verify the hash
try:
    ph.verify(stored_hash, password)
    print("Password is correct!")
except InvalidHash:
    print("The provided hash is invalid.")
except Exception as e:
    print(f"An error occurred: {e}")
