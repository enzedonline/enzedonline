$(document).ready(function(){
    const script = document.getElementById("thisArticle");
    const article = JSON.parse(script.firstChild.nodeValue);
    article["wordCount"] =`${document.getElementsByTagName('main')[0].innerText.split(/\s/).length}`;
    script.firstChild.nodeValue = JSON.stringify(article);
});