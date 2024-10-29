# Guide to the SC2006 Project Backend

## Setup on WINDOWS WSL

0. Retrieve config.py from the anyone else who has it

```
just ask maxwell first, he'll give it to you
```

1. Install Python 3.11

```
sudo apt update && upgrade
sudo apt install python3 python3-pip
```

2. clone the repo

```
git clone git@github.com:maxwellau2/ReportQuestBackend.git
cd ReportQuestBackend
```

3. Instantiate the virtual environment

```
python3 -m venv venv
```

4. Activate the virtual environment

```
source venv/bin/activate
```

5. Install dependencies as stated in requirements.txt

```
pip install -r "requirements.txt"
```

6. Run the migrations to create the databases

```
make migrate-up
```

7. Run the main.py, ensure you are in root directory

```
# activate the GPU if applicable
make enable-ollama-gpu
# run the main.py
make run-reloadable
```

8. To test the application, open http://0.0.0.0:8000/docs in your browser and test endpoints

## Setup on MACOS

1. Hey man tbh, i havent touched macOS in a while
