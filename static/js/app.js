document.addEventListener("DOMContentLoaded", () => {

    "use strict";


    /* =====================================================
       ELEMENTS
       ===================================================== */

    const form =
        document.getElementById("searchForm");

    const input =
        document.getElementById("searchInput");

    const clearButton =
        document.getElementById("clearSearch");

    const modeInput =
        document.getElementById("searchMode");

    const normalButton =
        document.getElementById("normalModeButton");

    const goButton =
        document.getElementById("goModeButton");

    const indicator =
        document.getElementById("modeIndicator");

    const tabs =
        document.querySelectorAll(".result-tab");

    const panels =
        document.querySelectorAll(".tab-panel");


    /* =====================================================
       MODE
       ===================================================== */

    function setMode(mode) {

        if (
            mode !== "normal" &&
            mode !== "go"
        ) {
            mode = "normal";
        }


        if (modeInput) {

            modeInput.value = mode;
        }


        if (normalButton) {

            const active =
                mode === "normal";

            normalButton.classList.toggle(
                "active",
                active
            );

            normalButton.setAttribute(
                "aria-pressed",
                String(active)
            );
        }


        if (goButton) {

            const active =
                mode === "go";

            goButton.classList.toggle(
                "active",
                active
            );

            goButton.setAttribute(
                "aria-pressed",
                String(active)
            );
        }


        if (indicator) {

            indicator.classList.toggle(
                "go-active",
                mode === "go"
            );


            indicator.innerHTML =
                mode === "go"

                    ? '<span class="mode-dot"></span> Go Mode Active'

                    : '<span class="mode-dot"></span> Normal Mode';
        }
    }


    if (normalButton) {

        normalButton.addEventListener(
            "click",
            () => {

                setMode("normal");

            }
        );
    }


    if (goButton) {

        goButton.addEventListener(
            "click",
            () => {

                setMode("go");

            }
        );
    }


    setMode(
        modeInput
            ? modeInput.value
            : "normal"
    );


    /* =====================================================
       SEARCH INPUT
       ===================================================== */

    function updateClearButton() {

        if (
            !clearButton ||
            !input
        ) {
            return;
        }


        const hasText =
            input.value.trim().length > 0;


        clearButton.classList.toggle(
            "visible",
            hasText
        );
    }


    if (input) {

        input.addEventListener(
            "input",
            updateClearButton
        );

        updateClearButton();
    }


    /* =====================================================
       CLEAR
       ===================================================== */

    if (clearButton) {

        clearButton.addEventListener(
            "click",
            () => {

                if (!input) {
                    return;
                }


                input.value = "";

                updateClearButton();

                input.focus();

            }
        );
    }


    /* =====================================================
       SEARCH FORM
       ===================================================== */

    if (form) {

        form.addEventListener(
            "submit",
            (event) => {

                if (!input) {
                    return;
                }


                const query =
                    input.value.trim();


                if (!query) {

                    event.preventDefault();

                    input.focus();

                    return;
                }


                input.value = query;

            }
        );
    }


    /* =====================================================
       "/" SEARCH SHORTCUT
       ===================================================== */

    document.addEventListener(
        "keydown",
        (event) => {

            const target =
                document.activeElement;


            const typing =
                target &&
                (
                    target.tagName === "INPUT" ||
                    target.tagName === "TEXTAREA" ||
                    target.isContentEditable
                );


            if (
                event.key === "/" &&
                !typing &&
                !event.ctrlKey &&
                !event.metaKey &&
                !event.altKey
            ) {

                event.preventDefault();

                if (input) {
                    input.focus();
                }
            }
        }
    );


    /* =====================================================
       RESULT TABS
       ===================================================== */

    function activateTab(
        tabName
    ) {

        tabs.forEach(
            (tab) => {

                const active =
                    tab.dataset.tab === tabName;


                tab.classList.toggle(
                    "active",
                    active
                );


                tab.setAttribute(
                    "aria-selected",
                    String(active)
                );
            }
        );


        panels.forEach(
            (panel) => {

                const active =
                    panel.dataset.panel === tabName;


                panel.classList.toggle(
                    "active",
                    active
                );


                if (active) {

                    panel.removeAttribute(
                        "hidden"
                    );

                } else {

                    panel.setAttribute(
                        "hidden",
                        ""
                    );
                }
            }
        );
    }


    tabs.forEach(
        (tab) => {

            tab.addEventListener(
                "click",
                () => {

                    const tabName =
                        tab.dataset.tab;


                    if (tabName) {

                        activateTab(
                            tabName
                        );
                    }
                }
            );
        }
    );


    /* =====================================================
       INITIAL TAB
       ===================================================== */

    if (tabs.length) {

        const activeTab =
            document.querySelector(
                ".result-tab.active"
            );


        activateTab(
            activeTab
                ? activeTab.dataset.tab
                : tabs[0].dataset.tab
        );
    }


    /* =====================================================
       IMAGE FALLBACK
       ===================================================== */

    document
        .querySelectorAll("img")
        .forEach(
            (image) => {

                image.addEventListener(
                    "error",
                    () => {

                        image.classList.add(
                            "image-load-error"
                        );

                    }
                );
            }
        );


    /* =====================================================
       READY
       ===================================================== */

    document.documentElement.classList.add(
        "vedfinder-ready"
    );

});