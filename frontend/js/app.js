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

document.addEventListener("DOMContentLoaded", () => {
    checkAPI();
});