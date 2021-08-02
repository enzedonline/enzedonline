window.fbAsyncInit = function() {
    FB.init({
      appId      : '492927945342914',
      cookie     : true,
      xfbml      : true,
      version    : '11.0'
    });
      
    FB.AppEvents.logPageView();   
      
  };

  (function(d, s, id){
     var js, fjs = d.getElementsByTagName(s)[0];
     if (d.getElementById(id)) {return;}
     js = d.createElement(s); js.id = id;
     js.src = "https://connect.facebook.net/en_US/sdk.js";
     fjs.parentNode.insertBefore(js, fjs);
   }(document, 'script', 'facebook-jssdk'));


  //  Dropdown menu aligns with right of button, lose focus after click
       $(document).ready(function() {
           $('.dropright button').on("click", function(e) {
               e.stopPropagation();
               e.preventDefault();
   
               if (!$(this).next('div').hasClass('show')) {
               $(this).next('div').addClass('show');
               } else {
               $(this).next('div').removeClass('show');
               }
           });
       });
       $(".navbar-toggler").mouseup(function(){
           $(this).blur();
       })
   
   