(function () {
    document.addEventListener("DOMContentLoaded", function () {
        var container = document.querySelector(".dashboard-container");
        if (!container) return;

        var config = {
            pollingIntervalMs: parseInt(container.dataset.pollingIntervalMs, 10),
            maxMonitoringSeconds: parseInt(container.dataset.maxMonitoringSeconds, 10),
            zeroReplicaTimeoutSeconds: parseInt(container.dataset.zeroReplicaTimeoutSeconds, 10),
            minMessages: parseInt(container.dataset.minMessages, 10),
            maxMessages: parseInt(container.dataset.maxMessages, 10),
        };

        var form = container.querySelector("[data-send-form]");
        var countInput = container.querySelector("[data-count-input]");
        var sendButton = container.querySelector("[data-send-button]");
        var inlineError = container.querySelector("[data-inline-error]");
        var statusMessage = container.querySelector("[data-status-message]");
        var chartSection = container.querySelector("[data-chart-section]");

        if (!form || !countInput || !sendButton || !inlineError || !statusMessage || !chartSection) return;

        var readings = [];
        var monitoringStart = null;
        var pollTimer = null;
        var zeroReplicaTimer = null;

        function showInlineError(message) {
            inlineError.textContent = message;
            inlineError.hidden = false;
        }

        function clearInlineError() {
            inlineError.textContent = "";
            inlineError.hidden = true;
        }

        function showStatus(message) {
            statusMessage.textContent = message;
            statusMessage.hidden = false;
        }

        function stopPolling() {
            if (pollTimer !== null) {
                clearInterval(pollTimer);
                pollTimer = null;
            }
            if (zeroReplicaTimer !== null) {
                clearTimeout(zeroReplicaTimer);
                zeroReplicaTimer = null;
            }
        }

        function updateReplicaCount(value) {
            var panel = container.querySelector("[data-replica-count]");
            if (!panel) return;
            var valueEl = panel.querySelector(".metric-value");
            if (valueEl) valueEl.textContent = value;
        }

        function renderChart(currentReadings) {
            if (!currentReadings || currentReadings.length === 0) return;

            var svgNS = "http://www.w3.org/2000/svg";
            var W = 500, H = 200;
            var padLeft = 50, padRight = 16, padTop = 12, padBottom = 36;
            var plotW = W - padLeft - padRight;
            var plotH = H - padTop - padBottom;

            var maxX = currentReadings[currentReadings.length - 1].elapsed_ms / 1000;
            if (maxX < 1) maxX = 1;
            var maxY = 0;
            for (var i = 0; i < currentReadings.length; i++) {
                if (currentReadings[i].queue_length > maxY) maxY = currentReadings[i].queue_length;
            }
            if (maxY < 1) maxY = 1;

            function toSvgX(sec) { return padLeft + (sec / maxX) * plotW; }
            function toSvgY(q) { return padTop + plotH - (q / maxY) * plotH; }

            var svg = chartSection.querySelector("svg");
            if (!svg) {
                svg = document.createElementNS(svgNS, "svg");
                svg.setAttribute("viewBox", "0 0 " + W + " " + H);
                svg.setAttribute("class", "chart-svg");
                chartSection.appendChild(svg);
            } else {
                while (svg.firstChild) svg.removeChild(svg.firstChild);
            }

            var axes = document.createElementNS(svgNS, "polyline");
            axes.setAttribute("points",
                padLeft + "," + padTop + " " +
                padLeft + "," + (padTop + plotH) + " " +
                (padLeft + plotW) + "," + (padTop + plotH)
            );
            axes.setAttribute("class", "chart-axis");
            svg.appendChild(axes);

            var yLabel = document.createElementNS(svgNS, "text");
            yLabel.setAttribute("x", padLeft - 4);
            yLabel.setAttribute("y", padTop + 4);
            yLabel.setAttribute("class", "chart-label");
            yLabel.setAttribute("text-anchor", "end");
            yLabel.textContent = maxY;
            svg.appendChild(yLabel);

            var xOrigin = document.createElementNS(svgNS, "text");
            xOrigin.setAttribute("x", padLeft);
            xOrigin.setAttribute("y", padTop + plotH + 20);
            xOrigin.setAttribute("class", "chart-label");
            xOrigin.setAttribute("text-anchor", "middle");
            xOrigin.textContent = "0s";
            svg.appendChild(xOrigin);

            var xLabel = document.createElementNS(svgNS, "text");
            xLabel.setAttribute("x", padLeft + plotW);
            xLabel.setAttribute("y", padTop + plotH + 20);
            xLabel.setAttribute("class", "chart-label");
            xLabel.setAttribute("text-anchor", "end");
            xLabel.textContent = Math.round(maxX) + "s";
            svg.appendChild(xLabel);

            if (currentReadings.length === 1) {
                var r = currentReadings[0];
                var dot = document.createElementNS(svgNS, "circle");
                dot.setAttribute("cx", toSvgX(r.elapsed_ms / 1000));
                dot.setAttribute("cy", toSvgY(r.queue_length));
                dot.setAttribute("r", 4);
                dot.setAttribute("class", "chart-point");
                svg.appendChild(dot);
            } else {
                var pts = [];
                for (var j = 0; j < currentReadings.length; j++) {
                    pts.push(toSvgX(currentReadings[j].elapsed_ms / 1000) + "," + toSvgY(currentReadings[j].queue_length));
                }
                var line = document.createElementNS(svgNS, "polyline");
                line.setAttribute("points", pts.join(" "));
                line.setAttribute("class", "chart-line");
                svg.appendChild(line);

                for (var k = 0; k < currentReadings.length; k++) {
                    var pt = document.createElementNS(svgNS, "circle");
                    pt.setAttribute("cx", toSvgX(currentReadings[k].elapsed_ms / 1000));
                    pt.setAttribute("cy", toSvgY(currentReadings[k].queue_length));
                    pt.setAttribute("r", 3);
                    pt.setAttribute("class", "chart-point");
                    svg.appendChild(pt);
                }
            }
        }

        function handleZeroReplicas(replicaCount) {
            if (replicaCount === 0) {
                if (zeroReplicaTimer === null) {
                    zeroReplicaTimer = setTimeout(function () {
                        zeroReplicaTimer = null;
                        stopPolling();
                        showStatus("Replicas did not recover — scaling may have stalled.");
                    }, config.zeroReplicaTimeoutSeconds * 1000);
                }
            } else {
                if (zeroReplicaTimer !== null) {
                    clearTimeout(zeroReplicaTimer);
                    zeroReplicaTimer = null;
                }
            }
        }

        function pollStatus() {
            fetch("/scaling/api/status")
                .then(function (response) {
                    return response.json().then(function (data) {
                        return { status: response.status, data: data };
                    });
                })
                .then(function (result) {
                    if (result.status !== 200) {
                        stopPolling();
                        showStatus(
                            "Monitoring stopped — " +
                                (result.data.error || "an error occurred during monitoring.")
                        );
                        return;
                    }

                    var elapsed = Date.now() - monitoringStart;
                    var queueLength = result.data.queue_length;
                    var replicaCount = result.data.replica_count;

                    readings.push({ elapsed_ms: elapsed, queue_length: queueLength });
                    updateReplicaCount(replicaCount);
                    renderChart(readings);
                    handleZeroReplicas(replicaCount);

                    if (queueLength === 0) {
                        stopPolling();
                        showStatus("Queue cleared — scaling event complete.");
                        return;
                    }

                    if (elapsed >= config.maxMonitoringSeconds * 1000) {
                        stopPolling();
                        showStatus(
                            "Monitoring ended — maximum duration reached without the queue clearing."
                        );
                    }
                })
                .catch(function () {
                    stopPolling();
                    showStatus("Monitoring stopped — unable to reach the scaling service.");
                });
        }

        function beginPolling() {
            pollTimer = setInterval(pollStatus, config.pollingIntervalMs);
        }

        function startMonitoring() {
            monitoringStart = Date.now();
            readings = [];
            form.hidden = true;
            chartSection.hidden = false;
            showStatus("Messages sent — monitoring scaling activity.");
            beginPolling();
        }

        function validate(raw) {
            var count = parseInt(raw, 10);
            if (!raw || isNaN(count) || count !== Number(raw) || count < config.minMessages || count > config.maxMessages) {
                return null;
            }
            return count;
        }

        form.addEventListener("submit", function (event) {
            event.preventDefault();
            clearInlineError();

            var count = validate(countInput.value.trim());

            if (count === null) {
                showInlineError(
                    "Enter a whole number between " + config.minMessages + " and " + config.maxMessages + "."
                );
                return;
            }

            sendButton.disabled = true;

            fetch("/scaling/api/send", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ count: count }),
            })
                .then(function (response) {
                    return response.json().then(function (data) {
                        return { status: response.status, data: data };
                    });
                })
                .then(function (result) {
                    if (result.status === 202) {
                        startMonitoring();
                    } else if (result.status === 400) {
                        showInlineError(
                            result.data.error ||
                                "Invalid count. Enter a number between " +
                                    config.minMessages + " and " + config.maxMessages + "."
                        );
                        sendButton.disabled = false;
                    } else if (result.status === 429) {
                        var queueLen = result.data.queue_length;
                        var msg = "Queue still active";
                        if (typeof queueLen === "number") {
                            msg += ", " + queueLen + " message" + (queueLen !== 1 ? "s" : "") + " remaining";
                        }
                        showStatus(msg + ". Wait for the queue to clear before sending more messages.");
                        sendButton.disabled = false;
                    } else {
                        showStatus(
                            "Error: " + (result.data.error || "Something went wrong. Please try again.")
                        );
                        sendButton.disabled = false;
                    }
                })
                .catch(function () {
                    showStatus("Request failed. Check your connection and try again.");
                    sendButton.disabled = false;
                });
        });
    });
})();
