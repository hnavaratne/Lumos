# Lumos

#### Prerequisites
* [`Python 3.5 or above`](https://www.python.org/downloads/)

#### Setting up:
Once your environment is set up, you need to install the following Python dependencies required by the add-on.
*	flask
*	textacy(http://github.com/chartbeat-labs/textacy.git)
*	textblob
*	flask-restful
*	bs4
*	spacy
*	http://github.com/explosion/spacy-models/releases/download/en_core_web_md-2.0.0/en_core_web_md-2.0.0.tar.gz
*	http://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.0.0/en_core_web_sm-2.0.0.tar.gz

Use the following command to install the dependencies above:
```python
python -m pip install <dependency_name>
```
Once all the dependencies have been installed, use following commands to install required corpora:
```python
python -m textblob.download_corpora
```
```python
python -m spacy download en
```

# Start Lumos: 
```python
python RQmeasurement.py
```
