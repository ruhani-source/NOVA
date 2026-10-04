const API_URL = "http://127.0.0.1:5000";


async function checkAPI() {
    try {
        const response = await fetch(`${API_URL}/health`);

        if (!response.ok) {
            throw new Error("API unavailable");
        }

        console.log("NOVA API connected successfully.");
    } catch (error) {
        console.error("Could not connect to NOVA API:", error);
    }
}


async function askNova() {
    const questionInput = document.getElementById("question-input");
    const answerText = document.getElementById("answer-text");
    const askButton = document.getElementById("ask-button");

    const question = questionInput.value.trim();

    if (!question) {
        answerText.textContent = "Please enter a question.";
        return;
    }

    askButton.disabled = true;
    askButton.textContent = "Thinking...";
    answerText.textContent = "NOVA is analyzing your question...";

    try {
        const response = await fetch(`${API_URL}/ask`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Request failed");
        }

        answerText.textContent = data.answer;

    } catch (error) {
        console.error("Search error:", error);
        answerText.textContent =
            "Sorry, NOVA could not answer your question right now.";
    } finally {
        askButton.disabled = false;
        askButton.textContent = "Search";
    }
}

async function addInformation() {
    const informationInput = document.getElementById("information-input");
    const informationStatus = document.getElementById("information-status");
    const informationButton = document.getElementById("information-button");

    const information = informationInput.value.trim();

    if (!information) {
        informationStatus.innerHTML =
            "<p>Please enter some information first.</p>";
        return;
    }

    informationButton.disabled = true;
    informationButton.textContent = "Adding...";
    informationStatus.innerHTML =
        "<p>NOVA is adding the new information...</p>";

    try {
        const response = await fetch(`${API_URL}/information`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                information: information
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Request failed");
        }

        informationStatus.innerHTML =
            "<p>✓ New information added successfully.</p>";

        informationInput.value = "";

    } catch (error) {
        console.error("Add information error:", error);

        informationStatus.innerHTML =
            "<p>Sorry, NOVA could not add the information right now.</p>";
    } finally {
        informationButton.disabled = false;
        informationButton.textContent = "Add Information";
    }
}


document.addEventListener("DOMContentLoaded", () => {
    checkAPI();

    const askButton = document.getElementById("ask-button");
    const informationButton = document.getElementById("information-button");

    askButton.addEventListener("click", askNova);
    informationButton.addEventListener("click", addInformation);
});