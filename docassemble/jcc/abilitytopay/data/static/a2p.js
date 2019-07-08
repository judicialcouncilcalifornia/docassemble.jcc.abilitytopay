function prepareFileUpload() {
  console.log('Preparing custom file upload.');
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
      $('.a2p-file-upload-label').text('Use a different photo');
    } else {
      $('.a2p-file-upload-label').text('Add a photo');
    }
  };

  $('.a2p-file-remove-button').on('click', function() {
    imagePreviewFailed = false;
    // Clear the uploaded files
    fileInputEl[0].value = '';
    renderAll();
  });

  fileInputEl.on('change', function() {
    imagePreviewFailed = false;
    renderAll();
  });

  // If the image preview fails, e.g. because someone
  // uploaded a PDF:
  $('.a2p-image-preview').on('error', function() {
    imagePreviewFailed = true;
    renderAll();
  });
}

// Uncomment below when we are ready to render a language dropdown in UAT.

// function insertLanguageDropdown(active_lang) {
//     var language_labels = {
//         'en': 'English',
//         'es': 'Español',
//         'zh-s': '简体中文',
//         'zh-t': '繁体中文'
//     };
//     var headerEl = $('.container.danavcontainer');
//     var languageButtonsHTML = '' +
//         '<div class="a2p-language-dropdown-container">' +
//             '<div class="dropdown a2p-language-dropdown">' +
//                 '<a href="#" class="a2p-language-dropdown-label nav-link dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">' +
//                     '<img class="a2p-language-dropdown-label-icon" src="/packagestatic/docassemble.jcc.abilitytopay/switch-language.png">' +
//                     '<span class="a2p-language-dropdown-label-text">' + language_labels[active_lang] + '</span>' +
//                 '</a>' +
//                 '<div class="dropdown-menu dropdown-menu-right" aria-labelledby="dropdownMenuButton">' +
//                     '<a class="dropdown-item" href="' + url_action('language_button_clicked', { language: 'en'}) + '">' + language_labels['en'] + '</a>' +
//                     '<a class="dropdown-item" href="' + url_action('language_button_clicked', { language: 'es'}) + '">' + language_labels['es'] + '</a>' +
//                     '<a class="dropdown-item" href="' + url_action('language_button_clicked', { language: 'zh-s'}) + '">' + language_labels['zh-s'] + '</a>' +
//                     '<a class="dropdown-item" href="' + url_action('language_button_clicked', { language: 'zh-t'}) + '">' + language_labels['zh-t'] + '</a>' +
//                 '</div>' +
//             '</div>' +
//         '</div>';
//     headerEl.append($(languageButtonsHTML));
// }

// $(document).on('daPageLoad', function() {
//     let lang = $('#a2p-python-var-lang').attr('data-value');
//     insertLanguageDropdown(lang);
// });

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
