const listContents = (
  tocElement,
  scopeElement = "body",
  levels = 3,
  tocTitle = false
) => {
  const toc = document.getElementById(tocElement);
  const scope = document.querySelector(scopeElement);

  if (!toc || toc.tagName !== "DIV") {
    console.error(
      `ToC: Missing or invalid target element with id=${tocElement}`
    );
    return;
  }

  if (!scope) {
    console.error(
      `ToC: Missing element with id=${scopeElement} or valid element tag name`
    );
    return;
  }

  const tags = ["H2", "H3", "H4", "H5", "H6"].slice(0, levels);

  const headings = Array.from(scope.querySelectorAll(tags.join(", ")));

  if (headings.length === 0) {
    return;
  }

  if (tocTitle) {
    const title = document.createElement("H2");
    title.innerText = tocTitle;
    title.classList.add("toc", "toc-title");
    toc.appendChild(title);
  }

  const nav = document.createElement("NAV");
  const list = document.createElement("UL");
  list.classList.add("toc", "toc-list");
  list.setAttribute("role", "list");

  headings.forEach((heading, index) => {
    const level = Number(heading.nodeName[1]) - 1;

    if (!heading.id) {
      heading.id = `${index + 1}-${slugify(heading.innerText)}`;
    }

    const contentsItem = document.createElement("LI");
    contentsItem.classList.add(`toc`, `toc-item-l${level}`);

    const link = document.createElement("A");
    link.textContent = heading.innerText;
    link.href = `#${heading.id}`;

    const permaLink = document.createElement("A");
    permaLink.className = "toc-link";
    permaLink.href = `#${heading.id}`;
    permaLink.innerHTML = heading.innerHTML;

    heading.innerHTML = "";
    heading.appendChild(permaLink);

    contentsItem.appendChild(link);
    list.appendChild(contentsItem);
  });

  nav.appendChild(list);
  toc.appendChild(nav);
};

const slugify = (str) => {
  str = str.replace(/^\s+|\s+$/g, "");
  str = str.toLowerCase();
  const from =
    "ÁÄÂÀÃÅČÇĆĎÉĚËÈÊẼĔȆÍÌÎÏŇÑÓÖÒÔÕØŘŔŠŤÚŮÜÙÛÝŸŽáäâàãåčçćďéěëèêẽĕȇíìîïňñóöòôõøðřŕšťúůüùûýÿžþÞĐđßÆa·/_,:;";
  const to =
    "AAAAAACCCDEEEEEEEEIIIINNOOOOOORRSTUUUUUYYZaaaaaacccdeeeeeeeeiiiinnooooooorrstuuuuuyyzbBDdBAa------";
  for (let i = 0, l = from.length; i < l; i++) {
    str = str.replace(new RegExp(from.charAt(i), "g"), to.charAt(i));
  }
  str = str.replace(/[^a-z0-9 -]/g, "").replace(/\s+/g, "-").replace(/-+/g, "-");
  return str;
};

document.addEventListener("DOMContentLoaded", function () {
  const tocElement = JSON.parse(document.getElementById("tocElement").textContent);
  const scopeElement = JSON.parse(document.getElementById("scopeElement").textContent);
  const levels = JSON.parse(document.getElementById("levels").textContent);
  const tocTitle = JSON.parse(document.getElementById("tocTitle").textContent);
  listContents(tocElement, scopeElement, levels, tocTitle);
});
