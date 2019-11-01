document.getElementById("submit-form").addEventListener("submit", function(e) {
  e.preventDefault();
  var text = document.getElementById("submit-text").value;
  if (text.length == 0) {
    return;
  }
  this.submit();
});

document
  .getElementById("submission-link")
  .addEventListener("click", function(e) {
    e.preventDefault();
    document.getElementById("submit-text").value += "[link]";
    document.getElementById("submit-text").focus();
  });

document
  .getElementById("submission-link-modal")
  .addEventListener("click", function(e) {
    e.preventDefault();
    document.getElementById("submit-text-modal").value += "[link]";
    document.getElementById("submit-text-modal").focus();
  });
