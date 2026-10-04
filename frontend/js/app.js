const API_URL = "http://127.0.0.1:5000";


// =========================================
// GLOBAL MEMORY
// =========================================

let novaMemory = null;


// =========================================
// API STATUS
// =========================================

async function checkAPI() {

    const statusDot =
        document.getElementById("status-dot");

    const statusText =
        document.getElementById("status-text");


    try {

        const response =
            await fetch(`${API_URL}/health`);


        if (!response.ok) {
            throw new Error("API unavailable");
        }


        statusDot.classList.remove("offline");

        statusDot.classList.add("online");

        statusText.textContent =
            "API Online";


        console.log(
            "NOVA API connected successfully."
        );


    } catch (error) {

        statusDot.classList.remove("online");

        statusDot.classList.add("offline");

        statusText.textContent =
            "API Offline";


        console.error(
            "Could not connect to NOVA API:",
            error
        );
    }
}


// =========================================
// LOAD PROJECT MEMORY
// =========================================

async function loadMemory() {

    try {

        const response =
            await fetch(`${API_URL}/memory`);


        if (!response.ok) {

            throw new Error(
                "Could not load project memory"
            );
        }


        novaMemory =
            await response.json();


        console.log(
            "NOVA project memory loaded:",
            novaMemory
        );


        renderMemory();


    } catch (error) {

        console.error(
            "Memory loading error:",
            error
        );
    }
}


// =========================================
// RENDER MEMORY
// =========================================

function renderMemory() {

    if (!novaMemory) {
        return;
    }


    renderDecisions();

    renderActions();

    renderRisks();

    renderSources();

    renderTimeline();
}


// =========================================
// DECISIONS
// =========================================

function renderDecisions() {

    const section =
        document.querySelector(
            "#decisions .card-grid"
        );


    if (!section) {
        return;
    }


    const decisions =
        novaMemory.decisions || [];


    if (decisions.length === 0) {

        section.innerHTML =
            emptyState(
                "No decisions found in the project memory."
            );

        return;
    }


    section.innerHTML =
        decisions
            .map(
                (decision, index) => `

                <article class="info-card">

                    <div class="card-top">

                        <span class="card-icon decision-icon">
                            ✓
                        </span>

                        <span class="tag decision-tag">
                            Decision ${index + 1}
                        </span>

                    </div>

                    <h3>
                        ${escapeHTML(
                            cleanText(decision.text)
                        )}
                    </h3>

                    <div class="card-footer">

                        <span>
                            Source
                        </span>

                        <strong>
                            ${escapeHTML(
                                decision.source
                            )}
                        </strong>

                    </div>

                </article>
            `
            )
            .join("");
}


// =========================================
// ACTIONS
// =========================================

function renderActions() {

    const container =
        document.querySelector(
            "#actions .action-list"
        );


    if (!container) {
        return;
    }


    const commitments =
        novaMemory.commitments || [];


    const owners =
        novaMemory.owners || [];


    const deadlines =
        novaMemory.deadlines || [];


    if (commitments.length === 0) {

        container.innerHTML =
            emptyState(
                "No remaining actions were found."
            );

        return;
    }


    container.innerHTML =
        commitments
            .map(
                (commitment, index) => {

                    const owner =
                        owners[index]?.text
                        || "À confirmer";


                    const deadline =
                        deadlines[index]?.text
                        || "À confirmer";


                    return `

                    <article class="action-card">

                        <div class="action-status pending">

                            <span></span>

                            Pending

                        </div>


                        <div class="action-main">

                            <h3>
                                ${escapeHTML(
                                    cleanText(
                                        commitment.text
                                    )
                                )}
                            </h3>

                            <p>
                                Action identified
                                from NOVA's project memory.
                            </p>

                        </div>


                        <div class="action-details">

                            <div>

                                <span>
                                    RESPONSIBLE
                                </span>

                                <strong>
                                    ${escapeHTML(
                                        cleanText(owner)
                                    )}
                                </strong>

                            </div>


                            <div>

                                <span>
                                    DEADLINE
                                </span>

                                <strong>
                                    ${escapeHTML(
                                        cleanText(deadline)
                                    )}
                                </strong>

                            </div>


                            <div>

                                <span>
                                    EVIDENCE
                                </span>

                                <strong>
                                    NOVA memory
                                </strong>

                            </div>

                        </div>

                    </article>

                    `;
                }
            )
            .join("");
}


// =========================================
// RISKS
// =========================================

