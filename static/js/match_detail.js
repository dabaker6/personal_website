(() => {
    const parseChartPayload = (container) => {
        const payloadNode = container.querySelector("[data-progression-chart-payload]");
        if (!(payloadNode instanceof HTMLScriptElement)) {
            return null;
        }

        try {
            const parsed = JSON.parse(payloadNode.textContent || "{}");
            return parsed && typeof parsed === "object" ? parsed : null;
        } catch {
            return null;
        }
    };

    const escapeHtml = (value) => String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");

    const renderProgressionChart = () => {
        const section = document.querySelector("[data-progression-chart-section]");
        if (!(section instanceof HTMLElement)) {
            return;
        }

        const chartHost = section.querySelector("[data-progression-chart]");
        if (!(chartHost instanceof HTMLElement)) {
            return;
        }

        const tooltip = section.querySelector("[data-progression-tooltip]");
        const wicketLayer = section.querySelector("[data-progression-wickets]");

        const payload = parseChartPayload(section);
        
        // Skip rendering if chart is not available
        if (payload?.availability !== "available") {
            return;
        }
        
        const series = Array.isArray(payload?.series) ? payload.series : [];
        const wickets = Array.isArray(payload?.wickets) ? payload.wickets : [];
        if (series.length === 0) {
            return;
        }

        const allPoints = series.flatMap((innings) => (Array.isArray(innings.points) ? innings.points : []));
        const maxOver = Math.max(1, ...allPoints.map((point) => Number(point.over) || 0));
        const maxRuns = Math.max(1, ...allPoints.map((point) => Number(point.cumulative_runs) || 0));

        const width = 820;
        const height = 380;
        const margin = { top: 16, right: 16, bottom: 44, left: 52 };
        const innerWidth = width - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;

        const xForOver = (over) => {
            if (maxOver <= 1) {
                return margin.left;
            }
            const clamped = Math.max(1, Math.min(maxOver, Number(over) || 1));
            return margin.left + ((clamped - 1) / (maxOver - 1)) * innerWidth;
        };

        const yForRuns = (runs) => {
            const clamped = Math.max(0, Math.min(maxRuns, Number(runs) || 0));
            return margin.top + (1 - clamped / maxRuns) * innerHeight;
        };

        const colors = ["#c4572b", "#0c5b63", "#8c3218", "#176f7a"];
        const runTicks = 4;
        const overTicks = Math.min(maxOver, 10);

        let svg = "";
        svg += `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Innings progression line chart">`;
        svg += `<line x1="${margin.left}" y1="${height - margin.bottom}" x2="${width - margin.right}" y2="${height - margin.bottom}" stroke="rgba(24,22,26,0.35)" />`;
        svg += `<line x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${height - margin.bottom}" stroke="rgba(24,22,26,0.35)" />`;

        for (let i = 0; i <= runTicks; i += 1) {
            const runs = Math.round((maxRuns / runTicks) * i);
            const y = yForRuns(runs);
            svg += `<line x1="${margin.left}" y1="${y}" x2="${width - margin.right}" y2="${y}" stroke="rgba(24,22,26,0.08)" />`;
            svg += `<text x="${margin.left - 10}" y="${y + 4}" text-anchor="end" font-size="11" fill="#5d5960">${runs}</text>`;
        }

        for (let i = 0; i <= overTicks; i += 1) {
            const over = Math.max(1, Math.round((maxOver / overTicks) * i));
            const x = xForOver(over);
            svg += `<line x1="${x}" y1="${margin.top}" x2="${x}" y2="${height - margin.bottom}" stroke="rgba(24,22,26,0.06)" />`;
            svg += `<text x="${x}" y="${height - margin.bottom + 18}" text-anchor="middle" font-size="11" fill="#5d5960">${over}</text>`;
        }

        series.forEach((innings, idx) => {
            const points = Array.isArray(innings.points) ? innings.points : [];
            if (points.length === 0) {
                return;
            }

            const color = colors[idx % colors.length];
            const pathData = points
                .map((point, pointIndex) => {
                    const x = xForOver(point.over);
                    const y = yForRuns(point.cumulative_runs);
                    return `${pointIndex === 0 ? "M" : "L"}${x},${y}`;
                })
                .join(" ");

            svg += `<path d="${pathData}" fill="none" stroke="${color}" stroke-width="2.5" />`;

            points.forEach((point) => {
                const x = xForOver(point.over);
                const y = yForRuns(point.cumulative_runs);
                const team = String(innings.team || `Innings ${innings.innings_number || idx + 1}`);
                const over = Number(point.over) || 0;
                const runs = Number(point.cumulative_runs) || 0;
                svg += `<circle cx="${x}" cy="${y}" r="3" fill="${color}"><title>${team}: Over ${over}, ${runs} runs</title></circle>`;
            });
        });

        wickets.forEach((wicket) => {
            const over = Number(wicket.over) || 1;
            const runs = Number(wicket.cumulative_runs) || 0;
            const stackIndex = Math.max(1, Number(wicket.index_in_over) || 1);
            const x = xForOver(over) + (stackIndex - 1) * 7;
            const y = yForRuns(runs) - 8 - (stackIndex - 1) * 9;

            const team = escapeHtml(String(wicket.team || "Innings"));
            const batter = escapeHtml(String(wicket.batter || "Unknown batter"));
            const bowler = escapeHtml(String(wicket.bowler || "Unknown bowler"));
            const dismissalMethod = escapeHtml(String(wicket.dismissal_method || wicket.dismissal || "wicket"));

            svg += `<circle class="progression-wicket-marker" data-wicket-marker data-team="${team}" data-over="${over}" data-runs="${runs}" data-batter="${batter}" data-bowler="${bowler}" data-dismissal="${dismissalMethod}" cx="${x}" cy="${y}" r="4" fill="#111" stroke="#fff" stroke-width="1.2" tabindex="0" role="button" aria-label="Wicket: ${team} over ${over}, ${batter} ${dismissalMethod}"></circle>`;
        });

        svg += `<text x="${width / 2}" y="${height - 8}" text-anchor="middle" font-size="12" fill="#5d5960">Overs</text>`;
        svg += `<text x="16" y="${height / 2}" text-anchor="middle" font-size="12" fill="#5d5960" transform="rotate(-90 16 ${height / 2})">Cumulative runs</text>`;
        svg += "</svg>";

        chartHost.innerHTML = svg;

        if (wicketLayer instanceof HTMLElement) {
            if (wickets.length > 0) {
                wicketLayer.hidden = false;
                wicketLayer.textContent = `${wickets.length} wicket marker${wickets.length === 1 ? "" : "s"} plotted.`;
            } else {
                wicketLayer.hidden = true;
                wicketLayer.textContent = "";
            }
        }

        if (!(tooltip instanceof HTMLElement)) {
            return;
        }

        const markers = Array.from(chartHost.querySelectorAll("[data-wicket-marker]"));
        if (markers.length === 0) {
            tooltip.hidden = true;
            return;
        }

        const hideTooltip = () => {
            tooltip.hidden = true;
            tooltip.textContent = "";
        };

        const showTooltip = (target) => {
            if (!(target instanceof SVGElement)) {
                return;
            }

            const team = target.getAttribute("data-team") || "Innings";
            const over = target.getAttribute("data-over") || "-";
            const runs = target.getAttribute("data-runs") || "-";
            const batter = target.getAttribute("data-batter") || "Unknown batter";
            const bowler = target.getAttribute("data-bowler") || "Unknown bowler";
            const dismissal = target.getAttribute("data-dismissal") || "wicket";

            tooltip.innerHTML = `<strong>${team}</strong><br>Over ${over} (${runs})<br>${batter} • ${dismissal}<br>Bowler: ${bowler}`;
            tooltip.hidden = false;

            const chartRect = chartHost.getBoundingClientRect();
            const markerRect = target.getBoundingClientRect();
            const offsetLeft = markerRect.left - chartRect.left + chartHost.scrollLeft;
            const offsetTop = markerRect.top - chartRect.top;
            tooltip.style.position = "absolute";
            tooltip.style.left = `${Math.max(8, offsetLeft + 10)}px`;
            tooltip.style.top = `${Math.max(8, offsetTop - 52)}px`;
        };

        markers.forEach((marker) => {
            marker.addEventListener("mouseenter", (event) => showTooltip(event.currentTarget));
            marker.addEventListener("focus", (event) => showTooltip(event.currentTarget));
            marker.addEventListener("mouseleave", hideTooltip);
            marker.addEventListener("blur", hideTooltip);
            marker.addEventListener("keydown", (event) => {
                if (event.key === "Escape") {
                    hideTooltip();
                }
            });
        });
    };

    const containers = Array.from(document.querySelectorAll("[data-scorecard-tabs]"));
    if (containers.length === 0) {
        renderProgressionChart();
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

    renderProgressionChart();
})();
