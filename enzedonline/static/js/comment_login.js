$(document).ready(function () {

    const login_url = JSON.parse(document.getElementById("login_url").textContent);


    $("#id_login_first_link").click(function (event) {
    event.preventDefault();
    $("#id_login_form").show();
  });

  $("#id_submit_login_form").click(function (event) {
    event.preventDefault();

    $.ajax({
      type: "POST",
      url: `"${login_url}"`,
      data: $("#id_login_form").serialize(),
      success: function (response, status) {
        $("#id_login_form").hide();
        $("#id_login_first_link").hide();
        location.reload();
      },
      error: function (xhr, status, error) {
        $("#id_login_form").submit();
      },
    });
  });
});
