class CodeBlockDefinition extends window.wagtailStreamField.blocks
    .StructBlockDefinition {
    render(placeholder, prefix, initialState, initialError) {
        this.block = super.render(
            placeholder,
            prefix,
            initialState,
            initialError,
        );
        // code child block textarea widget
        this.codeTextarea = this.block.childBlocks.code.widget.input;
        // language child block select widget
        this.languageSelector = this.block.childBlocks.language.widget.input;
        this.registerMissingLanguages();
        this.configureBlockAdminForm();
        this.addEventListeners();
        this.previewActive = false;
        return this.block;
    };

    registerMissingLanguages() {
        // check registered languages against those in language choice block, add script for each missing one
        let errors = [];
        const availableLanguages = hljs.listLanguages();
        const optionValues = Array.from(this.languageSelector.options).map(option => option.value);
        const missing_languages = optionValues.filter(optionValue => !availableLanguages.includes(optionValue));
        if (missing_languages) {
            // if scripts fail to load, write simple message to block form and error message with path to console
            const scriptPromises = missing_languages.map(language => {
                return new Promise((resolve, reject) => {
                    const script = document.createElement('script');
                    script.src = `${this.meta.language_base_path}${language}.min.js`;
                    script.onload = () => {
                        resolve();
                    };
                    script.onerror = () => {
                        const displayError = `${this.meta.text.languageScriptErrorLabel}: ${language}`;
                        const consoleError = `${displayError} (${script.src})`;
                        errors.push([displayError, consoleError]);
                        reject(new Error(consoleError));
                    };
                    document.head.appendChild(script);
                });
            });
            // When all scripts are either loaded or failed, report any errors
            Promise.allSettled(scriptPromises).then(() => {
                if (errors.length > 0) {
                    // displayError
                    this.highlighterErrors.innerText = errors.map(error => error[0]).join('\n');
                    // consoleError
                    errors.forEach(error => console.error(error[1]));
                }
            });
        }
    }

    configureBlockAdminForm() {
        // hide rawHTMLBlock textarea widget
        this.codeTextarea.style.setProperty('display', 'none');

        // create code editor textarea
        this.codeEditor = document.createElement('textarea');
        this.codeEditor.dataset.controller = "w-autosize";
        this.codeEditor.className = "w-field__autosize";
        this.codeEditor.setAttribute('spellcheck', 'false');
        this.codeTextarea.after(this.codeEditor);
        // set initial value from code innerText (extracts raw code from highlighted html)
        if (this.codeTextarea.value) {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = this.codeTextarea.value;
            this.codeEditor.value = tempDiv.innerText;
        }

        // create preview container, insert after textarea
        this.preview = document.createElement('div');
        this.preview.className = "code-block-preview";
        this.codeTextarea.after(this.preview);

        // create write/preview tabs, insert before textarea
        this.tabs = document.createElement('div');
        this.tabs.className = "code-block-tabs"
        this.writeTab = document.createElement('label');
        this.writeTab.className = "w-field__label code-block-tab active";
        this.writeTab.innerText = "Write"
        this.tabs.appendChild(this.writeTab);
        this.previewTab = document.createElement('label');
        this.previewTab.className = "w-field__label code-block-tab";
        this.previewTab.innerText = "Preview"
        this.tabs.appendChild(this.previewTab);
        this.codeTextarea.before(this.tabs);

        // placeholder for displaying any highlighter errors
        this.highlighterErrors = document.createElement('div');
        this.highlighterErrors.className = "code-block-highlighter-errors"
        this.block.childBlocks.code.field.firstElementChild.before(this.highlighterErrors);
    }

    addEventListeners() {
        // code editor content changed - convert entered code to highlighted markup
        this.codeEditor.addEventListener('input', () => this.getHighlightCodeHTML());
        // tab clicks - show/hide the preview pane
        this.writeTab.addEventListener('click', () => this.showPreview(false));
        this.previewTab.addEventListener('click', () => this.showPreview(true));
        // language changed - convert entered code with new language setting
        this.languageSelector.addEventListener('change', () => {
            this.getHighlightCodeHTML();
            if (this.previewActive) this.updatePreview();
        });
    }

    getHighlightCodeHTML() {
        this.highlighterErrors.innerText = '';
        // parse entered code with hljs, set this as the code child block value
        let parsedCode = {};
        try {
            parsedCode = hljs.highlight(this.codeEditor.value, { language: this.languageSelector.value, ignoreIllegals: 'true' });
        } catch (error) {
            // on error, plain text used, error displayed above tabs
            parsedCode.value = this.codeEditor.value;
            const errMessage = `${this.meta.text.highlighterErrorLabel}: ${error.message}`;
            console.error(errMessage);
            this.highlighterErrors.innerText = errMessage;
        }
        // wrap parsedCode value with <pre><code> tags - hljs class used by theme css, language class added for highlightjs consistency
        // if no parsedCode, return empty string so code child block required=true is enforced on page save
        this.codeTextarea.value = parsedCode.value 
            ? `<pre><code class="language-${this.languageSelector.value} hljs">${parsedCode.value}</code></pre>` 
            : '';
    }

    updatePreview() {
        // set the preview panel inner html from the code child block value
        this.preview.innerHTML = this.codeTextarea.value;
    }

    showPreview(active) {
        // set css classes to show/hide the preview panel, update tabs
        if (active === true) this.updatePreview();
        this.codeTextarea.parentElement.classList.toggle('preview-active', active);
        this.writeTab.classList.toggle('active', !active);
        this.previewTab.classList.toggle('active', active);
        this.previewActive = active;
    }
}

window.telepath.register('blocks.code.BlogCodeBlock', CodeBlockDefinition);
