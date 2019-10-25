//
// Chatbot helpers
//

function postStateToChatbot(language, county) {
  var chatbotIframe = $('#botDiv iframe');
  if (chatbotIframe.length === 0) {
    console.warn('Could not post message to chatbot. Element does not exist yet.')
    return;
  }

  var message = {
    type: 'state', // the message type
    language: language,
    county: county,
    questionId: $(document.body).attr('class').split(' ').find(function(s) { return s.includes('question'); })
  };

  // None of the data is private, so we don't care about the origin of the iframe.
  chatbotIframe[0].contentWindow.postMessage(message, '*');
}

//
// Gtag event helper
//

function nameSearchNoResultsEvent(params) {
  sendGtagEvent('name-search-no-results', params);
}

function citationIneligibleEvent(params) {
  sendGtagEvent('citation-ineligible', params);
}

function citationNumberReusedEvent(params) {
  sendGtagEvent('citation-number-reused', params);
}

function citationNoResultsEvent(params) {
  sendGtagEvent('citation-number-no-results', params);
}

function languageSelectEvent(language) {
  sendGtagEvent('selected-language-' + language);
}

function languageSelectorClickedEvent() {
  sendGtagEvent('clicked-language-selector');
}

function sendGtagEvent(event, params) {
  if (params)
    gtag('event', event, params);
  else
    gtag('event', event);
}

function sendGtagEventOnClick(selector, event) {
  $(document).ready(function() {
    var element = document.querySelector(selector);
    if (!element) {
      console.warn('Could not find element for selector ' + selector);
      return;
    }

    element.addEventListener('click', function() {
      gtag('event', event);
    });
  });
}

//
// Custom file upload helper
//

var texts = {
  'Use a different photo': {
    'en': 'Use a different photo',
    'es': 'Subir foto diferente'
  },
  'Add a photo': {
    'en': 'Add a photo',
    'es': 'Subir foto'
  },
  'benefit_proof_validation_error': {
    'en': 'Please click the "Add a photo" button or select "I don\'t have proof available".',
    'es': 'Favor de hacer clic en "Subir foto" o seleccionar "No tengo un comprobante en este momento".'
  }
};

function getText(key, lang) {
  var translations = texts[key];
  if (translations) {
    if (lang in translations)
      return translations[lang];
    else {
      console.warn('Could not find translation for ' + key + ' in ' + lang);
      return translations['en'];
    }
  } else {
    console.error('Could not find translation for ' + key);
  }
}

function prepareFileUpload(lang) {
  console.log('Preparing custom file upload in language: ' + lang);
  $('#daform').attr('enctype', 'multipart/form-data');
  $('#daform').attr('method', 'POST');

  var fileInputEl = $('.a2p-file-input');
  var imagePreviewFailed = false;

  var renderAll = function() {
    var state = { files: fileInputEl[0].files, imagePreviewFailed: imagePreviewFailed };
    renderUploadComplete(state);
    renderImagePreview(state);
    renderRemoveButton(state);
    renderUploadButton(state);
  };

  var renderUploadComplete = function(state) {
    if (state.imagePreviewFailed) {
      $('.a2p-upload-complete').css('display', 'flex');
    } else {
      $('.a2p-upload-complete').css('display', 'none');
    }
  };

  var renderImagePreview = function(state) {
    if (state.imagePreviewFailed) {
      $('.a2p-image-preview').css('display', 'none');
      $('.a2p-image-preview').removeAttr('src');
    } else if (state.files.length > 0) {
      $('.a2p-image-preview').css('display', 'block');
      $('.a2p-image-preview').attr('src', URL.createObjectURL(state.files[0]));
    } else {
      $('.a2p-image-preview').css('display', 'none');
      $('.a2p-image-preview').removeAttr('src');
    }
  };

  var renderRemoveButton = function(state) {
    if (state.files.length > 0) {
      $('.a2p-file-remove-button').css('display', 'block');
    } else {
      $('.a2p-file-remove-button').css('display', 'none');
    }
  };

  var renderUploadButton = function(state) {
    if (state.files.length > 0) {
      $('.a2p-file-upload-label').text(getText('Use a different photo', lang));
    } else {
      $('.a2p-file-upload-label').text(getText('Add a photo', lang));
    }
  };

  $('.a2p-file-remove-button').on('click', function() {
    imagePreviewFailed = false;
    // Clear the uploaded files
    fileInputEl[0].value = '';
    renderAll();
  });

  fileInputEl.on('change', function() {
    if (fileInputEl[0].files.length > 0) {
      hideA2PValidationError();
    }
    imagePreviewFailed = false;
    renderAll();
  });

  // If the image preview fails, e.g. because someone
  // uploaded a PDF:
  $('.a2p-image-preview').on('error', function() {
    imagePreviewFailed = true;
    renderAll();
  });

  renderAll();

  prepareCustomValidation({
    formIsValidFn: function() {
      // Extremeley sloppy to register this event listener here, but at least we know the element has been
      // added to the DOM. Ugh.
      $('[aria-checked]').on('click', hideA2PValidationError);

      var hasFiles = $('.a2p-file-input')[0].files.length > 0;
      var checkedNoProof = $('[aria-checked]').attr('aria-checked') === 'true';
      return hasFiles || checkedNoProof;
    },
    errorMessage: getText('benefit_proof_validation_error', lang)
  });
}

