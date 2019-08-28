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

> TODO: Make it easier to add new annotations.

Here is the structure(and the example) of the Annotation class(~`attributes_v2.js`):

```javascript
const Annotation = {
  attributes: {
    sentence: {
      attribute1: {
        order: 1,
        title: '1. Persuasiveness Score',
        attribute_key: 'Persuasiveness_Score',
        options: [
          'A very strong, clear argument.',
          'A strong, pretty clear argument.',
          'A decent, fairly clear argument.',
          'A poor, understandable argument.',
          'It is unclear what the author is trying to argue.',
          'The author does not appear to make any argument.'
        ]
      },
      attribute2: {
        order: 2,
        title: '2. Evidence Score',
        attribute_key: 'Evidence_Score',
        options: [
          '...'
        ]
      },
      '...'
    },
    event: {
      attribute1: {
        order: 1,
        title: '1. Knowledge Awareness',
        attribute_key: 'Knowledge_Awareness',
        options: ['I already know.', 'I did not know.']
      },
      attribute2: {
        order: 2,
        title: '2. Credibility',
        attribute_key: 'Credibility',
        options: [
          '...'
        ]
      },
      '...'
    }
  },
  data: [],
  /* functions... */
}
```

In the attribute `attributes`, there are two kinds of members: `sentence`, and `event`.
Each member in the `sentence` allows user to choose an annotation. For example, in the script above takes an annotation for the category 'Persuasiveness Score', which has five options(scores).

## Deploy

```bash
pip install fabric3
fab deploy
```

## Contributors

- [Seungwon](http://nlp.kaist.ac.kr/~swyoon)
- [Junseop](https://github.com/gaonnr)
