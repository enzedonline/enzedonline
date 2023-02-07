let listContents = (
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

  let toc, scope;
  // find target DIV element to write ToC to, only accept DIV as valid element type
  toc = document.getElementById(tocElement);
  if (toc) {
    if (toc.tagName !== "DIV") {
      console.error(
        `ToC: Target element is type <${toc.tagName}>, only <DIV> is valid element type.`
      );
      toc = null;
    }
  }

  // find tag name matching scopeElement, if scope tag not found, try finding element by ID
  scope = document.getElementsByTagName(scopeElement)[0];
  if (!scope) {
    scope = document.getElementById(scopeElement);
  }

  if (scope && toc) {
    // determine which heading tags to search by slicing list 'levels' deep
    const tags = ["h2", "h3", "h4", "h5", "h6"].slice(0, levels).join();

    // find the relevant heading tags contained within the scope element
    const headings = scope.querySelectorAll(tags);

    // create ToC only if headings found
    if (headings.length > 0) {
      // add ToC title if supplied, add css classes
      if (tocTitle) {
        let title = toc.appendChild(document.createElement("H2"));
        title.innerText = tocTitle;
        title.classList.add("toc", "toc-title");
      }

      // nest ToC inside nav element 
      const nav = toc.appendChild(document.createElement("NAV"));

      // add ToC list to nav, add css classes
      const list = nav.appendChild(document.createElement("UL"));
      list.classList.add("toc", "toc-list");
      list.setAttribute('role', 'list')

      // loop through headings in order
      for (let i = 0; i < headings.length; i++) {
        // determine nesting level (h2->1, h3->2 etc)
        const level = Number(headings[i].nodeName[1]) - 1;

        // if heading has no id, create one from slugified title and assign to heading
        // pre-fix id with index to avoid duplicate id's
        if (!headings[i].id) {
          headings[i].id = `${i + 1}-${slugify(headings[i].innerText)}`;
        }

        // create element to hold link, add css including level specific css class
        const linkLine = list.appendChild(document.createElement("LI"));
        linkLine.classList.add(`toc`, `toc-item-l${level}`);

        // create link to point to ID of heading
        const link = linkLine.appendChild(document.createElement("A"));
        link.appendChild(document.createTextNode(headings[i].innerText));
        link.href = `#${headings[i].id}`;
      }
    }
  } else {
    if (!scope) {
      console.error(
        `ToC: Missing either <${scopeElement}> or element with id=${scopeElement}`
      );
    }
    if (!toc) {
      console.error(
        `ToC: Missing ToC target <DIV> element with id=${tocElement}`
      );
    }
  }
}

let slugify = (str) => {
  str = str.replace(/^\s+|\s+$/g, "");

  // Make the string lowercase
  str = str.toLowerCase();

  // Remove accents, swap ñ for n, etc
  var from =
    "ÁÄÂÀÃÅČÇĆĎÉĚËÈÊẼĔȆÍÌÎÏŇÑÓÖÒÔÕØŘŔŠŤÚŮÜÙÛÝŸŽáäâàãåčçćďéěëèêẽĕȇíìîïňñóöòôõøðřŕšťúůüùûýÿžþÞĐđßÆa·/_,:;";
  var to =
    "AAAAAACCCDEEEEEEEEIIIINNOOOOOORRSTUUUUUYYZaaaaaacccdeeeeeeeeiiiinnooooooorrstuuuuuyyzbBDdBAa------";
  for (var i = 0, l = from.length; i < l; i++) {
    str = str.replace(new RegExp(from.charAt(i), "g"), to.charAt(i));
  }

  str = str
    .replace(/[^a-z0-9 -]/g, "")   // Remove invalid chars
    .replace(/\s+/g, "-")          // Collapse whitespace and replace with -
    .replace(/-+/g, "-");          // Collapse dashes

  return str;
}

$(document).ready(function () {
  const tocElement = JSON.parse(document.getElementById("tocElement").textContent);
  const scopeElement = JSON.parse(document.getElementById("scopeElement").textContent);
  const levels = JSON.parse(document.getElementById("levels").textContent);
  const tocTitle = JSON.parse(document.getElementById("tocTitle").textContent);
  listContents(tocElement, scopeElement, levels, tocTitle);
});
