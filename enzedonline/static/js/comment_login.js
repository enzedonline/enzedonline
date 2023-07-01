document.addEventListener("DOMContentLoaded", () => {
  const login_url = JSON.parse(document.getElementById("login_url").textContent);

  document.querySelector("#id_login_first_link").addEventListener("click", (event) => {
    event.preventDefault();
    document.querySelector("#id_login_form").style.display = "block";
  });

  document.querySelector("#id_submit_login_form").addEventListener("click", (event) => {
    event.preventDefault();

    fetch(login_url, {
      method: "POST",
      body: new FormData(document.querySelector("#id_login_form"))
    })
      .then((response) => {
        if (response.ok) {
          document.querySelector("#id_login_form").style.display = "none";
          document.querySelector("#id_login_first_link").style.display = "none";
          location.reload();
        } else {
          document.querySelector("#id_login_form").submit();
        }
      })
      .catch((error) => {
        console.error(error);
      });
  });
});
