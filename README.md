# Guide to the SC2006 Project Backend

## Setup on WINDOWS WSL

1. Install Python 3.11

```
sudo apt update && upgrade
sudo apt install python3 python3-pip
```

2. Instantiate the virtual environment

```
python3 -m venv venv
```

3. Activate the virtual environment

```
source venv/bin/activate
```

4. Install dependencies as stated in requirements.txt

```
pip install -r "requirements.txt"
```

5. Run the migrations to create the databases

```
make migrate-up
```

6. Run the main.py, ensure you are in root directory

```
make run
```

7. To test the application, open http://0.0.0.0:8000/docs in your browser and test endpoints

## Setup on MACOS

1. Hey man tbh, i havent touched macOS in a while
