@echo off
cd ..
pip install pip-tools
python -m piptools compile pyproject.toml -o requirements.txt
pip install -r requirements.txt
del requirements.txt
pause