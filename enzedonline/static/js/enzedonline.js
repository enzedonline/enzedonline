const localDateTime = (element, date) => {
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
const convertUTCDateToLocalDate = (date, date_options, time_options) => {
  local_date = new Date(date.getTime() + date.getTimezoneOffset() * 60000);
  return (
    local_date.toLocaleDateString(undefined, date_options) +
    " " +
    local_date.toLocaleTimeString(undefined, time_options)
  );
};

// global on document ready code
$(document).ready(() => {

  // set all external links and documents to open in new tab
  $('a[href^="http"], a[href^="/documents/"]').attr({ 'target': '_blank', 'rel': 'nofollow noopener' });

  // change rich text <span class="fa-icon"> font awesome tags: 
  // <span class="fa-icon">something</span> -> <span class="something">&nbsp;&nbsp;&nbsp;&nbsp;</span>
  faIcons = [...document.getElementsByClassName('fa-icon')];
  faIcons.forEach(faIcon => {
    const faClass = faIcon.innerText;
    if (faClass) {
      faIcon.innerHTML = "&nbsp;".repeat(4);
      faIcon.className = faClass;
    }
  });

  // load mathjax if equation found on page
  loadMathJax();
});
// end on document ready code

// load mathjax if equation found on page
const loadMathJax = () => {
  const body = document.body.innerText;
  if (body.match(/(?:\$|\\\(|\\\[|\\begin\{.*?})/)) {
    if (typeof window.MathJax === 'undefined') {
      window.MathJax = {
        tex: {
          inlineMath: { '[+]': [['$', '$']] }
        }
      };
    }
    let script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = 'https://polyfill.io/v3/polyfill.min.js?features=es6';
    document.head.appendChild(script);
    script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js';
    script.id = 'MathJax-script';
    script.async = true;
    document.head.appendChild(script);
  }
};

// include js script only if not already included
const include_js = (js, id) => {
  const script_tag = document.getElementById(id);
  if (!script_tag) {
    const new_script = document.createElement('script');
    new_script.type = 'text/javascript';
    new_script.src = js;
    new_script.id = id;
    document.head.appendChild(new_script);
    if (document.getElementById(id)) {
      return new_script;
    }
  } else {
    return script_tag;
  }
};

// include css only if not already included
const include_css = (css, id) => {
  const link_tag = document.getElementById(id);
  if (!link_tag) {
    const new_link = document.createElement('link');
    new_link.rel = 'stylesheet';
    new_link.href = css;
    new_link.id = id;
    document.head.appendChild(new_link);
    if (document.getElementById(id)) {
      return new_link;
    }
  } else {
    return link_tag;
  }
};
