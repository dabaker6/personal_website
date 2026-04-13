(function () {
    const header = document.querySelector("[data-mobile-nav]");
    if (!header) {
        return;
    }

    const toggleButton = header.querySelector("[data-nav-toggle]");
    const navMenu = header.querySelector("[data-nav-menu]");
    if (!toggleButton || !navMenu) {
        return;
    }

    const setExpandedState = function (isOpen) {
        header.setAttribute("data-nav-open", isOpen ? "true" : "false");
        toggleButton.setAttribute("aria-expanded", isOpen ? "true" : "false");
    };

    const closeMenu = function () {
        setExpandedState(false);
    };

    header.setAttribute("data-nav-ready", "true");
    setExpandedState(false);

    toggleButton.addEventListener("click", function () {
        const isExpanded = toggleButton.getAttribute("aria-expanded") === "true";
        setExpandedState(!isExpanded);
    });

    navMenu.addEventListener("click", function (event) {
        const target = event.target;
        if (target instanceof Element && target.closest("a")) {
            closeMenu();
        }
    });

    document.addEventListener("click", function (event) {
        if (toggleButton.getAttribute("aria-expanded") !== "true") {
            return;
        }
        if (!header.contains(event.target)) {
            closeMenu();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeMenu();
        }
    });

    const desktopMedia = window.matchMedia("(min-width: 861px)");
    const syncForViewport = function () {
        if (desktopMedia.matches) {
            closeMenu();
        }
    };

    if (desktopMedia.addEventListener) {
        desktopMedia.addEventListener("change", syncForViewport);
    } else {
        desktopMedia.addListener(syncForViewport);
    }
})();
