const annotation = {
  attributes: {
    sentence: {
      attribute1: {
        order: 1,
        title: '1. Knowledge Awareness',
        attribute_key: 'Knowledge_Awareness',
        options: [
          'I did not know the information.',
          'I already knew the information before I read this document.',
          'I did not know the information before, but came to know it by reading the previous sentences.',
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
      attribute3: {
        order: 3,
        title: '3. Disputability of the sentence',
        attribute_key: 'Disputability_of_the_sentence',
        options: [
          'I can verify it using my knowledge.',
          'I can verify it by short-time googling.',
          'I can verify it by long-time googling.',
          'I might find an off-line way to verify it, but it will be very hard.',
          'There is no way to verify it.',
          'None of the above',
        ]
      },
      attribute4: {
        order: 4,
        title: '4. Perceived Author Credibility for the upcoming sentences',
        attribute_key: 'Perceived_Author_Credibility_for_the_upcoming_sentences',
        options: [
          'Strong Credibility for the upcoming sentences',
          'Credibility for the upcoming sentences',
          'Weak Credibility for the upcoming sentences',
          'Hard to Judge',
          'Weak Suspicion for the upcoming sentencese',
          'Suspicion for the upcoming sentences',
          'Strong Suspicion for the upcoming sentences',
        ]
      },
    },
    event: {
      attribute1: {
        order: 1,
        title: '1. Knowledge Awareness',
        attribute_key: 'Knowledge_Awareness',
        options: [
          'I already know.',
          'I did not know.',
        ]
      },
      attribute2: {
        order: 2,
        title: '2. Credibility',
        attribute_key: 'Credibility',
        options: [
          'false',
          'feel like false',
          'hard to judge',
          'feel like true',
          'true',
          'none',
        ]
      },
      attribute3: {
        order: 3,
        title: '3. Verifiability',
        attribute_key: 'Verifiability',
        options: [
          'verify it with my knowledge',
          'verify it by short time googling',
          'verify it by long time googling',
          'hard to verify it',
          'no way to verify it',
          'none',
        ]
      },
      attribute4: {
        order: 4,
        title: '4. Conditionality',
        attribute_key: 'Conditionality',
        options: [
          'sufficient condition',
          'necessary condition',
          'none',
        ]
      },
      attribute5: {
        order: 5,
        title: '5. Polarity',
        attribute_key: 'Conditionality',
        options: [
          'negative',
          'positive',
        ]
      },
      attribute6: {
        order: 6,
        title: '6. Tense',
        attribute_key: 'Tense',
        options: [
          'past',
          'present',
          'future',
          'unspecified',
        ]
      },
      attribute7: {
        order: 7,
        title: '7. Genericity',
        attribute_key: 'Genericity',
        options: [
          'specific',
          'generic',
        ]
      },
      attribute8: {
        order: 8,
        title: '8. Source Type',
        attribute_key: 'Source_Type',
        options: [
          'author',
          'involved',
          'named third party',
          'unnamed third party',
        ]
      },
      attribute9: {
        order: 9,
        title: '9. Subjectivity',
        attribute_key: 'Subjectivity',
        options: [
          'positive',
          'negative',
          'neutral',
          'multi valued',
        ]
      },
      attribute10: {
        order: 10,
        title: '10. Factuality',
        attribute_key: 'Factuality',
        options: [
          'asserted',
          'speculated',
          'none',
        ]
      },
      attribute11: {
        order: 11,
        title: '11. Prominence',
        attribute_key: 'Prominence',
        options: [
          'new',
          'prominent',
          'presupposed',
        ]
      },
    },
  },
  // attributes: [
  //   ['attribute1', 'knowledge_awareness'],
  //   ['attribute2', 'credibility'],
  //   ['attribute3', 'verifiability'],
  //   ['attribute4', 'conditionality'],
  //   ['attribute5', 'polarity'],
  //   ['attribute6', 'tense'],
  //   ['attribute7', 'genericity'],
  //   ['attribute8', 'source_type'],
  //   ['attribute9', 'subjectivity'],
  //   ['attribute10', 'factuality'],
  //   ['attribute11', 'prominence'],
  // ],
  // attributes_default: {
  //   knowledge_awareness: 'I_did_not_know',
  //   credibility: 'hard_to_judge',
  //   verifiability: 'verify_it_by_short_time_googling',
  //   conditionality: 'none',
  //   polarity: 'positive',
  //   tense: 'present',
  //   genericity: 'specific',
  //   source_type: 'author',
  //   subjectivity: 'neutral',
  //   factuality: 'asserted',
  //   prominence: 'new',
  // },
  data: [
    /**
     * {
     *     type: String, // "event" or "sentence"
     *     index: Integer,
     *     sent: ObjectID,
     *     doc: ObjectID,
     *     user: ObjectID,
     *     anchor_offset: Integer,
     *     focus_offset: Integer,
     *     entire_text: String,
     *     target_text: String,
     *     basket: {
     *         KnowledgeAwareness: "2_I_did_not_know",
     *         Tense: "1_past",
     *     },
     * }
     */
  ],
  find_attribute_name_by_id: function (id) {
    for (let i = 0; i < this.attributes.length; i++) {
      if (this.attributes[i][0] === id) return this.attributes[i][1];
    }
    return '';
  },
  find_by_id: function (annotation_id) {
    for (let i = 0; i < this.data.length; i++) {
      const item = this.data[i];
      if (item.id === annotation_id) {
        return item;
      }
    }
    return null;
  },
  find_event: function (index, anchor_offset, focus_offset) {
    for (let i = 0; i < this.data.length; i++) {
      const item = this.data[i];
      if (item.type === 'event') continue;
      if (item.index !== index) continue;
      if (item.anchor_offset !== anchor_offset) continue;
      if (item.focus_offset !== focus_offset) continue;
      return i;
    }
    return -1;
  },
  add: function (item) {
    if (item.type === 'event' && this.find_event(item.index, item.anchor_offset, item.focus_offset) !== -1) return;
    this.data.push(item);
  },
  update: function (annotation_id, new_item) {
    for (let i = 0; i < this.data.length; i++) {
      const item = this.data[i];
      if (item.id === annotation_id) {
        this.data[i] = new_item;
      }
    }
  },
  remove: function (annotation_id) {
    for (let i = 0; i < this.data.length; i++) {
      const item = this.data[i];
      if (item.id === annotation_id) {
        this.data.splice(i, 1);
        break;
      }
    }
  },
  random: function (range) {
    return Math.floor(Math.random() * range);
  }
};

const api = {
  get_doc: function (callback) {
    const doc_id = $('#doc_id').val();
    $.get({
      url: '/api/doc/' + doc_id,
    }).done(function (data) {
      callback(JSON.parse(data));
    })
  },
  get_doc_by_local: function (callback) {
    let doc_id = $('#doc_id').val();
    let doc = localStorage.getItem(doc_id);
    if (doc) {
      callback(JSON.parse(doc));
    } else {
      callback(null);
    }
  },
  get_annotation: function (callback) {
    const doc_id = $('#doc_id').val();
    $.get({
      url: '/api/doc/' + doc_id + '/annotation',
    }).done(function (data) {
      callback(JSON.parse(data));
    })
  },
  post_annotation: function (item, callback) {
    item.doc = $('#doc_id').val();
    $.ajax({
      url: '/api/annotation',
      contentType: 'application/json',
      type: 'POST',
      data: JSON.stringify(item),
    }).done(function (data) {
      callback(JSON.parse(data));
    }).fail(function (data) {
      console.error(data);
      swal({
        title: '',
        text: 'Failed to save annotation, please check network.',
        type: 'error',
      });
    })
  },
  delete_annotation: function (annotation_id, callback) {
    $.ajax({
      url: '/api/annotation/' + annotation_id,
      type: 'DELETE',
    }).done(function () {
      toastr.success("Deleted");
      callback();
    }).fail(function (data) {
      console.error(data);
      swal({
        title: '',
        text: 'Failed to delete annotation, please check network.',
        type: 'error',
      });
    })
  },
  put_annotation: function (item, callback) {
    $.ajax({
      url: '/api/annotation/' + item.id,
      contentType: 'application/json',
      type: 'PUT',
      data: JSON.stringify(item),
    }).done(function (data) {
      toastr.success("Saved");
      callback(JSON.parse(data));
    }).fail(function (data) {
      console.error(data);
      swal({
        title: '',
        text: 'Failed to update annotation, please check network.',
        type: 'error',
      });
    })
  },
};