/* ==========================================================================
   ryan-sandell.com — site script
   --------------------------------------------------------------------------
   This file does exactly one thing: open and close the navigation menu on
   narrow screens. Everything else on the site is plain HTML and CSS.

   If you delete this file the site still works — the menu just stays open
   on phones instead of collapsing.
   ========================================================================== */

(function () {
	"use strict";

	var toggle = document.querySelector(".nav-toggle");
	var nav    = document.querySelector(".nav");

	if (!toggle || !nav) {
		return;                                  // page has no nav; nothing to do
	}

	/* Open or close the menu, keeping the button's ARIA state in sync so that
	   screen readers announce it correctly. */
	function setOpen(open) {
		nav.setAttribute("data-open", open ? "true" : "false");
		toggle.setAttribute("aria-expanded", open ? "true" : "false");
		toggle.textContent = open ? "Close" : "Menu";
	}

	setOpen(false);

	toggle.addEventListener("click", function () {
		setOpen(nav.getAttribute("data-open") !== "true");
	});

	/* Escape closes the menu and returns focus to the button. */
	document.addEventListener("keydown", function (event) {
		if (event.key === "Escape" && nav.getAttribute("data-open") === "true") {
			setOpen(false);
			toggle.focus();
		}
	});

	/* Following a link should not leave the menu hanging open behind the page. */
	nav.addEventListener("click", function (event) {
		if (event.target.closest("a")) {
			setOpen(false);
		}
	});

	/* If the window is widened past the phone breakpoint, drop the collapsed
	   state so the desktop layout is never left hidden. */
	var wide = window.matchMedia("(min-width: 761px)");
	(wide.addEventListener ? wide.addEventListener.bind(wide, "change") : wide.addListener.bind(wide))(function (e) {
		if (e.matches) { setOpen(false); }
	});
})();
