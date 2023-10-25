call .venv\Scripts\activate
uvicorn src.main:app --reload --log-config=src/log_conf.yaml
