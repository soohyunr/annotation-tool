# annotation-tool

This repository provides a web server, can be used as a text annotation tool.
The program distributes texts that may show a copyright issue when distributing the original text type, to several annotators without copyright issues.

## Major Dependencies

- Flask
- flask-mongoengine
- pymongo
- Werkzeug

## Dependencies for machine learning & data analysis

- numpy
- scipy
- pandas
- Pillow
- scikit-learn
- allennlp

## Prerequisites

```bash
pip3 install -r requirements.txt

# Modify the settings in config.sample.py
vi config.sample.py
mv config.smaple.py config.py
```

## Run Service

```bash
sudo python3 app.py
```

## Add New Annotation

1. Make new attributes file in `static/js/` folder.
2. Include the file at `templates/doc.html` file.

## Annotation documentation

`Still working`

## Deploy

```bash
pip install fabric3
fab deploy
```

## Contributor

- [Seungwon](http://nlp.kaist.ac.kr/~swyoon)
- [Junseop](https://github.com/gaonnr)
