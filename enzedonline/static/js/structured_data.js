const wordCount = (element) => {
    return element.innerText.split(/\s/).length
}

// find a json node from a path described as array, i.e. ['firstLevelNode', 'secondLevelNode'] etc. 
const findJsonNodeFromArray = (scriptNode, array) => {
    node = scriptNode[array.shift()];
    if (array.length){
        findJsonNodeFromArray(node, array);
    }
    return node;
}

// write to a json node from a path described as array, i.e. ['firstLevelNode', 'secondLevelNode'] etc. 
const writeJsonNodeFromArray = (scriptNode, array, value) => {
    key = array.shift();
    node = null;
    if (array.length){
        if (!scriptNode[key]) {
            scriptNode[key] = {};
        }
        node = writeJsonNodeFromArray(scriptNode[key], array, value);
        return node;
    } else {
        scriptNode[key] = value; 
        return scriptNode[key];
    }
}

// describe the json Node Path as an array, i.e. ['firstLevelNode', 'secondLevelNode'] etc.
const addDocWordCount = (countElementID, scriptID, jsonPathAsArray) => {
    const countElement = document.getElementById(countElementID)
    if (!countElement) {
        console.error(`addDocWordCount: Element to count with id '${countElementID}' not found`);
        return;
    }
    const script = document.getElementById(scriptID);
    if (!script) {
        console.error(`addDocWordCount: Structured data script with id '${scriptID}' not found`);
        return;
    }
    structuredData = JSON.parse(script.firstChild.nodeValue);
    writeJsonNodeFromArray(structuredData, jsonPathAsArray, `${wordCount(countElement)}`);
    script.firstChild.nodeValue = JSON.stringify(structuredData);
}