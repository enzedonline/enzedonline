function getQuerySelector(levels) {
  // Return a fomatted list of header tags to include in the element search
  // H1 tags are not included in the ToC -> base level = H2
  // levels=1 returns "h2" only, levels=5 returns "h2,h3,h4,h5,h6"
  const baseLevel = 2;
  const selector = [];
  for (let hLevel = baseLevel; hLevel < baseLevel + levels; hLevel++) {
    selector.push("h" + hLevel);
  }
  return selector.join();
}

function listContents(
  tocElement,
  scopeElement = "body",
  levels = 3,
  tocTitle = false
) {
  // Create Table of Contents (ToC) based on header tags (H2 to H6)
  // Required: tocElement - element ID to create ToC in (<DIV> recommended)
  // Optional: scopeElement - element to limit the search to, defaults to <body>. Change definition below to search by ID.
  // Optional: levels - number of levels to include in ToC (1 to 5 starting with H2). Default=3 (H2-H4)
  // Optional: tocTitle - string to display as ToC title, defaults to no title (false)

  const toc = document.getElementById(tocElement);
  const scope = document.getElementsByTagName(scopeElement);

  if (scope.length > 0 && toc) {
    // scope is HTMLElementArray, take the first element, find the relevant header tags in that element
    const headers = scope[0].querySelectorAll(getQuerySelector(levels));

    // create ToC only if headers found
    if (headers.length > 0) {
      // add ToC title if supplied, add css classes
      if (tocTitle) {
        let title = toc.appendChild(document.createElement("P"));
        title.innerText = tocTitle;
        title.classList.add("toc", "toc-title");
      }

      // add ToC list DIV, add css classes
      const list = toc.appendChild(document.createElement("DIV"));
      list.classList.add("toc", "toc-list");

      // loop through headers in order
      for (let i = 0; i < headers.length; i++) {
        // determine nesting level (h2->1, h3->2 etc)
        const level = Number(headers[i].nodeName[1]) - 1;
        
        // if header has no id, create one and assign to header
        // pre-fix id with index to avoid duplicate id's
        if (!headers[i].id) {
          headers[i].id = `${i + 1}-${slugify(headers[i].innerText)}`;
        }

        // create element to hold link, add css including level specific css class
        const linkLine = list.appendChild(document.createElement("P"));
        linkLine.classList.add(`toc`, "toc-list", `toc-item-l${level}`);

        // create link to point to ID of header
        const link = linkLine.appendChild(document.createElement("A"));
        link.appendChild(document.createTextNode(headers[i].innerText));
        link.href = `#${headers[i].id}`;
      }
    }
  } else {
    if (scope.length == 0) {
      console.error(`ToC: Missing <${scopeElement}> element`);
    }
    if (!toc) {
      console.error(`ToC: Missing ToC target element with ID ${tocElement}`);
    }
  }
}

function slugify(str) {
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

  // Remove invalid chars
  str = str
    .replace(/[^a-z0-9 -]/g, "")
    // Collapse whitespace and replace by -
    .replace(/\s+/g, "-")
    // Collapse dashes
    .replace(/-+/g, "-");

  return str;
}
