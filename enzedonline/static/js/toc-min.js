let listContents=(e,t="body",n=3,o=!1)=>{let l,c;if(l=document.getElementById(e),l&&"DIV"!==l.tagName&&(l=null),c=document.getElementsByTagName(t)[0],c||(c=document.getElementById(t)),c&&l){const e=["h2","h3","h4","h5","h6"].slice(0,n).join(),t=c.querySelectorAll(e);if(t.length>0){if(o){let e=l.appendChild(document.createElement("H2"));e.innerText=o,e.classList.add("toc","toc-title")}const e=l.appendChild(document.createElement("UL"));e.classList.add("toc","toc-list"),e.setAttribute("role","list");for(let n=0;n<t.length;n++){const o=Number(t[n].nodeName[1])-1;t[n].id||(t[n].id=`${n+1}-${slugify(t[n].innerText)}`);const l=e.appendChild(document.createElement("LI"));l.classList.add("toc",`toc-item-l${o}`);const c=l.appendChild(document.createElement("A"));c.appendChild(document.createTextNode(t[n].innerText)),c.href=`#${t[n].id}`}}}},slugify=e=>{e=(e=e.replace(/^\s+|\s+$/g,"")).toLowerCase();for(var t="ÁÄÂÀÃÅČÇĆĎÉĚËÈÊẼĔȆÍÌÎÏŇÑÓÖÒÔÕØŘŔŠŤÚŮÜÙÛÝŸŽáäâàãåčçćďéěëèêẽĕȇíìîïňñóöòôõøðřŕšťúůüùûýÿžþÞĐđßÆa·/_,:;",n=0,o=t.length;n<o;n++)e=e.replace(new RegExp(t.charAt(n),"g"),"AAAAAACCCDEEEEEEEEIIIINNOOOOOORRSTUUUUUYYZaaaaaacccdeeeeeeeeiiiinnooooooorrstuuuuuyyzbBDdBAa------".charAt(n));return e=e.replace(/[^a-z0-9 -]/g,"").replace(/\s+/g,"-").replace(/-+/g,"-")};$(document).ready((function(){const e=JSON.parse(document.getElementById("tocElement").textContent),t=JSON.parse(document.getElementById("scopeElement").textContent),n=JSON.parse(document.getElementById("levels").textContent),o=JSON.parse(document.getElementById("tocTitle").textContent);listContents(e,t,n,o)}));