(() => {
    const visibleInput = document.getElementById("date-range-input");
    const fromInput = document.querySelector('input[name="fromDate"]');
    const toInput = document.querySelector('input[name="toDate"]');

    if (!visibleInput || !fromInput || !toInput || typeof flatpickr !== "function") {
        return;
    }

    const initialDates = [fromInput.value, toInput.value].filter(Boolean);

    flatpickr(visibleInput, {
        mode: "range",
        dateFormat: "Y-m-d",
        defaultDate: initialDates.length > 0 ? initialDates : undefined,
        onChange: (selectedDates, dateStr) => {
            const parts = dateStr.split(" to ");
            fromInput.value = parts[0] || "";
            toInput.value = parts[1] || "";
        },
    });
})();
