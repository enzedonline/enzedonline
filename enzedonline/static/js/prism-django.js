// Insert whitespace after "{%" and "{{" if the next character is not whitespace
// Insert whitespace before "%}" and "}}" if the previous character is not whitespace

const processDjangoCodeBlock = (blockId) => {
    const element = document.getElementById(`code-block-${blockId}`);
    element.innerHTML = content
        .replace(/({%)(?!\s)/g, "$1 ")
        .replace(/({{)(?!\s)/g, "$1 ")
        .replace(/(?<!\s)(%})/g, " $1")
        .replace(/(?<!\s)(}})/g, " $1");
};

