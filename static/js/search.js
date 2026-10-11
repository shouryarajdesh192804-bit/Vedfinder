// =========================================
// VedFinder V2
// search.js
// =========================================

document.addEventListener("DOMContentLoaded", () => {

    setupSearch();

    setupKeyboardShortcuts();

    restoreLastSearch();

});


// =========================================
// Search Validation
// =========================================

function setupSearch() {

    const form = document.querySelector(".search-box");

    const input = document.querySelector(
        'input[name="query"]'
    );

    if (!form || !input) return;

    form.addEventListener("submit", function (event) {

        const query = input.value.trim();

        if (query.length === 0) {

            event.preventDefault();

            alert("Please enter something to search.");

            input.focus();

            return;

        }

        if (

            document.getElementById("mode").value !== "go"

        ) {

            localStorage.setItem(

                "last_search",

                query

            );

            saveSearch(query);

        }

    });

}


// =========================================
// Search History
// =========================================

function saveSearch(query) {

    let history = JSON.parse(

        localStorage.getItem(

            "search_history"

        ) || "[]"

    );

    history = history.filter(item => item !== query);

    history.unshift(query);

    if (history.length > 10) {

        history = history.slice(0, 10);

    }

    localStorage.setItem(

        "search_history",

        JSON.stringify(history)

    );

}


// =========================================
// Restore Last Search
// =========================================

function restoreLastSearch() {

    const input = document.querySelector(

        'input[name="query"]'

    );

    if (!input) return;

    const last = localStorage.getItem(

        "last_search"

    );

    if (

        last &&

        input.value.trim() === ""

    ) {

        input.value = last;

    }

}


// =========================================
// Keyboard Shortcut
// Ctrl + K
// =========================================

function setupKeyboardShortcuts() {

    document.addEventListener(

        "keydown",

        function (event) {

            if (

                event.ctrlKey &&

                event.key.toLowerCase() === "k"

            ) {

                event.preventDefault();

                const input = document.querySelector(

                    'input[name="query"]'

                );

                if (input) {

                    input.focus();

                    input.select();

                }

            }

        }

    );

}


// =========================================
// Clear Search
// =========================================

function clearSearch() {

    const input = document.querySelector(

        'input[name="query"]'

    );

    if (!input) return;

    input.value = "";

    input.focus();

}