function renderRisks() {

    const container =
        document.querySelector(
            "#risks .risk-grid"
        );


    if (!container) {
        return;
    }


    const risks =
        novaMemory.risks || [];


    if (risks.length === 0) {

        container.innerHTML =
            emptyState(
                "No risks found in the project memory."
            );

        return;
    }


    container.innerHTML =
        risks
            .map(
                (risk, index) => `

                <article class="risk-card">

                    <div class="risk-level medium">
                        MONITORED
                    </div>

                    <h3>
                        Risk ${index + 1}
                    </h3>

                    <p>
                        ${escapeHTML(
                            cleanText(risk.text)
                        )}
                    </p>

                    <span class="risk-source">

                        Source:
                        ${escapeHTML(
                            risk.source
                        )}

                    </span>

                </article>

            `
            )
            .join("");
}


// =========================================
// SOURCES
// =========================================

function renderSources() {

    const container =
        document.querySelector(
            "#sources .source-list"
        );


    if (!container) {
        return;
    }


    const sources =
        novaMemory.sources || [];


    if (sources.length === 0) {

        container.innerHTML =
            emptyState(
                "No sources found."
            );

        return;
    }


    // Remove duplicate filenames

    const uniqueSources =
        [
            ...new Map(
                sources.map(
                    source => [
                        source.filename,
                        source
                    ]
                )
            ).values()
        ];


    container.innerHTML =
        uniqueSources
            .map(
                source => `

                <article class="source-card">

                    <div class="source-icon">
                        ▤
                    </div>


                    <div class="source-info">

                        <h3>
                            ${escapeHTML(
                                source.filename
                            )}
                        </h3>

                        <p>
                            Indexed project source
                            used by NOVA.
                        </p>

                    </div>


                    <span class="source-status">
                        Indexed
                    </span>

                </article>

            `
            )
            .join("");
}


// =========================================
// TIMELINE
// =========================================

function renderTimeline() {

    const container =
        document.querySelector(
            "#timeline .timeline"
        );


    if (!container) {
        return;
    }


    const decisions =
        novaMemory.decisions || [];


    const deadlines =
        novaMemory.deadlines || [];


    const events = [];


    decisions.forEach(
        decision => {

            events.push({
                type: "Decision",
                text: decision.text,
                source: decision.source
            });

        }
    );


    deadlines.forEach(
        deadline => {

            events.push({
                type: "Deadline",
                text: deadline.text,
                source: deadline.source
            });

        }
    );


    if (events.length === 0) {

        container.innerHTML =
            emptyState(
                "No timeline events found."
            );

        return;
    }


    container.innerHTML =
        events
            .slice(0, 12)
            .map(
                (event, index) => `

                <div class="timeline-item">

                    <div class="timeline-marker ${
                        index === 0
                            ? "current"
                            : ""
                    }">

                        <span></span>

                    </div>


                    <div class="timeline-content">

                        <div class="timeline-date">
                            PROJECT MEMORY
                        </div>


                        <h3>
                            ${escapeHTML(
                                event.type
                            )}
                        </h3>


                        <p>
                            ${escapeHTML(
                                cleanText(
                                    event.text
                                )
                            )}
                        </p>


                        <div class="timeline-meta">

                            <span class="tag decision-tag">
                                ${escapeHTML(
                                    event.type
                                )}
                            </span>


                            <span class="source-tag">

                                ${escapeHTML(
                                    event.source
                                )}

                            </span>

                        </div>

                    </div>

                </div>

            `
            )
            .join("");
}


// =========================================
// ASK NOVA
// =========================================

async function askNova() {

    const questionInput =
        document.getElementById(
            "question-input"
        );


    const askButton =
        document.getElementById(
            "ask-button"
        );


    const question =
        questionInput.value.trim();


    if (!question) {

        questionInput.focus();

        return;
    }


    addUserMessage(question);


    questionInput.value = "";


    askButton.disabled = true;


    askButton.querySelector(
        "span"
    ).textContent =
        "Thinking...";


    const loadingMessage =
        addNovaMessage(
            "NOVA is analyzing the project memory..."
        );


    try {

        const response =
            await fetch(
                `${API_URL}/ask`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        question: question
                    })
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Request failed"
            );
        }


        loadingMessage.remove();


        addNovaMessage(
            data.answer,
            true
        );


    } catch (error) {

        console.error(
            "Ask NOVA error:",
            error
        );


        loadingMessage.remove();


        addNovaMessage(
            "Sorry, NOVA could not answer the question right now."
        );


    } finally {

        askButton.disabled = false;

        askButton.querySelector(
            "span"
        ).textContent =
            "Ask NOVA";
    }
}


// =========================================
// CHAT HELPERS
// =========================================

function addUserMessage(message) {

    const chatMessages =
        document.getElementById(
            "chat-messages"
        );


    const wrapper =
        document.createElement("div");


    wrapper.className =
        "message user-message";


    wrapper.innerHTML = `

        <div class="message-bubble">

            <p>
                ${escapeHTML(message)}
            </p>

        </div>

    `;


    chatMessages.appendChild(
        wrapper
    );


    scrollChatToBottom();
}


