document.addEventListener("DOMContentLoaded", () => {
  const droprightButtons = Array.from(document.querySelectorAll(".dropright button"));
  droprightButtons.forEach((button) => {
    button.addEventListener("click", (e) => {
      e.stopPropagation();
      e.preventDefault();
      const dropdownDiv = button.nextElementSibling;
      if (!dropdownDiv.classList.contains("show")) {
        dropdownDiv.classList.add("show");
      } else {
        dropdownDiv.classList.remove("show");
      }
    });
  });
});

const searchbox = document.getElementById("searchbox");
const searchObserver = new IntersectionObserver((entries) => {
  const isVisible = entries[0].isIntersecting;
  if (isVisible) {
    searchbox.focus();
  } else {
    searchbox.blur();
  }
});
searchObserver.observe(searchbox);
