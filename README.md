# CITS3403 Group Project

## Quick start

1. Ensure you have Python 3.10 or later installed.
2. Install dependencies
```console
pip install -r requirements.txt
```

3. Set a secret key
- bash/zsh
```console
export FLASK_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex())')
```
- PowerShell
```powershell
$env:FLASK_SECRET_KEY = $(python -c 'import secrets; print(secrets.token_hex())')
```

4. Setup the database
```console
flask db upgrade
```
5. Run the app
```console
python -m app
```

## Test data

After first-time setup (see above):

```console
$ python -m app.test_data.whatevertest
```

Where `whatevertest` is replaced with the name of the test file (minus `.py`) in the `/app/test_data` folder, e.g. `messages`.

# Key Features:
## Artist Pages:
Artists can post "ads" displaying the sort of work they can do, including an artist gallery displaying their previous work.
## DM system: 
Potential buyers can DM artists, either through their profile or an ad and request to get work done.
## Homepage: 
A homepage where the ads of artists can be displayed, with the option to filter out categories.
