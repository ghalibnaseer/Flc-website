/* FLC & Associates LLP: small enhancements. The site works fully without this file. */
(function () {
  var d = document;

  /* Phone menu */
  var btn = d.querySelector(".menu-btn"), nav = d.getElementById("site-nav");
  if (btn && nav) {
    var setOpen = function (open) {
      nav.classList.toggle("open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    };
    btn.addEventListener("click", function () { setOpen(!nav.classList.contains("open")); });
    d.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("open")) { setOpen(false); btn.focus(); }
    });
    d.addEventListener("click", function (e) {
      if (nav.classList.contains("open") && !nav.contains(e.target) && !btn.contains(e.target)) setOpen(false);
    });
  }

  /* Long lists of names: on phones show the first ten, with a button for the rest */
  var lists = d.querySelectorAll(".names");
  for (var i = 0; i < lists.length; i++) {
    (function (ul) {
      var n = ul.children.length;
      if (n <= 12) return;
      var more = d.createElement("button");
      more.type = "button";
      more.className = "names-more";
      more.textContent = "Show all " + n;
      more.addEventListener("click", function () { ul.classList.remove("collapsed"); more.remove(); });
      ul.classList.add("collapsed");
      ul.parentNode.insertBefore(more, ul.nextSibling);
    })(lists[i]);
  }

  /* Sections fade in as they come into view */
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!reduce && "IntersectionObserver" in window) {
    var blocks = d.querySelectorAll("main > section:not(:first-child) > .wrap, .contact > .wrap");
    var io = new IntersectionObserver(function (entries) {
      for (var j = 0; j < entries.length; j++) {
        if (entries[j].isIntersecting) { entries[j].target.classList.add("in"); io.unobserve(entries[j].target); }
      }
    }, { rootMargin: "0px 0px -6% 0px" });
    for (var k = 0; k < blocks.length; k++) { blocks[k].classList.add("reveal"); io.observe(blocks[k]); }
  }
})();
