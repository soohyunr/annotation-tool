# annotation-tool

This repository provides a web server, can be used as a text annotation tool.

The program distributes texts that may show a copyright issue when distributing the original text type, to several annotators without copyright issues.

## Major dependencies

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

## Run service

```bash
sudo python3 app.py
```

## Add new annotation

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
        title: '1. Local Acceptability',
        attribute_key: 'Local_Acceptability',
        options: [
          'Strong Accept',
          'Accept',
          'Weak Accept',
          'Hard to judge',
          'Weak Reject',
          'Reject',
          'Strong Reject',
        ]
      },
      attribute2: {
        order: 2,
        title: '2. Verifiability',
        attribute_key: 'Verifiability',
        options: [
          'I can verify it using my knowledge.',
          'I can verify it by short-time googling.',
          'I can verify it by long-time googling.',
          'I might find an off-line way to verify it, but it will be very hard.',
          'There is no way to verify it.',
          'None of the above',
        ]
      },
      '...'
    },
    event: {
      attribute1: {
        order: 1,
        title: '1. Knowledge Awareness',
        attribute_key: 'Knowledge_Awareness',
        options:  [
          'I did not know the information.',
          'I already knew the information before I read this document.',
          'I did not know the information before, but came to know it by reading the previous sentences.',
        ],
      },
      '...'
    }
  },
  data: [],
  /* functions... */
}
```

In the attribute `attributes`, there are two kinds of members: `sentence`, and `event`.
Each member in the `sentence` allows user to choose an annotation. For example, in the script above takes an annotation for the category 'Local Acceptability', which has 7 options.

## Deploy

```bash
pip install fabric3
fab deploy
```

## Citation

Please cite our PACLIC 2019 paper:
```bibtex
@inproceedings{yang-2019-local-acceptability,
    title = "A Corpus of Sentence-level Annotations of Local Acceptability with Reasons",
    author = "Yang, Wonsuk and Kim, Jung-Ho and Yoon, Seungwon and Park, Chaehun Park, Jong C.",
    booktitle = "Proceedings of the 33nd Pacific Asia Conference on Language, Information and Computation",
    year = "2019",
    publisher = "Association for Computational Linguistics"
}
```
