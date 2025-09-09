/**
 * @typedef {Object} AccordionItem
 * @param {string} heading - The header text for the accordion section
 * @param {string} detail - The content for the accordion section
 * @property {HTMLElement} element - The accordion item element
 * @param {HTMLElement} button - The accordion item button element
 */
class AccordionItem {
    element = undefined;
    button = undefined;

    constructor(heading, detail) {
        const idString = Math.random().toString(36).substring(2, 6);
        this.element = document.createElement('div');
        this.element.className = 'base-accordion-item';
        const header = document.createElement('div');
        header.className = 'base-accordion-header';
        this.button = document.createElement('button');
        this.button.id = `accordion-${idString}-button`
        this.button.className = 'base-accordion-btn';
        this.button.innerHTML = this._sanitizeHTML(heading ?? '');
        this.button.setAttribute('aria-controls', `accordion-${idString}-content`);
        this.button.setAttribute('aria-expanded', 'false');
        header.appendChild(this.button);
        const body = document.createElement('div');
        body.className = 'base-accordion-body';
        body.innerHTML = this._sanitizeHTML(detail ?? '');
        body.setAttribute('id', `accordion-${idString}-content`);
        body.setAttribute('role', 'region');
        body.setAttribute('aria-labelledby', this.button.id); 
        this.element.append(header, body);
    }

    /**
     * @description remove the element
     */
    destroy() {
        this.element.remove();
        this.element = null;
        this.button = null;
    }

    /**
     * @returns {boolean} True if item is expanded
     */
    get isExpanded() {
        return this.button.getAttribute('aria-expanded') === 'true';
    }

    /**
     * @param {boolean} [expanded] - sets the expanded state on the item
     */
    setState(expanded) {
        this.button.setAttribute('aria-expanded', expanded);
    }

    /**
     * Sanitizes the given HTML input by removing any <script> elements.
     *
     * @private
     * @param {string} input - The HTML string to be sanitized.
     * @returns {string} - The sanitized HTML string with <script> elements removed.
     */
    _sanitizeHTML(input) {
        const doc = new DOMParser().parseFromString(input, 'text/html');
        doc.querySelectorAll('script').forEach(script => script.remove());
        return doc.body.innerHTML;
    }
}

class AccordionItems {
    _items = [];
    openUnique = true;

    constructor(openUnique = true) {
        this.openUnique = openUnique;
    }

    destroy() {
        this._items.forEach(item => item.destroy());
        this._items = null;
    }

    /**
     * Adds a new item to the accordion
     * @private
     * @param {AccordionItem} accordionItem - The item to add
     * @param {number} index - Optional. Position to insert the item (appends if beyond length). Appends item if omitted.
     * @returns {AccordionItem} The created AccordionItem instance
     */
    _add(heading, detail, index = undefined) {
        const item = new AccordionItem(heading, detail);
        if (typeof(index) !== 'number' || index >= this.element.children.length || index < 0) {
            this._items.push(item);
        } else {
            this._items.splice(index, 0, item);
        }
        return item;
    }

    /**
     * Gets an item from the accordion items collection
     * @param {number | HTMLElement | AccordionItem} accordionItem - Item, index of the item, or accordion item element, to get. Null if invalid or not found.
     */
    get(accordionItem) {
        if (typeof accordionItem === 'number') {
            return this._items[accordionItem] || null;
        } else if (accordionItem instanceof HTMLElement) {
            return this._items.find(item => item.element === accordionItem) || null;
        } else if (accordionItem instanceof AccordionItem) {
            return this._items.includes(accordionItem) ? accordionItem : null;
        }
        return null;
    }

    /**
     * Removes an item from the accordion
     * @param {number | HTMLElement} accordionItem - Index of the item, or accordion item element, to remove. Ignored if invalid.
     */
    remove(accordionItem) {
        const item = this.get(accordionItem);
        if (item) {
            item.destroy();
            this._items.splice(this._items.indexOf(item), 1);
        }
    }

    /**
     * Toggle the expanded state of an accordion item, auto-collapses other items if this.openUnique===true
     * @param {number | HTMLElement} accordionItem - Index of the item, or accordion item element, to collapse/expand. Ignored if invalid.
     * @param {boolean | undefined} [expanded] - Optional. Sets the expanded state on the item. Toggles the current state if omitted.
     */
    setState(accordionItem, expanded = undefined) {
        const thisItem = this.get(accordionItem);
        if (thisItem) {
            const newState = expanded ?? !thisItem.isExpanded;
            if (this.openUnique && newState) {
                this._items.forEach((item) => item.setState(item === thisItem));
            } else {
                thisItem.setState(newState);
            }
        }
    }
}

/**
 * Creates an accordion component
 * @param {AccordionItem[]} accordionItems - Array of items to display [{heading: string, detail:string}, ...]
 * @param {string} [className] - Optional additional CSS class name to apply to accordion container
 * @param {boolean} [openUnique] - If true, collapses other items when an item is expanded (default behaviour)
 * @throws {Error} If accordionItems is not an array
 */
export class BaseAccordion {
    element = undefined;
    items;

    constructor(accordionItems, className = null, openUnique = true) {
        if (!Array.isArray(accordionItems)) {
            throw new Error('accordionItems must be an array');
        }
        this._createNewAccordion(accordionItems, className, openUnique);
        window.accordion=this;
    }

    /**
     * Cleanup resources and event listeners
     * @public
     */
    destroy() {
        this.items.destroy();
        if (this.element) {
            this.element.removeEventListener('click', this._clickHandler);
            this.element.remove();
            this.element = null;
        }
    }

    /**
     * Creates new accordion container with contents and options from constructor parameters
     * @private
     * @param {AccordionItem[]} accordionItems - Array of items to display [{heading: string, detail:string}, ...]
     * @param {string} [className] - Optional. Additional CSS class name to apply to accordion container
     * @param {boolean} [openUnique] - Optional. If true, collapses other items when an item is expanded (default behaviour)
     */
    _createNewAccordion(accordionItems, className = null, openUnique = true) {
        this.items = new AccordionItems(openUnique);
        this.element = document.createElement('div');
        this.element.className = 'base-accordion';
        this.element.setAttribute('role', 'presentation');
        if (className) this.element.classList.add(className);
        accordionItems.forEach((accordionItem, index) => {
            const { heading, detail } = accordionItem;
            this.addItem(heading, detail, index);
        });
        this.element.addEventListener('click', this._clickHandler);
    }

    /**
     * Handles click events on accordion buttons
     * @private
     * @param {MouseEvent} clickEvent - The click event object
     */
    _clickHandler = (clickEvent) => {
        const clickedItem = this.items.get(clickEvent.target.closest('div.base-accordion-item'));
        if (clickedItem) this.items.setState(clickedItem);
    }

    /**
     * Adds a new item to the accordion
     * @param {string} heading - HTML string for the item button innerHTML
     * @param {string} detail - HTML string for the item detail innerHTML
     * @param {number} index - Optional. Position to insert the item. Appends item if omitted or not valid.
     * @returns {AccordionItem} The created AccordionItem instance
     */
    addItem(heading, detail, index = undefined) {
        const item = this.items._add(heading, detail)
        if (item) {
            if (typeof(index) !== 'number' || index >= this.element.children.length || index < 0) {
                this.element.appendChild(item.element);
            } else {
                this.element.insertBefore(item.element, this.element.children[index]);
            }
            return item;
        }
    }

}