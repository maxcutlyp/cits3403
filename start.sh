pip install -r requirements.txt
export FLASK_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex())')
flask db upgrade
flask run
