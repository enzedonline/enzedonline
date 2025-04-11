import { tableOfContents } from "./toc-min.js";

export const tocBlock = () => {
    const tocElement = JSON.parse(document.getElementById("tocElement").textContent);
    const scopeElement = JSON.parse(document.getElementById("scopeElement").textContent);
    const levels = JSON.parse(document.getElementById("levels").textContent);
    const tocTitle = JSON.parse(document.getElementById("tocTitle").textContent);
    if (document.readyState === 'interactive') {
        queueMicrotask(() => tableOfContents(tocElement, scopeElement, levels, tocTitle));
    } else {
        document.addEventListener('DOMContentLoaded', () => {
            tableOfContents(tocElement, scopeElement, levels, tocTitle);
        });
    }
}