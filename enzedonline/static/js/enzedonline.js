// Usage: document.getElementById("id").innerHTML = convertUTCDateToLocalDate(new Date('02 Aug 2021 09:58:22'));
let convertUTCDateToLocalDate = (date) => {
  local_date = new Date(date.getTime() + date.getTimezoneOffset() * 60000);
  const date_options = {
    weekday: "short",
    year: "numeric",
    month: "long",
    day: "numeric",
  };
  const time_options = { hour: "2-digit", minute: "2-digit", hour12: false };
  return (
    local_date.toLocaleDateString(undefined, date_options) +
    " " +
    local_date.toLocaleTimeString(undefined, time_options)
  );
};

$(document).ready(function () {
  $('a[href^="http://"]').attr("target", "_blank");
  $('a[href^="http://"]').attr("rel", "nofollow noopener");
  $('a[href^="https://"]').attr("target", "_blank");
  $('a[href^="https://"]').attr("rel", "nofollow noopener");
});

$(document).ready(function () {
  fa_icons = document.getElementsByTagName('fa');
  for (let i = 0; i < fa_icons.length; i++) {
    const fa_class = fa_icons[i].innerText;
    if (fa_class) {
      fa_icons[i].innerText = "";
      const fa = fa_icons[i].appendChild(document.createElement("i"));
      fa.className = fa_class;
      fa_icons[i].removeAttribute('style');
    }
  }
});

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

