const processDjangoCodeBlock = (element) => {
    const content = element.innerHTML;

    // Step 1: Insert whitespace after "{%" and "{{" if the next character is not whitespace
    const step1Content = content.replace(/({%)(?!\s)/g, "$1 ")
        .replace(/({{)(?!\s)/g, "$1 ");

    // Step 2: Insert whitespace before "%}" and "}}" if the previous character is not whitespace
    const step2Content = step1Content.replace(/(?<!\s)(%})/g, " $1")
        .replace(/(?<!\s)(}})/g, " $1");

    // Update the inner HTML of the element with the processed content
    element.innerHTML = step2Content;
};
