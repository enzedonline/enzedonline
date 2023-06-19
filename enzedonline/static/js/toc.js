const listContents = (
  tocElement,
  scopeElement = "body",
  levels = 3,
  tocTitle = false
) => {
  // Create Table of Contents (ToC) based on heading tags (H2 to H6)
  // Required: tocElement - element ID to create ToC in (<DIV> only)
  // Optional: scopeElement - element to limit the search to, defaults to <body>.
  //                          Can be element tag or element ID.
  // Optional: levels - number of levels to include in ToC (1 to 5 starting with H2). Default=3 (H2-H4)
  // Optional: tocTitle - string to display as ToC title, defaults to no title (false)
  const toc = document.getElementById(tocElement);
  const scope = document.querySelector(scopeElement);

  // find target DIV element to write ToC to, only accept DIV as valid element type, return on error
  if (!toc || toc.tagName !== "DIV") {
    console.error(
      `ToC: Missing or invalid target element with id=${tocElement}`
    );
    return;
  }

  // find tag name matching scopeElement, return if not found
  if (!scope) {
    console.error(
      `ToC: Missing element with id=${scopeElement} or valid element tag name`
    );
    return;
  }

  // determine which heading tags to search by slicing list 'levels' deep
  const tags = ["H2", "H3", "H4", "H5", "H6"].slice(0, levels);

  // find the relevant heading tags contained within the scope element
  const headings = Array.from(scope.querySelectorAll(tags.join(", ")));

  // create ToC only if headings found
  if (headings.length === 0) {
    return;
  }

  // add ToC title if supplied
  if (tocTitle) {
    const title = document.createElement("H2");
    title.innerText = tocTitle;
    title.classList.add("toc", "toc-title");
    toc.appendChild(title);
  }

  // nest ToC inside nav element 
  const nav = document.createElement("NAV");
  const list = document.createElement("UL");
  list.classList.add("toc", "toc-list");
  list.setAttribute("role", "list");

  // add ToC list to nav, add css classes
  // loop through headings in order of position on page
  headings.forEach((heading, index) => {
    // determine nesting level (h2->1, h3->2 etc)
    const level = Number(heading.nodeName[1]) - 1;

    // if heading has no id, create one from slugified title and assign to heading
    // pre-fix id with index to avoid duplicate id's
    if (!heading.id) {
      heading.id = `${index + 1}-${slugify(heading.innerText)}`;
    }

    // create element to hold link, add css including level specific css class
    const contentsItem = document.createElement("LI");
    contentsItem.classList.add(`toc`, `toc-item-l${level}`);

    // create link to point to ID of heading
    const link = document.createElement("A");
    link.textContent = heading.innerText;
    link.href = `#${heading.id}`;

    // add permalink to heading
    const permaLink = document.createElement("A");
    permaLink.className = "toc-link";
    permaLink.href = `#${heading.id}`;
    permaLink.innerHTML = heading.innerHTML;
    heading.innerHTML = "";
    heading.appendChild(permaLink);

    contentsItem.appendChild(link);
    list.appendChild(contentsItem);
  });

  // add nav & list to DOM
  nav.appendChild(list);
  toc.appendChild(nav);
};

