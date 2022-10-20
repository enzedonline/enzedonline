let localDateTime = (element, date) => {
  // Only run if element exists and date is valid
  if (element != null && date instanceof Date && !isNaN(date)) {
    const date_options = {
      weekday: "short",
      year: "numeric",
      month: "long",
      day: "numeric",
    };
    const time_options = { 
      hour: "2-digit", 
      minute: "2-digit", 
      hour12: false 
    };
    element.innerText = convertUTCDateToLocalDate(date, date_options, time_options);
  }
  else {
    if (element == null) {
      console.warn('An null element was passed to localDate, check the element exists on the current page.')
    }
    if (!(date instanceof Date) || isNaN(date)) {
      console.warn('A non-date value was passed to localDate, check a valid datetime object is being passed.')
    }
  }
}

// Usage: document.getElementById("id").innerText = convertUTCDateToLocalDate(new Date('2021-08-12 09:58:22'));
// Non-numeric month format will cause errors in multi-lingual setting
let convertUTCDateToLocalDate = (date, date_options, time_options) => {
  local_date = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return (
    local_date.toLocaleDateString(undefined, date_options) +
    " " +
    local_date.toLocaleTimeString(undefined, time_options)
  );
};

// set all external links to open in new tab
$(document).ready(function () {
  $('a[href^="http://"]').attr("target", "_blank");
  $('a[href^="http://"]').attr("rel", "nofollow noopener");
  $('a[href^="https://"]').attr("target", "_blank");
  $('a[href^="https://"]').attr("rel", "nofollow noopener");
});

// change rich text <fa> font awesome tags: 
// <fa style="display:none;">something</fa> -> <fa class="something">&nbsp;&nbsp;&nbsp;&nbsp;</fa>
$(document).ready(() => {
  fa_icons = document.getElementsByTagName('fa');
  for (let i = 0; i < fa_icons.length; i++) {
    const fa_class = fa_icons[i].innerText;
    if (fa_class) {
      fa_icons[i].className = fa_class;
      fa_icons[i].innerHTML = "&nbsp;".repeat(4);
      fa_icons[i].removeAttribute('style');
    }
  }
});

// include js script only if not already included
let include_js = (js, id) => {
  let script_tag = document.getElementById(`${id}`)
  if (!script_tag) {
    let target_tag = document.getElementsByTagName("head")[0];
    let script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = `${js}`;
    script.id = `${id}`;
    target_tag.appendChild(script);
    if (document.getElementById(`${id}`)) {
      return script;
    }
    else {
      return null;
    } 
  }
  else {
    return script_tag;
  }
}

// include css only if not already included
let include_css = (css, id) => {
  let link_tag = document.getElementById(`${id}`)
  if (!link_tag) {
    let target_tag = document.getElementsByTagName("head")[0];
    let link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = `${css}`;
    link.id = `${id}`;
    target_tag.appendChild(link);
    if (document.getElementById(`${id}`)) {
      return link;
    }
    else {
      return null;
    } 
  }
  else {
    return link_tag;
  }
}

