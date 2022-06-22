cd %~dp0
CALL venv\Scripts\activate
python -m pip install -r requirements.txt
python watcher.py