const convertExtendedAscii = (str) => {
  // replace any extended-latin characters with standard ASCII letters
  const characterMap = {
    'À': 'A', 'Á': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A', 'Å': 'A', 'Æ': 'AE', 'Ç': 'C', 'È': 'E', 'É': 'E', 'Ê': 'E', 'Ë': 'E',
    'Ì': 'I', 'Í': 'I', 'Î': 'I', 'Ï': 'I', 'Ð': 'D', 'Ñ': 'N', 'Ò': 'O', 'Ó': 'O', 'Ô': 'O', 'Õ': 'O', 'Ö': 'O', 'Ø': 'O',
    'Ù': 'U', 'Ú': 'U', 'Û': 'U', 'Ü': 'U', 'Ý': 'Y', 'Þ': 'TH', 'ß': 'ss', 'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a',
    'å': 'a', 'æ': 'ae', 'ç': 'c', 'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e', 'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i', 'ð': 'd',
    'ñ': 'n', 'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o', 'ø': 'o', 'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u', 'ý': 'y',
    'þ': 'th', 'ÿ': 'y', 'Ā': 'A', 'ā': 'a', 'Ă': 'A', 'ă': 'a', 'Ą': 'A', 'ą': 'a', 'Ć': 'C', 'ć': 'c', 'Ĉ': 'C', 'ĉ': 'c',
    'Ċ': 'C', 'ċ': 'c', 'Č': 'C', 'č': 'c', 'Ď': 'D', 'ď': 'd', 'Đ': 'D', 'đ': 'd', 'Ē': 'E', 'ē': 'e', 'Ĕ': 'E', 'ĕ': 'e',
    'Ė': 'E', 'ė': 'e', 'Ę': 'E', 'ę': 'e', 'Ě': 'E', 'ě': 'e', 'Ĝ': 'G', 'ĝ': 'g', 'Ğ': 'G', 'ğ': 'g', 'Ġ': 'G', 'ġ': 'g',
    'Ģ': 'G', 'ģ': 'g', 'Ĥ': 'H', 'ĥ': 'h', 'Ħ': 'H', 'ħ': 'h', 'Ĩ': 'I', 'ĩ': 'i', 'Ī': 'I', 'ī': 'i', 'Ĭ': 'I', 'ĭ': 'i',
    'Į': 'I', 'į': 'i', 'İ': 'I', 'ı': 'i', 'Ĳ': 'IJ', 'ĳ': 'ij', 'Ĵ': 'J', 'ĵ': 'j', 'Ķ': 'K', 'ķ': 'k', 'ĸ': 'k', 'Ĺ': 'L',
    'ĺ': 'l', 'Ļ': 'L', 'ļ': 'l', 'Ľ': 'L', 'ľ': 'l', 'Ŀ': 'L', 'ŀ': 'l', 'Ł': 'L', 'ł': 'l', 'Ń': 'N', 'ń': 'n', 'Ņ': 'N',
    'ņ': 'n', 'Ň': 'N', 'ň': 'n', 'ŉ': 'n', 'Ō': 'O', 'ō': 'o', 'Ŏ': 'O', 'ŏ': 'o', 'Ő': 'O', 'ő': 'o', 'Œ': 'OE', 'œ': 'oe',
    'Ŕ': 'R', 'ŕ': 'r', 'Ŗ': 'R', 'ŗ': 'r', 'Ř': 'R', 'ř': 'r', 'Ś': 'S', 'ś': 's', 'Ŝ': 'S', 'ŝ': 's', 'Ş': 'S', 'ş': 's',
    'Š': 'S', 'š': 's', 'Ţ': 'T', 'ţ': 't', 'Ť': 'T', 'ť': 't', 'Ŧ': 'T', 'ŧ': 't', 'Ũ': 'U', 'ũ': 'u', 'Ū': 'U', 'ū': 'u',
    'Ŭ': 'U', 'ŭ': 'u', 'Ů': 'U', 'ů': 'u', 'Ű': 'U', 'ű': 'u', 'Ų': 'U', 'ų': 'u', 'Ŵ': 'W', 'ŵ': 'w', 'Ŷ': 'Y', 'ŷ': 'y',
    'Ÿ': 'Y', 'Ź': 'Z', 'ź': 'z', 'Ż': 'Z', 'ż': 'z', 'Ž': 'Z', 'ž': 'z', 'ſ': 's', 'ƒ': 'f', 'Ơ': 'O', 'ơ': 'o', 'Ư': 'U',
    'ư': 'u', 'Ǎ': 'A', 'ǎ': 'a', 'Ǐ': 'I', 'ǐ': 'i', 'Ǒ': 'O', 'ǒ': 'o', 'Ǔ': 'U', 'ǔ': 'u', 'Ǖ': 'U', 'ǖ': 'u', 'Ǘ': 'U',
    'ǘ': 'u', 'Ǚ': 'U', 'ǚ': 'u', 'Ǜ': 'U', 'ǜ': 'u', 'Ǻ': 'A', 'ǻ': 'a', 'Ǽ': 'AE', 'ǽ': 'ae', 'Ǿ': 'O', 'ǿ': 'o'
  };

  return str.replace(/[^\u0000-\u007E]/g, (a) => {
    return characterMap[a] || '';
  });
};

const slugify = (str) => {
  str = str.replace(/^\s+|\s+$/g, ''); // remove leading and trailing whitespace
  str = convertExtendedAscii(str);     // replace any extended-latin characters with standard ASCII letters
  str = str.toLowerCase()              // convert to lower case
    .replace(/[^a-z0-9 -]/g, '')       // Remove invalid chars
    .replace(/\s+/g, '-')              // Collapse whitespace and replace with dash -
    .replace(/-+/g, '-');              // Collapse duplicate dashes

  return str;
};


document.addEventListener("DOMContentLoaded", () => {
  const tocElement = JSON.parse(document.getElementById("tocElement").textContent);
  const scopeElement = JSON.parse(document.getElementById("scopeElement").textContent);
  const levels = JSON.parse(document.getElementById("levels").textContent);
  const tocTitle = JSON.parse(document.getElementById("tocTitle").textContent);
  listContents(tocElement, scopeElement, levels, tocTitle);
});
