(() => {
    const searchInput = document.getElementById("updates-search");
    const tagControls = document.querySelector('[data-role="tag-controls"]');
    const sortControls = document.querySelector('[data-role="sort-controls"]');
    const emptyFilterState = document.querySelector('[data-role="empty-filter"]');
    const entries = Array.from(document.querySelectorAll("article[data-search-text]"));

    if (!searchInput || !tagControls || entries.length === 0) {
        return;
    }

    const cardGrid = entries[0].parentElement;
    const tagButtons = Array.from(tagControls.querySelectorAll("button[data-tag]"));
    const sortButtons = sortControls
        ? Array.from(sortControls.querySelectorAll("button[data-sort]"))
        : [];

    let activeTag = "all";
    let activeSort = "newest";

    const normalize = (value) => String(value || "").trim().toLowerCase();

    const setActiveTag = (tag) => {
        activeTag = normalize(tag) || "all";
        tagButtons.forEach((button) => {
            button.setAttribute(
                "aria-pressed",
                normalize(button.dataset.tag) === activeTag ? "true" : "false"
            );
        });
    };

    const setActiveSort = (sort) => {
        activeSort = sort === "oldest" ? "oldest" : "newest";
        sortButtons.forEach((button) => {
            button.setAttribute(
                "aria-pressed",
                button.dataset.sort === activeSort ? "true" : "false"
            );
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

        // Re-order entries in the grid by date. appendChild moves existing
        // children so no clone is needed; hidden entries stay hidden.
        const sorted = entries.slice().sort((a, b) => {
            const da = a.dataset.date || "";
            const db = b.dataset.date || "";
            return activeSort === "oldest"
                ? da < db ? -1 : da > db ? 1 : 0
                : da > db ? -1 : da < db ? 1 : 0;
        });
        sorted.forEach((entry) => cardGrid.appendChild(entry));

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

    if (sortControls) {
        sortControls.addEventListener("click", (event) => {
            const target = event.target;
            if (!(target instanceof HTMLButtonElement)) {
                return;
            }
            const selectedSort = target.dataset.sort;
            if (!selectedSort) {
                return;
            }
            setActiveSort(selectedSort);
            applyFilters();
        });
    }

    setActiveTag("all");
    setActiveSort("newest");
    applyFilters();

    // Pre-select a tag when arriving via a tag link (e.g. from the detail page).
    const initialTag = new URLSearchParams(location.search).get("tag");
    if (initialTag) {
        setActiveTag(initialTag);
        applyFilters();
    }
})();
