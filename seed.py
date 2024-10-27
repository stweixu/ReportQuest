# purpose of this file is to seed the database with dummy data
# basically to run all the fules in the database_seeder folder

import os


base_path = "database_seeder"

for i in os.listdir(base_path):
    command = f"python {base_path}/{i}"
    print(f"executing {command}")
    os.system(command)
