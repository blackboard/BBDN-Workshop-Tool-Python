# BBDN-Workshop-Tool-Python

## HOW TO

### Install

```
python -m venv <path to project>/BBDN-Workshop-Tool-Python/venv

pip install -r requirements.txt
```

### Setup
```
source venv/bin/activate

export PYTHONPATH='<path to project>/BBDN-Workshop-Tool-Python/app'
```

Build keys
```bash
python keys/build_config.py
```

### Configuration
Edit the `lti.json` file in the root folder to configure your Client ID, devportal, and Deployment ID.

### Run

```
python app.py
```

### Configuration

If you want to modify your configuration it's best to create a `.env` file. These are the possible values you can change:

```
PORT='5000'
DOMAIN='localhost'
FRONTEND_URL='http://localhost:3000'
Collapse
```