function addNovaMessage(
    message,
    showSource = false
) {

    const chatMessages =
        document.getElementById(
            "chat-messages"
        );


    const wrapper =
        document.createElement("div");


    wrapper.className =
        "message nova-message";


    wrapper.innerHTML = `

        <div class="message-avatar">
            N
        </div>


        <div class="message-bubble">

            <p>
                ${formatAnswer(message)}
            </p>


            ${
                showSource
                    ? `
                        <span class="message-source">
                            Grounded in project memory
                        </span>
                      `
                    : ""
            }

        </div>

    `;


    chatMessages.appendChild(
        wrapper
    );


    scrollChatToBottom();


    return wrapper;
}


function scrollChatToBottom() {

    const chatMessages =
        document.getElementById(
            "chat-messages"
        );


    chatMessages.scrollTop =
        chatMessages.scrollHeight;
}


// =========================================
// NEW INFORMATION
// =========================================

async function addInformation() {

    const informationInput =
        document.getElementById(
            "information-input"
        );


    const informationStatus =
        document.getElementById(
            "information-status"
        );


    const informationButton =
        document.getElementById(
            "information-button"
        );


    const information =
        informationInput.value.trim();


    if (!information) {

        informationStatus.textContent =
            "Please enter some information first.";

        return;
    }


    informationButton.disabled =
        true;


    informationButton.querySelector(
        "span"
    ).textContent =
        "Adding...";


    informationStatus.textContent =
        "NOVA is updating the project memory...";


    try {

        const response =
            await fetch(
                `${API_URL}/information`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        information:
                            information
                    })
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Request failed"
            );
        }


        informationStatus.textContent =
            "✓ Information added to NOVA's memory.";


        informationInput.value = "";


    } catch (error) {

        console.error(
            "Add information error:",
            error
        );


        informationStatus.textContent =
            "Sorry, NOVA could not add the information right now.";


    } finally {

        informationButton.disabled =
            false;


        informationButton.querySelector(
            "span"
        ).textContent =
            "＋ Add to memory";
    }
}


// =========================================
// NAVIGATION
// =========================================

function setupNavigation() {

    const navItems =
        document.querySelectorAll(
            ".nav-item"
        );


    const sections =
        document.querySelectorAll(
            ".page-section"
        );


    navItems.forEach(
        item => {

            item.addEventListener(
                "click",
                () => {

                    navItems.forEach(
                        nav =>
                            nav.classList.remove(
                                "active"
                            )
                    );


                    item.classList.add(
                        "active"
                    );

                }
            );

        }
    );


    const observer =
        new IntersectionObserver(
            entries => {

                entries.forEach(
                    entry => {

                        if (
                            !entry.isIntersecting
                        ) {
                            return;
                        }


                        const id =
                            entry.target.id;


                        navItems.forEach(
                            item => {

                                item.classList.toggle(
                                    "active",
                                    item.getAttribute(
                                        "href"
                                    ) ===
                                    `#${id}`
                                );

                            }
                        );

                    }
                );

            },
            {
                threshold: 0.25
            }
        );


    sections.forEach(
        section =>
            observer.observe(section)
    );
}


// =========================================
// KEYBOARD
// =========================================

function setupKeyboardShortcuts() {

    const questionInput =
        document.getElementById(
            "question-input"
        );


    questionInput.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Enter" &&
                (
                    event.ctrlKey ||
                    event.metaKey
                )
            ) {

                event.preventDefault();

                askNova();
            }

        }
    );
}


// =========================================
// HELPERS
// =========================================

function cleanText(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";
    }


    if (
        typeof value === "string"
    ) {

        return value;
    }


    return JSON.stringify(value);
}


function escapeHTML(text) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        String(text);


    return div.innerHTML;
}


function formatAnswer(text) {

    return escapeHTML(
        text || ""
    ).replace(
        /\n/g,
        "<br>"
    );
}


function emptyState(message) {

    return `

        <div class="info-card">

            <p style="
                color: var(--text-soft);
                font-size: 13px;
            ">

                ${escapeHTML(message)}

            </p>

        </div>

    `;
}


// =========================================
// INITIALIZATION
// =========================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        checkAPI();

        loadMemory();

        setupNavigation();

        setupKeyboardShortcuts();


        const askButton =
            document.getElementById(
                "ask-button"
            );


        const informationButton =
            document.getElementById(
                "information-button"
            );


        askButton.addEventListener(
            "click",
            askNova
        );


        informationButton.addEventListener(
            "click",
            addInformation
        );

    }
);