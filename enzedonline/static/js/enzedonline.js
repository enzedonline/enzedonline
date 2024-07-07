// Usage: localDateTime('someElementID', '2023-12-31 23:59:59');
// Amend date/time options to suit:
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat

const localDateTime = (elementID, dateString) => {
  const element = document.getElementById(elementID);
  // Only run if element exists and date is valid
  if (element != null) {
    const date_options = {
      // weekday: "short",
      year: "numeric",
      month: "long",
      day: "numeric",
    };
    const time_options = {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false
    };
    element.innerText = convertUTCDateToLocalDate(dateString, date_options, time_options);
  }
  else {
    console.warn('An null element was passed to localDate, check the element exists on the current page.')
  }
}

const localiseDates = (
    className, 
    date_options = {weekday: "short", year: "numeric", month: "long", day: "numeric"}, 
    time_options = {hour: "2-digit", minute: "2-digit", hour12: false}
  ) => {
    document.querySelectorAll(`.${className}`).forEach((element) => {
      const utcDateString = element.innerText;
      const localDateString = convertUTCDateToLocalDate(utcDateString, date_options, time_options);
      element.innerText = localDateString;
    });

}

// Non-numeric month format will cause errors in multi-lingual setting
const convertUTCDateToLocalDate = (dateString, date_options, time_options) => {
  const date = new Date(Date.parse(dateString + " UTC"));
  if (date instanceof Date && !isNaN(date)) {
    const formattedDate = date.toLocaleDateString(undefined, date_options);
    const formattedTime = date.toLocaleTimeString(undefined, time_options);
    const localTimezone = date.toLocaleDateString(navigator.language, { timeZoneName:'short' }).split(/\s+/).pop();
    return `${formattedDate} ${formattedTime} (${localTimezone})`;
  } else {
    console.warn('Date string could not be parsed, check a valid ISO formatted datetime string is being passed.')
  }
};


// global on document ready code
document.addEventListener('DOMContentLoaded', () => {
  // set all external links and documents to open in new tab
  document.querySelectorAll('a[href^="http"], a[href^="/documents/"]').forEach(link => {
    link.setAttribute('target', '_blank');
    link.setAttribute('rel', 'nofollow noopener');
  });

  // change rich text <span class="fa-icon"> font awesome tags: 
  // <span class="fa-icon">something</span> -> <span class="something">&nbsp;&nbsp;&nbsp;&nbsp;</span>
  const faIcons = document.querySelectorAll('.fa-icon');
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
    // script.type = 'text/javascript';
    // script.src = 'https://polyfill.io/v3/polyfill.min.js?features=es6';
    // document.head.appendChild(script);
    // script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js';
    script.id = 'MathJax-script';
    script.async = true;
    document.head.appendChild(script);
  }
};

// include js script only if not already included
const include_js = (js, id) => {
  return new Promise((resolve, reject) => {
    let script_tag = document.getElementById(id);
    if (!script_tag) {
      const head = document.head || document.getElementsByTagName('head')[0];
      script_tag = document.createElement('script');
      script_tag.type = 'text/javascript';
      script_tag.src = js;
      script_tag.id = id;
      script_tag.onload = resolve; // Resolve the promise when script is loaded
      script_tag.onerror = reject; // Reject the promise on error
      head.appendChild(script_tag);
    } else {
      resolve(); // Resolve the promise if script is already loaded
    }
  });
};

// include css only if not already included
const include_css = (css, id) => {
  let link_tag = document.getElementById(id);
  if (!link_tag) {
    const head = document.head || document.getElementsByTagName('head')[0];
    link_tag = document.createElement('link');
    link_tag.rel = 'stylesheet';
    link_tag.href = css;
    link_tag.id = id;
    head.appendChild(link_tag);
  }
};
