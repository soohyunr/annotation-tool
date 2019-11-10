# annotation-tool

This repository provides a web server, can be used as a text annotation tool.

Annotators can upload a document to the server, then the server automatically split the document into sentences. The annotators can annotate the attributes, and at the same time they can leave notes for each selection. The annotators can use keystrokes to navigate through different sentences. Users can export the annotation results as a JSON file.

<img src="https://github.com/nlpcl-lab/annotation-tool/blob/master/static/img/screenshot.png">


## JSON Export Format

```javascript
{
        "sentence_index": 0, 
        "title": "example_document.txt", 
        "annotation_anchor_offset": 0, 
        "created_at": {
            "$date": 1540481324137
        }, 
        "sentence": "This is an example sentence to annotate.", 
        "annotator": "koala", 
        "source": "n/a", 
        "annotation_focus_offset": 5, 
        "annotation_type": "sentence", 
        "attributes": {
            "Knowledge_Awareness": {
                "reason": "the reason for the unawareness of the annotator can be written here.", 
                "memo": "", 
                "value": "I_did_not_know_the_information.", 
                "initial_value": "I_did_not_know_the_information_before,_but_came_to_know_it_by_reading_the_previous_sentences."
            }, 
            '...'
        }, 
        "annotation_target_text": "Sent0", 
        "doc_id": 1
    },
    ...
```

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
        title: '1. Knowledge Awareness',
        attribute_key: 'Knowledge_Awareness',
        options:  [
          'I did not know the information.',
          'I already knew the information before I read this document.',
          'I did not know the information before, but came to know it by reading the previous sentences.',
        ],
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
    }
  },
  data: [],
  /* functions... */
}
```

In the attribute `attributes`, there are two kinds of members: `sentence`, and `event`.
Each member in the `sentence` allows user to choose an annotation. For example, in the script above takes an annotation for the category 'Local Acceptability', which has 7 options.

## Citation
When you use this tool, please cite the paper:

```bibtex
@inproceedings{yang-2019-local-acceptability,
    title = "A Corpus of Sentence-level Annotations of Local Acceptability with Reasons",
    author = "Yang, Wonsuk and Kim, Jung-Ho and Yoon, Seungwon and Park, Chaehun Park, Jong C.",
    booktitle = "Proceedings of the 33nd Pacific Asia Conference on Language, Information and Computation",
    year = "2019",
    publisher = "Association for Computational Linguistics"
}
```
