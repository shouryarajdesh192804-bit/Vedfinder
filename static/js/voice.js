// =========================================
// VedFinder V3
// voice.js
// =========================================

document.addEventListener("DOMContentLoaded", () => {

    initializeVoice();

});


// =========================================
// Voice Search
// =========================================

function initializeVoice() {

    const button = document.getElementById("voiceBtn");

    const input = document.querySelector(

        'input[name="query"]'

    );

    if (!button || !input) return;

    const SpeechRecognition =

        window.SpeechRecognition ||

        window.webkitSpeechRecognition;

    if (!SpeechRecognition) {

        button.disabled = true;

        button.title =

            "Voice search is not supported by your browser.";

        return;

    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-US";

    recognition.interimResults = false;

    recognition.maxAlternatives = 1;

    recognition.continuous = false;

    button.addEventListener(

        "click",

        () => {

            button.disabled = true;

            button.innerHTML = "🎙️";

            recognition.start();

        }

    );

    recognition.onstart = () => {

        button.classList.add(

            "recording"

        );

    };

    recognition.onresult = (event) => {

        const transcript =

            event.results[0][0].transcript;

        input.value = transcript;

        input.focus();

    };

    recognition.onerror = (event) => {

        console.error(

            "Voice Error:",

            event.error

        );

        alert(

            "Voice search failed. Please try again."

        );

    };

    recognition.onend = () => {

        button.disabled = false;

        button.innerHTML = "🎤";

        button.classList.remove(

            "recording"

        );

    };

}