export class BlogListing {
    tags = [];
    activeTags = [];
    baseUrl = '';
    filterItems = null;
    offCanvas = null;
    tagListContainer = null;
    travelblogCardList = null;
    clearBtn = null;
    applyBtn = null;
    searchForm = null;
    searchInput = null;

    constructor(baseUrl) {
        this.baseUrl = baseUrl;
        this.tagListContainer = document.getElementById('travelblog-taglist');
        this.travelblogCardList = document.getElementById('travelblog-card-list');
        this.filterItems = document.querySelector('div.travelblog-filter-items');
        this.offCanvas = bootstrap.Offcanvas.getOrCreateInstance(document.querySelector('div.travelblog-offcanvas'));
        this.clearBtn = document.getElementById('clear-filter-btn');
        this.applyBtn = document.getElementById('apply-filter-btn');
        this.searchForm = document.getElementById('search-travelblogs-form');
        this.searchInput = document.getElementById('search-travelblogs-input');
        this.getTagList();
        this.getActiveTags();
        this.preSelectFilterTags();
        this.addEventListeners();
    }

    addEventListeners = () => {
        this.filterItems?.addEventListener('click', (event) => {
            const target = event.target;
            if (target.classList.contains('tag-item')) {
                target.classList.toggle('active');
            }
        });
        this.clearBtn?.addEventListener('click', this.clearButtonHandler);
        this.applyBtn?.addEventListener('click', this.applyButtonHandler);
        this.searchForm?.addEventListener('submit', this.searchFormHandler);
        this.tagListContainer?.addEventListener('click', this.tagListClickHandler);
    }

    clearButtonHandler = () => {
        window.location.href = this.baseUrl;
    }

    applyButtonHandler = () => {
        const selectedTagElements = this.filterItems.querySelectorAll('.tag-item.active');
        const filterUrl = selectedTagElements.length 
            ? `tags/${Array.from(selectedTagElements).map(tagElem => tagElem.getAttribute('data-tag-slug')).filter(Boolean).join('/')}/` 
            : '';
        window.location.href = `${this.baseUrl}${filterUrl}#filter`;
    }

    searchFormHandler = (e) => {
        e.preventDefault();
        const query = this.searchInput.value.trim();
        if (!query) {
            window.location.href = `${this.baseUrl}#filter`;
        } else {
            const suffix = `search/?q=${encodeURIComponent(query)}`
            window.location.href = `${this.baseUrl}${suffix}#filter`;
        }
    }

    tagListClickHandler = (e) => {
        const target = e.target;
        const deleteBtn = target.closest('.travelblog-tag-item-delete');
        if (deleteBtn) {
            const tagItem = target.closest('.travelblog-tag-item');
            const tagSlug = tagItem.getAttribute('data-tag-slug');
            this.activeTags = this.activeTags.filter(t => t.slug !== tagSlug);
            const filterURL = this.activeTags.length 
                ? `tags/${this.activeTags.map(tag => tag.slug).join('/')}/` 
                : '';
            window.location.href = `${this.baseUrl}${filterURL}#filter`;
        }
    }

    getTagList = () => {
        const tagElements = this.filterItems?.querySelectorAll('.tag-item');
        if (!tagElements) return [];
        tagElements.forEach(tagElem => {
            const tagSlug = tagElem.getAttribute('data-tag-slug');
            if (tagSlug) {
                this.tags.push({ slug: tagSlug, name: tagElem.textContent });
            }
        });
    }

    getActiveTags = () => {
        const url = new URL(window.location.href);
        const basePath = new URL(this.baseUrl).pathname;
        let relativePath = url.pathname.slice(basePath.length);
        if (relativePath.startsWith("tags/")) {
            relativePath = relativePath.slice("tags/".length);
        }
        const slugsInUrl = relativePath.split("/").filter(Boolean);
        this.activeTags = this.tags.filter(tag => slugsInUrl.includes(tag.slug));
    }

    preSelectFilterTags = () => {
        if (!this.filterItems) return;
        const tagElements = this.filterItems.querySelectorAll('.tag-item');
        tagElements.forEach(tagElem => {
            const tagSlug = tagElem.getAttribute('data-tag-slug');
            if (this.activeTags.some(tag => tag.slug === tagSlug)) {
                tagElem.classList.add('active');
            } else {
                tagElem.classList.remove('active');
            }
        });
    }

    applyFlexMasonry = () => {
        if (!this.travelblogCardList) return;
        if (this.travelblogCardList.querySelectorAll('.travelblog-summary').length > 0) {
            flexMasonryInit(this.travelblogCardList);
            setTimeout(() => {
                flexMasonryInit(this.travelblogCardList);
            }, 1000);
        } else {
            requestAnimationFrame(this.applyFlexMasonry);
        }
    };
}