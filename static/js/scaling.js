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
            // T010: chart rendering implemented here
        }

        function handleZeroReplicas(replicaCount) {
            // T011: zero-replica timeout logic implemented here
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