//
// Custom form validation
//

function hideA2PValidationError() {
  $('.a2p-validation-error').remove();
}

function showA2PValidationError(message) {
  $('.a2p-validation-error').remove();
  var errorEl = $('<div class="a2p-validation-error">' + message + '</div>');
  $('.da-field-buttons').prepend(errorEl);
}

function prepareCustomValidation(validationOpts) {
  var errorMessage = validationOpts.errorMessage;
  var formIsValidFn = validationOpts.formIsValidFn;
  // wrapped in a setTimeout because daValidator does not exist on page load. Ugh.
  setTimeout(function() {
    // save the current validation rules
    var oldRules = daValidator.settings.rules;

    // destroy existing event listeners
    daValidator.destroy();
    
    // re-initialize with old validation rules + custom handler
    $('#daform').validate({
      rules: oldRules,
      submitHandler: function(form) {
        var formIsValid = formIsValidFn();
        if (formIsValid) {
          daValidationHandler(form);
        } else {
          showA2PValidationError(errorMessage);
        }
      }
    });
  });
}

//
// Language selector
//

function insertLanguageDropdown(active_lang) {
    var language_labels = {
        'en': 'English',
        'es': 'Español',
        'zh-s': '简体中文',
        'zh-t': '繁体中文'
    };
    var headerEl = $('.container.danavcontainer');
    var languageButtonsHTML = '' +
        '<div class="a2p-language-dropdown-container">' +
            '<div class="dropdown a2p-language-dropdown">' +
                '<a href="#" class="a2p-language-dropdown-label nav-link dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">' +
                    '<img class="a2p-language-dropdown-label-icon" src="/packagestatic/docassemble.jcc.abilitytopay/switch-language.png">' +
                    '<span class="a2p-language-dropdown-label-text">' + language_labels[active_lang] + '</span>' +
                '</a>' +
                '<div class="dropdown-menu dropdown-menu-right" aria-labelledby="dropdownMenuButton">' +
                    '<a class="dropdown-item" data-lang="en" href="#">' + language_labels['en'] + '</a>' +
                    '<a class="dropdown-item" data-lang="es" href="#">' + language_labels['es'] + '</a>' +
                    // uncomment below when chinese translations are ready
                    // '<a class="dropdown-item" data-lang="zh-s" href="#">' + language_labels['zh-s'] + '</a>' +
                    // '<a class="dropdown-item" data-lang="zh-t" href="#">' + language_labels['zh-t'] + '</a>' +
                '</div>' +
            '</div>' +
        '</div>';
    $('.a2p-language-dropdown-container').remove();
    headerEl.append($(languageButtonsHTML));
    $('.a2p-language-dropdown-container .a2p-language-dropdown-label').on('click', function() {
      languageSelectorClickedEvent();
    });
    $('.a2p-language-dropdown-container .dropdown-item').on('click', function() {
      var language = $(this).data('lang');
      languageSelectEvent(language);
      url_action_perform('language_button_clicked', { language: language })
    });
}

/* Manually redirect the user to clear cookies
 * after an idle timeout of 60 minutes. */

var idleTime = 0;

//Increment the idle time counter every minute.
var idleInterval = setInterval(timerIncrement, 60000); // 1 minute

//Zero the idle timer on mouse movement.
$(window).mousemove(function (e) {
    idleTime = 0;
});
$(window).keypress(function (e) {
    idleTime = 0;
});

function timerIncrement() {
    idleTime = idleTime + 1;
    if (idleTime > 60) { // 60 minutes
        window.location.href = "/user/sign-out?next=https://" + window.location.hostname;
    }
}
