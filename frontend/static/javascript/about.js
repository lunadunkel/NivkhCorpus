const lang = window.location.pathname.split("/")[1];

document.querySelectorAll('a[href*="{lang}"]').forEach(link => {
    const href = link.getAttribute("href");
    link.setAttribute("href", href.replace("{lang}", lang));
});


// function scrollToElement(id) {
//     const newId = id + '-element';
//     const element = document.getElementById(newId);
//     element.scrollIntoView();
// }

// document.addEventListener("DOMContentLoaded", function () {
//     const parent = document.querySelector('ol')
//     parent.querySelectorAll(":scope > li").forEach(item => {
//         item.addEventListener("click", scrollToElement(item.id))
//     })

    
//     // document.getElementById("use-corpus").addEventListener()
//     // parentFrame.appendChild(frame);
//     // document.getElementById("closure-0").style.display = "none";

// });

