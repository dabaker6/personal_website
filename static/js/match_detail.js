(() => {
    const containers = Array.from(document.querySelectorAll("[data-scorecard-tabs]"));
    if (containers.length === 0) {
        return;
    }

    const activateTab = (tabs, panels, nextIndex) => {
        tabs.forEach((tab, index) => {
            const active = index === nextIndex;
            tab.classList.toggle("is-active", active);
            tab.setAttribute("aria-selected", active ? "true" : "false");
            tab.setAttribute("tabindex", active ? "0" : "-1");
            if (panels[index]) {
                panels[index].hidden = !active;
            }
        });
        tabs[nextIndex]?.focus();
    };

    containers.forEach((container) => {
        const tabs = Array.from(container.querySelectorAll('[role="tab"]'));
        const panels = tabs.map((tab) => {
            const id = tab.getAttribute("aria-controls");
            return id ? container.querySelector(`#${id}`) : null;
        });

        if (tabs.length === 0) {
            return;
        }

        container.addEventListener("click", (event) => {
            const target = event.target;
            if (!(target instanceof HTMLButtonElement) || target.getAttribute("role") !== "tab") {
                return;
            }
            const index = tabs.indexOf(target);
            if (index >= 0) {
                activateTab(tabs, panels, index);
            }
        });

        container.addEventListener("keydown", (event) => {
            const target = event.target;
            if (!(target instanceof HTMLButtonElement) || target.getAttribute("role") !== "tab") {
                return;
            }

            const currentIndex = tabs.indexOf(target);
            if (currentIndex < 0) {
                return;
            }

            let nextIndex = currentIndex;
            if (event.key === "ArrowRight") {
                nextIndex = (currentIndex + 1) % tabs.length;
            } else if (event.key === "ArrowLeft") {
                nextIndex = (currentIndex - 1 + tabs.length) % tabs.length;
            } else if (event.key === "Home") {
                nextIndex = 0;
            } else if (event.key === "End") {
                nextIndex = tabs.length - 1;
            } else {
                return;
            }

            event.preventDefault();
            activateTab(tabs, panels, nextIndex);
        });
    });
})();
