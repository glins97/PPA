$( document ).ready(function() {
  $('#id_file').change(function() {
    document.getElementsByName('_continue')[0].click()
    return false;
  });
});