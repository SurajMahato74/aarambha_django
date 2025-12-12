
$(document).ready(function() {
  $(".phone_holder").click(function() {
    $(".dropdown_no").toggleClass("visible-dd");
  });

  $(document).click(function(event) {
    var target = $(event.target);
    if (!target.closest(".phone_holder").length && !target.closest(".dropdown_no").length) {
      $(".dropdown_no").removeClass("visible-dd");
    }
  });
});
