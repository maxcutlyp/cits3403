# CITS3403 Group Project

## Quick start

```console
$ pip install -r requirements.txt
$ export FLASK_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex())')
$ flask db upgrade # setup database
$ python -m app
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
