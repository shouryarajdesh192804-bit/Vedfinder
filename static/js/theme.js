// =========================================
// VedFinder V3
// theme.js
// =========================================

document.addEventListener("DOMContentLoaded", () => {

    initializeTheme();

});


// =========================================
// Initialize Theme
// =========================================

function initializeTheme() {

    const button = document.getElementById("themeBtn");

    loadTheme();

    if (!button) return;

    button.addEventListener(

        "click",

        toggleTheme

    );

}


// =========================================
// Toggle Theme
// =========================================

function toggleTheme() {

    document.body.classList.toggle(

        "dark"

    );

    const theme = document.body.classList.contains(

        "dark"

    )

        ? "dark"

        : "light";

    localStorage.setItem(

        "theme",

        theme

    );

    updateButton();

}


// =========================================
// Load Theme
// =========================================

function loadTheme() {

    let theme = localStorage.getItem(

        "theme"

    );

    if (!theme) {

        theme = window.matchMedia(

            "(prefers-color-scheme: dark)"

        ).matches

            ? "dark"

            : "light";

    }

    if (theme === "dark") {

        document.body.classList.add(

            "dark"

        );

    }

    else {

        document.body.classList.remove(

            "dark"

        );

    }

    updateButton();

}


// =========================================
// Theme Button
// =========================================

function updateButton() {

    const button = document.getElementById(

        "themeBtn"

    );

    if (!button) return;

    if (

        document.body.classList.contains(

            "dark"

        )

    ) {

        button.innerHTML = "☀️";

        button.title =

            "Switch to Light Mode";

    }

    else {

        button.innerHTML = "🌙";

        button.title =

            "Switch to Dark Mode";

    }

}


// =========================================
// System Theme Change
// =========================================

window.matchMedia(

    "(prefers-color-scheme: dark)"

).addEventListener(

    "change",

    () => {

        if (

            !localStorage.getItem(

                "theme"

            )

        ) {

            loadTheme();

        }

    }

);