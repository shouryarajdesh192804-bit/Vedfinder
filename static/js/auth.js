// =========================================
// VedFinder V3
// auth.js
// =========================================

document.addEventListener("DOMContentLoaded", () => {

    initializeForms();

    initializePasswordToggle();

    initializeValidation();

});


// =========================================
// Form Loading
// =========================================

function initializeForms() {

    const forms = document.querySelectorAll("form");

    forms.forEach(form => {

        form.addEventListener("submit", () => {

            const button = form.querySelector(

                'button[type="submit"], button'

            );

            if (!button) return;

            button.disabled = true;

            button.dataset.original = button.innerHTML;

            button.innerHTML = "Please wait...";

        });

    });

}


// =========================================
// Password Toggle
// =========================================

function initializePasswordToggle() {

    const toggles = document.querySelectorAll(

        ".toggle-password"

    );

    toggles.forEach(toggle => {

        toggle.addEventListener("click", () => {

            const input = document.getElementById(

                toggle.dataset.target

            );

            if (!input) return;

            if (input.type === "password") {

                input.type = "text";

                toggle.innerHTML = "🙈";

            }

            else {

                input.type = "password";

                toggle.innerHTML = "👁️";

            }

        });

    });

}


// =========================================
// Basic Validation
// =========================================

function initializeValidation() {

    const password = document.querySelector(

        'input[name="password"]'

    );

    const confirm = document.querySelector(

        'input[name="confirm_password"]'

    );

    if (!password || !confirm) return;

    confirm.addEventListener("input", () => {

        if (

            password.value !== confirm.value

        ) {

            confirm.setCustomValidity(

                "Passwords do not match."

            );

        }

        else {

            confirm.setCustomValidity("");

        }

    });

}