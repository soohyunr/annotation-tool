const Annotation = {
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
          'Highly Disputable',
          'Disputable',
          'Weakly Disputable',
          'Not Disputable',
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
      attribute5: {
        order: 5,
        title: '5. Acceptance of the sentence as true',
        attribute_key: 'Acceptance_of_the_sentence_as_true',
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
        attribute_key: 'Polarity',
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
  is_empty_basket: function (basket) {
    for (let key in basket) {
      if (!basket[key].value) {
        return true;
      }
    }
    return false;
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

const API = {
  get_doc: function (callback) {
    const doc_id = $('#doc_id').val();
    $.get({
      url: '/api/doc/' + doc_id,
    }).done(function (data) {
      callback(JSON.parse(data));
    })
  },
  get_doc_by_local: function (prefix, callback) {
    let doc_id = $('#doc_id').val();
    let doc = localStorage.getItem(prefix + doc_id);
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
  get_review_annotation: function (callback) {
    const doc_id = $('#doc_id').val();
    const annotator_id = $('#annotator_id').val();
    $.get({
      url: '/api/review/' + annotator_id + '/doc/' + doc_id + '/annotation',
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

const Event = {
  state: {
    view_mode: 'paragraph',
    target_sent: {
      index: 0,
      min: 0,
      max: 0,
    },
  },
  selection_listen: function () {
    document.onmouseup = document.onkeyup = function () {
      const selection = window.getSelection();
      if (selection.type !== 'Range') return;

      const anchorNodeParent = selection.anchorNode.parentElement;
      const focusNodeParent = selection.focusNode.parentElement;

      if (anchorNodeParent.className !== 'type-event' && anchorNodeParent.className !== 'type-sentence') return;
      if (anchorNodeParent.className !== focusNodeParent.className) return;
      if (anchorNodeParent.getAttribute('data-index') !== focusNodeParent.getAttribute('data-index')) return;

      const index = Number(anchorNodeParent.getAttribute('data-index'));
      const entire_text = anchorNodeParent.innerText;
      const common_offset = entire_text.indexOf(selection.anchorNode.data);
      let anchor_offset = selection.anchorOffset + common_offset;
      let focus_offset = selection.focusOffset + common_offset;

      const selection_text = selection.toString();

      for (let i = 0; i < selection_text.length; i++) {
        // To detect &nbsp;(&nbsp;'s chartCode is 160 and space chartCode is 32).
        if (selection_text.charCodeAt(i) === 160 || selection_text[i] === ' ') anchor_offset++;
        else break;
      }
      for (let i = selection_text.length - 1; i >= 0; i--) {
        if (selection_text.charCodeAt(i) === 160 || selection_text[i] === ' ') focus_offset--;
        else break;
      }
      if (anchor_offset >= focus_offset) return;
      if (anchor_offset < 0 || anchor_offset > entire_text.length) return;
      if (focus_offset < 0 || focus_offset > entire_text.length) return;

      let type = 'event';
      if (anchorNodeParent.className === 'type-sentence') type = 'sentence';
      const item = {
        target_text: entire_text.substr(anchor_offset, focus_offset - anchor_offset),
        index: index,
        anchor_offset: anchor_offset,
        focus_offset: focus_offset,
        type: type,
        basket: {},
      };

      const range = selection.getRangeAt(0);
      const bound = range.getBoundingClientRect();
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      Modal.set_position(bound.left, bound.top + scrollTop);

      let attributes = Annotation.attributes[type];
      for (let key in attributes) {
        let options = attributes[key].options;
        let attribute_key = attributes[key].attribute_key;
        let initial_value = options[Annotation.random(options.length)];
        initial_value = initial_value.split(' ').join('_');
        item.basket[attribute_key] = {
          initial_value: initial_value,
          value: '',
          memo: '',
          reason: '',
        }
      }

      API.post_annotation(item, function (data) {
        const annotation_item = data['annotation'];
        Annotation.add(annotation_item);
        Renderer.render_table();

        Modal.set_annotation_item(annotation_item);

        if (annotation_item.type === 'sentence') {
          Modal.show();
          Modal.state.step = 0;
          Modal.next_step();
        }
      });

    }.bind(this);
  },
  listen_view_mode: function () {
    $('#view-mode-btn').click(function () {
      if (Event.state.view_mode === 'paragraph') {
        Event.state.view_mode = 'sentence';
        $('#view-mode-btn span').html('paragraph mode');
        $('table').removeClass('table-striped');
        $('.progress').show();
      } else {
        Event.state.view_mode = 'paragraph';
        $('#view-mode-btn span').html('sentence mode');
        $('table').addClass('table-striped');
        $('.progress').hide();
      }
      Renderer.render_table();
    });
  },
  listen_annotation_badge: function () {
    $('.annotation-badge').click(function (e) {
      const annotation_id = $(this).attr('data-id');
      const annotation_item = Annotation.find_by_id(annotation_id);

      Modal.set_position(e.pageX, e.pageY);
      Modal.set_annotation_item(annotation_item);
      Modal.show();
      Modal.state.step = 0;
      Modal.next_step();
    });
  },
  listen_annotation_review_badge: function () {
    $('.annotation-badge').click(function (e) {
      const annotation_id = $(this).attr('data-id');
      const annotation_item = Annotation.find_by_id(annotation_id);

      Modal.set_position(e.pageX, e.pageY);
      Modal.set_annotation_item(annotation_item);
      Modal.show_review();
      Modal.state.step = 0;
      Modal.next_review_step();
    });
  },
  listen_tooltip: function () {
    $('[data-toggle="tooltip"]').tooltip();
    // $('[data-toggle="tooltip"]').tooltip('show');
  },
  listen_key: function () {
    $(document).keydown(function (e) {
      switch (e.which) {
        case 13: // enter
          break;
        case 37: // left
          if (Modal.state.open) break;
          if (Event.state.target_sent.index > Event.state.target_sent.min) {
            Event.state.target_sent.index--;
          }
          $('#sentence-index').html(Event.state.target_sent.index);
          Renderer.render_table();
          e.preventDefault();
          break;
        case 39: // right
          if (Modal.state.open) break;
          if (Event.state.target_sent.index < Event.state.target_sent.max) {
            Event.state.target_sent.index++;
          }
          $('#sentence-index').html(Event.state.target_sent.index);
          Renderer.render_table();
          e.preventDefault();
          break;
        case 38: // up
          break;
        case 40: // down
          break;
        case 49: // 1
          break;
        case 50: // 2
          break;
        case 51: // 3
          break;
        case 52: // 4
          break;
        case 53: // 5
          break;
        default:
          return;
      }
    });
  }
};

const Modal = {
  el: null,
  state: {
    step: 1,
    open: false,
    annotation_item: {},
    max_attribute: 11,
  },
  init: function () {
    this.el = $('#modal');
    this.el.modal({
      show: false,
    });
    this.el.draggable({
      handle: '.modal-header',
    });

    this.el.on('hidden.bs.modal', function (e) {
      Modal.state.open = false;
    });
    this.el.on('shown.bs.modal', function (e) {
      Modal.state.open = true;
    });

    $('#modal-delete-btn').click(function () {
      const annotation_id = Modal.state.annotation_item.id;
      API.delete_annotation(Modal.state.annotation_item.id, function () {
        Annotation.remove(annotation_id);
        Renderer.render_table();
        Modal.el.modal('hide');
      });
    });

    $('#modal-save-btn').click(function () {
      Modal.save();
      Modal.el.modal('hide');
    });
  },
  next_step() {
    if (this.state.step === this.state.max_attribute) {
      return;
    }
    const step = this.state.step + 1;

    setTimeout(function () {
      $('#attribute' + step + '-val').click();
      setTimeout(function () {
        $('#attribute' + step + ' .active').focus();
      }, 100);
    }, 200);

    $('.input-group-text').removeClass('text-primary');
    $('#attribute' + step).parents('.input-group').find('.input-group-text').addClass('text-primary');
    $('.dropdown-toggle').removeClass('text-primary');
    $('#attribute' + step + '-val').addClass('text-primary');
  },
  next_review_step() {
    if (this.state.step === this.state.max_attribute) {
      return;
    }
    const step = this.state.step + 1;

    setTimeout(function () {
      $('#attribute' + step + '-review-val').click();
      setTimeout(function () {
        $('#attribute' + step + '-review .active').focus();
      }, 100);
    }, 200);

    $('.input-group-text').removeClass('text-primary');
    $('#attribute' + step + '-review').parents('.input-group').find('.input-group-text').addClass('text-primary');
    $('.dropdown-toggle').removeClass('text-primary');
    $('#attribute' + step + '-review-val').addClass('text-primary');
  },
  set_annotation_item: function (annotation_item) {
    this.state.annotation_item = annotation_item;
  },
  load_attributes: function () {
    const annotation_type = this.state.annotation_item.type;
    const basket = this.state.annotation_item.basket;
    for (let i = 1; i <= this.state.max_attribute; i++) {
      const attribute_id = 'attribute' + i;

      const attribute_key = Annotation.attributes[annotation_type][attribute_id].attribute_key;
      let value = basket[attribute_key].value;
      if (!value) value = basket[attribute_key].initial_value;

      $('#' + attribute_id + '-memo').val(basket[attribute_key].memo);
      $('#' + attribute_id + '-reason').val(basket[attribute_key].reason);

      $('#' + attribute_id + '-val').html(value.split('_').join(' '));

      $('#' + attribute_id + ' .dropdown-item').removeClass('active');
      $('#' + attribute_id + ' .dropdown-item[data-value="' + value + '"]').addClass('active');
    }
  },
  load_review_attributes: function () {
    const annotation_type = this.state.annotation_item.type;
    const basket = this.state.annotation_item.basket;
    for (let i = 1; i <= this.state.max_attribute; i++) {
      const attribute_id = 'attribute' + i;

      const attribute_key = Annotation.attributes[annotation_type][attribute_id].attribute_key;
      let value = basket[attribute_key].value;
      if (!value) value = basket[attribute_key].initial_value;

      let memo_reason = basket[attribute_key].memo;
      if (memo_reason) {
        memo_reason = 'Memo: '+ memo_reason + ', Reason: ' + basket[attribute_key].reason;
      }
      else memo_reason += 'Reason: ' + basket[attribute_key].reason;

      $('#' + attribute_id).html(value.split('_').join(' ')).attr('title', memo_reason);

      $('#' + attribute_id + '-review-val').html(value.split('_').join(' '));
      $('#' + attribute_id + '-review .dropdown-item').removeClass('active');
      $('#' + attribute_id + '-review .dropdown-item[data-value="' + value + '"]').addClass('active');
    }
    $('.memo-reason-tooltip').tooltip('update');
  },
  show: function () {
    this.set_header();
    this.el.modal('show');

    const annotation_type = this.state.annotation_item.type;
    this.change_type(annotation_type);
    this.render_input(annotation_type);
    this.load_attributes();
  },
  show_review: function () {
    this.set_review_header();
    this.el.modal('show');

    const annotation_type = this.state.annotation_item.type;
    this.change_type(annotation_type);
    this.render_review_input(annotation_type);
    this.load_review_attributes();
  },
  render_input: function (type) {
    $('#col1').html('');
    $('#col2').html('');

    let attributes = Annotation.attributes[type];
    for (let key in attributes) {
      let title = attributes[key].title;
      let options = attributes[key].options;
      let order = attributes[key].order;

      let input_group_template = $('#attribute-input-group-template').html();

      input_group_template = input_group_template.split('<%attribute%>').join(key);
      input_group_template = input_group_template.split('<%title%>').join(title);

      if (order <= 6) {
        $('#col1').append(input_group_template);
      } else {
        $('#col2').append(input_group_template);
      }

      for (let i = 0; i < options.length; i++) {
        let option = options[i];
        let button_template = $('#attribute-button-template').html();
        button_template = button_template.replace('<%value%>', option.split(' ').join('_'));
        button_template = button_template.replace('<%value_space%>', option);

        $('#' + key + ' .dropdown-menu').append(button_template);
      }
    }
    this.input_listen();
  },
  render_review_input: function (type) {
    $('#col1').html('');
    $('#col2').html('');

    let attributes = Annotation.attributes[type];
    for (let key in attributes) {
      let title = attributes[key].title;
      let options = attributes[key].options;
      let order = attributes[key].order;

      let input_group_template = $('#attribute-review-input-group-template').html();

      input_group_template = input_group_template.split('<%attribute%>').join(key);
      input_group_template = input_group_template.split('<%title%>').join(title);

      if (order <= 6) {
        $('#col1').append(input_group_template);
      } else {
        $('#col2').append(input_group_template);
      }

      for (let i = 0; i < options.length; i++) {
        let option = options[i];
        let button_template = $('#attribute-button-template').html();
        button_template = button_template.replace('<%value%>', option.split(' ').join('_'));
        button_template = button_template.replace('<%value_space%>', option);

        $('#' + key + '-review .dropdown-menu').append(button_template);
      }
    }
    this.input_review_listen();
  },
  set_header: function () {
    const type = this.state.annotation_item.type;
    let title = 'Event: ' + this.state.annotation_item.target_text;
    if (type === 'sentence') {
      title = 'Sentence ' + this.state.annotation_item.index;
    }
    this.el.find('.modal-title').html(title);
  },
  set_review_header: function () {
    const type = this.state.annotation_item.type;
    let title = 'Event: ' + this.state.annotation_item.target_text;
    if (type === 'sentence') {
      title = 'Sentence ' + this.state.annotation_item.index;
    }
    this.el.find('.modal-title').html(title + ' Review');
  },
  set_position: function (left, top) {
    const window_width = document.body.clientWidth;

    const margin = 20;
    let calibrated_left = Math.max(margin, left - 450);
    calibrated_left = Math.min(calibrated_left, window_width - 850 - margin);
    this.el.css('left', calibrated_left);
    this.el.css('top', top + 50);
  },
  save: function () {
    const annotation_type = this.state.annotation_item.type;
    for (let i = 1; i <= this.state.max_attribute; i++) {
      const attribute_id = 'attribute' + i;
      const value = $('#' + attribute_id + '-val').html().trim().split(' ').join('_');
      const attribute_key = Annotation.attributes[annotation_type][attribute_id].attribute_key;
      this.state.annotation_item.basket[attribute_key].value = value;

      const memo = $('#' + attribute_id + '-memo').val();
      const reason = $('#' + attribute_id + '-reason').val();

      this.state.annotation_item.basket[attribute_key].memo = memo;
      this.state.annotation_item.basket[attribute_key].reason = reason;
    }

    API.put_annotation(this.state.annotation_item, function () {
      Annotation.update(Modal.state.annotation_item.id, Modal.state.annotation_item);
      Renderer.render_table();
    });
  },
  save_review: function () {
    const annotation_type = this.state.annotation_item.type;
    for (let i = 1; i <= this.state.max_attribute; i++) {
      const attribute_id = 'attribute' + i;
      const value = $('#' + attribute_id + '-val').html().trim().split(' ').join('_');
      const attribute_key = Annotation.attributes[annotation_type][attribute_id].attribute_key;
      this.state.annotation_item.basket[attribute_key].value = value;

      const memo = $('#' + attribute_id + '-memo').val();
      const reason = $('#' + attribute_id + '-reason').val();

      this.state.annotation_item.basket[attribute_key].memo = memo;
      this.state.annotation_item.basket[attribute_key].reason = reason;
    }

    API.put_annotation(this.state.annotation_item, function () {
      Annotation.update(Modal.state.annotation_item.id, Modal.state.annotation_item);
      Renderer.render_table();
    });
  },
  change_type: function (type) {
    let width = '850px';
    if (type === 'event') {
      $('#col1').removeClass('col-md-12').addClass('col-md-6');
      $('#col2').show();
      this.state.max_attribute = 11;
      for (let i = 6; i <= 11; i++) {
        $('#attribute' + i).parents('.input-group').show();
      }
    } else {
      $('#col1').removeClass('col-md-6').addClass('col-md-12');
      $('#col2').hide();
      this.state.max_attribute = 5;
      for (let i = 6; i <= 11; i++) {
        $('#attribute' + i).parents('.input-group').hide();
      }
      width = '950px';
    }
    $('#modal').css('width', width).css('max-width', width);
    $('#modal .modal-content').css('width', width).css('min-width', width);
  },
  input_listen: function () {
    $('.dropdown-item').click(function () {
      const dropdown = $(this).parents('.dropdown');
      const attribute_id = dropdown.attr('id');
      const dropdown_toggle = dropdown.find('.dropdown-toggle');
      const value = $(this).attr('data-value');

      dropdown.find('.dropdown-toggle').html(value.split('_').join(' '));

      $('#' + attribute_id + ' .dropdown-item').removeClass('active');
      $('#' + attribute_id + ' .dropdown-item[data-value="' + value + '"]').addClass('active');

      Modal.state.step = Number(dropdown_toggle.attr('id').replace('attribute', '').replace('-val', ''));
      Modal.next_step();
    });
  },
  input_review_listen: function () {
    $('.dropdown-item').click(function () {
      const dropdown = $(this).parents('.dropdown');
      const attribute_id = dropdown.attr('id');
      const dropdown_toggle = dropdown.find('.dropdown-toggle');
      const value = $(this).attr('data-value');

      dropdown.find('.dropdown-toggle').html(value.split('_').join(' '));

      $('#' + attribute_id + '-review .dropdown-item').removeClass('active');
      $('#' + attribute_id + '-review .dropdown-item[data-value="' + value + '"]').addClass('active');

      Modal.state.step = Number(dropdown_toggle.attr('id').replace('attribute', '').replace('-review-val', ''));
      Modal.next_review_step();
    });
  },
};

const Renderer = {
  state: {
    sents: [],
    mode: 'annotation', // annotation, review,
  },
  set_mode: function (mode) {
    this.state.mode = mode;
  },
  load_annotation_and_render_table: function () {
    API.get_annotation(function (data) {
      Annotation.data = data['annotations'];
      Renderer.render_table();
    });
  },
  render_table: function () {
    const sents = this.state.sents;

    const tbody = $('#tbody');
    tbody.html('');

    // make annotation map
    const annotation_map = {};
    for (let i = 0; i < sents.length; i++) {
      annotation_map[sents[i].index] = [];
    }
    for (let i = 0; i < Annotation.data.length; i++) {
      const item = Annotation.data[i];
      annotation_map[item.index].push(item);
    }

    for (let i = 0; i < sents.length; i++) {
      const sent = sents[i];
      let tr = $('#tr-template').html();

      const index = sent['index'];
      const text = sent['text'];

      const annotations = annotation_map[Number(index)];

      tr = tr.split('<%index%>').join(sent['index']);
      tr = tr.replace('<%text%>', this.render_markup_sentence(Number(index), text, annotations));

      let sent_col = 'Sent' + index;
      let sent_markup = '';
      let sentence_type_index = -1;
      for (let j = 0; j < annotations.length; j++) {
        if (annotations[j].type === 'sentence') {
          sentence_type_index = j;
          break;
        }
      }
      if (sentence_type_index !== -1) {
        const annotation_item = annotations[sentence_type_index];
        let badge_type = 'primary';
        if (Annotation.is_empty_basket(annotation_item.basket)) {
          badge_type = 'secondary';
        }
        sent_markup += '<span class="badge badge-' + badge_type + ' annotation-badge" data-id="' + annotation_item.id + '" ';
        sent_markup += 'data-toggle="tooltip" data-placement="right" data-html="true" title="' + this.render_tooltip_markup(annotation_item) + '">';
        sent_markup += sent_col + '</span>';
        tr = tr.replace('<%sent%>', sent_markup);
      } else {
        tr = tr.replace('<%sent%>', sent_col);
      }

      tbody.append(tr);
    }

    if (Event.state.view_mode === 'sentence') {
      $('.tr-sentence').hide();
      $('#tr-' + Event.state.target_sent.index).show();

      const target_sent = Event.state.target_sent;
      let ratio = (target_sent.index - target_sent.min + 1) / (target_sent.max - target_sent.min + 1) * 100;
      $('.progress-bar').css('width', ratio + '%');
    }

    if (this.state.mode === 'review') {
      Event.listen_annotation_review_badge();
    } else {
      Event.listen_annotation_badge();
    }

    Event.listen_tooltip();
  },
  render_markup_sentence: function (index, text, annotations) {
    const start = {}, end = {};
    for (let i = 0; i < annotations.length; i++) {
      const item = annotations[i];
      if (item.type !== 'event') continue;
      if (item.index !== index) continue;
      start[item.anchor_offset] = i;
      end[item.focus_offset] = i;
    }
    let markup = '';

    for (let i = 0; i < text.length; i++) {
      if (i in start) {
        const annotation_item = annotations[start[i]];
        let badge_type = 'success';
        if (Annotation.is_empty_basket(annotation_item.basket)) {
          badge_type = 'secondary';
        }

        markup += '<span class="badge badge-' + badge_type + ' annotation-badge" data-id="' + annotation_item.id + '" ';
        markup += 'data-toggle="tooltip" data-placement="right" data-html="true" title="' + this.render_tooltip_markup(annotation_item) + '">';
      }

      if (text[i] !== ' ') {
        markup += text[i];
      } else {
        markup += '&nbsp;';
      }

      if (i + 1 in end) {
        markup += '</span>';
      }
    }
    return markup;
  },
  render_tooltip_markup: function (annotation_item) {
    let markup = '';
    const annotation_type = annotation_item['type'];
    for (let key in Annotation.attributes[annotation_type]) {
      const attribute_key = Annotation.attributes[annotation_type][key].attribute_key;
      const order = Annotation.attributes[annotation_type][key].order;
      if (attribute_key in annotation_item.basket && annotation_item.basket[attribute_key].value) {
        markup += order + '. ' + attribute_key + ': <em>' + annotation_item.basket[attribute_key].value + '</em><br/>'
      }
    }
    return markup;
  },
};

const TextReader = {
  data_text: '',
  data_json: {},
  listen: function () {
    let input = document.getElementById("doc-uploader");
    input.addEventListener("change", function () {
      if (this.files && this.files[0]) {
        let myFile = this.files[0];
        let reader = new FileReader();
        reader.addEventListener('load', function (e) {
          TextReader.data_text = e.target.result;
          TextReader.data_text = TextReader.decode_string(TextReader.data_text, $('#ENCRYPTION_KEY').val());
          TextReader.data_json = JSON.parse(TextReader.data_text);
          let doc_id = $('#doc_id').val();

          if (doc_id === TextReader.data_json['doc_id']) {
            localStorage.setItem(TextReader.data_json['doc_id'], TextReader.data_text);
            location.reload();
          } else {
            swal({
              title: '',
              text: 'The document number does not match.',
              type: 'error',
            });
          }
          console.log(TextReader.data_json);
        });
        reader.readAsBinaryString(myFile);
      }
    });
  },
  decode_string: function (input, key) {
    input = input.split(',');
    let c = '';
    while (key.length < input.length) {
      key += key;
    }
    for (let i = 0; i < input.length; i++) {
      let value1 = input[i];
      let value2 = key[i].charCodeAt(0);

      let xor = value1 ^ value2;
      c += String.fromCharCode(xor);
    }
    return c;
  }
};
