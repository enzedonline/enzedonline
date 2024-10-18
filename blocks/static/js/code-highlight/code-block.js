const copyCodeToClipboard = (event, id, buttonText) => {
    try {
        const copyText = document.getElementById(id);
        navigator.clipboard.writeText(copyText.innerText);
        event.target.innerText = `${buttonText.copied} ✓`;
        event.target.classList.add('copied-to-clipboard');
        setTimeout(() => {
            event.target.innerText = buttonText.copy;
            event.target.classList.remove('copied-to-clipboard');
        }, 2000);
    } catch (error) {
        event.target.innerText = buttonText.error;
        console.error('Error copying the code to clipboard:', error);
    }
}
