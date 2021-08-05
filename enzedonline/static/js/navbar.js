//  Dropdown menu aligns with right of button, lose focus after click
$(document).ready(function () {
  $(".dropright button").on("click", function (e) {
    e.stopPropagation();
    e.preventDefault();

    if (!$(this).next("div").hasClass("show")) {
      $(this).next("div").addClass("show");
    } else {
      $(this).next("div").removeClass("show");
    }
  });
});
$(".navbar-toggler").mouseup(function () {
  $(this).blur();
});

respondToVisibility = function (element, callback) {
  var options = {
    root: document.documentElement,
  };

  var observer = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      callback(entry.intersectionRatio > 0);
    });
  }, options);

  observer.observe(element);
};

respondToVisibility(document.getElementById("searchbox"), (visible) => {
  if (visible) {
    document.getElementById("searchbox").focus();
  }
});
