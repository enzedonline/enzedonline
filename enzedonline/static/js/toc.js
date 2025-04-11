export const tableOfContents = (
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
  list.setAttribute("role", "tree");

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
    contentsItem.setAttribute("role", "treeitem");
    contentsItem.setAttribute("aria-level", level);

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

// --------- slugify function --------- //

const INVALID_CHARS_REGEX = /[^a-z0-9 -]/g;
const WHITESPACE_REGEX = /\s+/g;
const MULTI_DASH_REGEX = /-+/g;

const DIACRITICS_REGEX = /[\u0300-\u036f]/g;
const specialCharsMap = {
    'ß': 'ss',
    'Æ': 'AE',
    'æ': 'ae',
    'Œ': 'OE',
    'œ': 'oe',
    'ø': 'o',
    'Ø': 'O'
};

const specialCharsRegex = new RegExp(
    `[${Object.keys(specialCharsMap).join('')}]`,
    'g'
);

const convertExtendedLatin = (str) => {
    // replace any extended-latin characters with standard ASCII letters
    // any non-matching letters are dropped from the returned string
    return str
        .replace(specialCharsRegex, ch => specialCharsMap[ch] || '')
        .normalize("NFD")
        .replace(DIACRITICS_REGEX, ""); // remove diacritics;
};

/**
 * Converts a given string into a URL-friendly "slug".
 * 
 * The function performs the following transformations:
 * 1. Removes leading and trailing whitespace.
 * 2. Replaces extended Latin characters with standard ASCII letters.
 * 3. Converts the string to lowercase.
 * 4. Removes invalid characters (anything other than letters, numbers, spaces, and dashes).
 * 5. Replaces spaces with dashes.
 * 6. Collapses multiple consecutive dashes into a single dash.
 * 
 * @param {string} str - The input string to be slugified.
 * @returns {string} - The slugified version of the input string.
 */
export const slugify = (str) =>
    convertExtendedLatin(str.trim())
        .toLowerCase()
        .replace(INVALID_CHARS_REGEX, '') // remove invalid characters
        .replace(WHITESPACE_REGEX, '-')   // replace spaces with dashes
        .replace(MULTI_DASH_REGEX, '-');  // collapse multiple dashes into a single dash