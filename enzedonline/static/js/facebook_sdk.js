window.fbAsyncInit = () => {
  FB.init({
    appId: '492927945342914',
    cookie: true,
    xfbml: true,
    version: 'v11.0'
  });

  FB.AppEvents.logPageView();
};

((d, s, id) => {
  if (d.getElementById(id)) {
    return;
  }
  const js = d.createElement(s);
  js.id = id;
  js.src = "https://connect.facebook.net/en_US/sdk.js";
  const fjs = d.getElementsByTagName(s)[0];
  fjs.parentNode.insertBefore(js, fjs);
})(document, 'script', 'facebook-jssdk');
