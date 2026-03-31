(() => {
    const searchInput = document.getElementById("updates-search");
    const tagControls = document.querySelector('[data-role="tag-controls"]');
    const emptyFilterState = document.querySelector('[data-role="empty-filter"]');
    const entries = Array.from(document.querySelectorAll("article[data-search-text]"));

    if (!searchInput || !tagControls || entries.length === 0) {
        return;
    }

    const tagButtons = Array.from(tagControls.querySelectorAll("button[data-tag]"));
    let activeTag = "all";

    const normalize = (value) => String(value || "").trim().toLowerCase();

    const setActiveTag = (tag) => {
        activeTag = normalize(tag) || "all";

        tagButtons.forEach((button) => {
            const buttonTag = normalize(button.dataset.tag);
            const isActive = buttonTag === activeTag;
            button.setAttribute("aria-pressed", isActive ? "true" : "false");
        });
    };

    const applyFilters = () => {
        const query = normalize(searchInput.value);
        let visibleCount = 0;

        entries.forEach((entry) => {
            const searchText = normalize(entry.dataset.searchText);
            const tagsText = normalize(entry.dataset.tags);
            const tags = tagsText ? tagsText.split(/\s+/) : [];

            const matchesQuery = !query || searchText.includes(query);
            const matchesTag = activeTag === "all" || tags.includes(activeTag);
            const isVisible = matchesQuery && matchesTag;

            entry.hidden = !isVisible;
            if (isVisible) {
                visibleCount += 1;
            }
        });

        if (emptyFilterState) {
            emptyFilterState.hidden = visibleCount !== 0;
        }
    };

    searchInput.addEventListener("input", applyFilters);

    tagControls.addEventListener("click", (event) => {
        const target = event.target;
        if (!(target instanceof HTMLButtonElement)) {
            return;
        }

        const selectedTag = normalize(target.dataset.tag);
        if (!selectedTag) {
            return;
        }

        // Clicking the currently active non-"all" tag clears the filter.
        if (selectedTag === activeTag && selectedTag !== "all") {
            setActiveTag("all");
        } else {
            setActiveTag(selectedTag);
        }

        applyFilters();
    });

    setActiveTag("all");
    applyFilters();
})();
