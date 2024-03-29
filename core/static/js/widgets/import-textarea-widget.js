// js/widgets/import-textarea-widget.js

class ImportTextAreaWidget {
    constructor(id) {
        this.textArea = document.getElementById(id);
        this.textArea.classList.add('import-textarea')
        this.fileInput = this.textArea.parentElement.querySelector(`input#${id}-file-input`);
        // event listeners
        this.textArea.addEventListener('dragover', (event) => { this.handleDragOver(event); });
        this.textArea.addEventListener('drop', (event) => { this.handleDrop(event); });
        this.textArea.addEventListener('import', (event) => { this.handleImport(event); });
        this.fileInput.addEventListener('change', (event) => { this.handleFileInputChange(event); });
    }

    readFile(source, target) {
        const reader = new FileReader();
        reader.addEventListener('load', (event) => {
            target.value = event.target.result;
            this.textArea.dispatchEvent(new Event('input'));
            this.textArea.dispatchEvent(new Event('import'));
        });
        reader.readAsText(source);
    }

    handleFileInputChange(event) {
        event.preventDefault();
        const input = this.fileInput.files[0];
        this.readFile(input, this.textArea);
        this.fileInput.value = '';
        this.fileInput.blur();
    }

    handleDragOver(event) {
        event.stopPropagation();
        event.preventDefault();
        event.dataTransfer.dropEffect = 'copy';
    }

    handleDrop(event) {
        event.stopPropagation();
        event.preventDefault();
        const input = event.dataTransfer.files[0];
        this.readFile(input, this.textArea);
        console.log(event.dataTransfer.files[0])
    }

    isElementInViewport(element) {
        const rect = element.getBoundingClientRect();
        return rect.top >= 50 && rect.top < window.innerHeight;
    };

    handleImport(event) {
        if (!this.isElementInViewport(this.textArea)) {
            setTimeout(() => {
                this.textArea.scrollIntoView({ behavior: "smooth" });
            }, 200);
        }
    }
}
