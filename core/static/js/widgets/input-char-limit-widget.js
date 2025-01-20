// js/widgets/import-textInput-widget.js
class InputCharLimitWidget {
    /**
     * @param {string} id - The ID of the text input element.
     * @param {number} min - The minimum character limit.
     * @param {number} max - The maximum character limit (null for no limit).
     * @param {boolean} enforced - Whether the character limit is enforced.
     */
    constructor(id, min = 0, max = Infinity, enforced = true) {
        this.min = min;
        this.max = max;
        this.textInput = document.getElementById(id);
        this.feedbackLabel = this.textInput.parentElement.querySelector(`div#${id}-feedback-label`);
        this.charCount = this.feedbackLabel.querySelector('span[data-used-chars]');
        this.warningIcon = this.feedbackLabel.querySelector('svg');
        this.passColor = 'var(--w-color-text-label)';
        if (enforced) {
            this.failColor = 'var(--w-color-text-error)';
        } else {
            this.failColor = 'var(--w-color-warning-100)';
        }

        this.renderFeedback();
        this.textInput.addEventListener('input', this.handleInput.bind(this));
    };
    
    handleInput() {
        this.renderFeedback();
    }

    renderFeedback() {
        // Update character count
        const textLength = this.textInput.value.length;
        this.charCount.textContent = textLength;
        // Validate text length
        const isValidLength = textLength >= this.min && textLength <= this.max;
        if (!isValidLength) {
            this.textInput.style.borderColor = this.failColor;
            this.feedbackLabel.style.color = this.failColor;
            this.warningIcon.style.display = 'inline';
        } else {
            this.textInput.style.borderColor = ''; // Reset to default
            this.feedbackLabel.style.color = this.passColor;
            this.warningIcon.style.display = 'none';
        }
    }
}
