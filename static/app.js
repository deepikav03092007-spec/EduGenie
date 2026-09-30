const tasks = {

    qa: {
        label: "Ask a question",

        placeholder:
            "Example: What is artificial intelligence?",

        button:
            "Get Answer"
    },


    explain: {
        label:
            "Topic to explain",

        placeholder:
            "Example: Explain photosynthesis in simple language.",

        button:
            "Explain Concept"
    },


    quiz: {
        label:
            "Topic or passage for the quiz",

        placeholder:
            "Paste a lesson, paragraph, or enter a topic.",

        button:
            "Generate Quiz"
    },


    summarize: {
        label:
            "Text to summarize",

        placeholder:
            "Paste your study notes or educational passage here.",

        button:
            "Summarize"
    },


    learn: {
        label:
            "Topic for a learning path",

        placeholder:
            "Example: Python, SQL, Machine Learning...",

        button:
            "Build Learning Path"
    }

};


let currentTask = "qa";

let lastResult = "";


const $ = (id) =>
    document.getElementById(id);


const input =
    $("inputText");


const label =
    $("inputLabel");


const submitBtn =
    $("submitBtn");


const result =
    $("result");


const copyBtn =
    $("copyBtn");


const options =
    $("options");


const levelContainer =
    $("levelContainer");


const weeksContainer =
    $("weeksContainer");


const countContainer =
    $("countContainer");


function setTask(task) {

    currentTask = task;


    document
        .querySelectorAll(".task")
        .forEach(
            (button) => {

                button.classList.toggle(
                    "active",
                    button.dataset.task === task
                );

            }
        );


    const config =
        tasks[task];


    label.textContent =
        config.label;


    input.placeholder =
        config.placeholder;


    submitBtn.textContent =
        config.button;


    options.style.display =
        task === "learn" ||
        task === "quiz"
            ? "flex"
            : "none";


    levelContainer.style.display =
        task === "learn"
            ? "block"
            : "none";


    weeksContainer.style.display =
        task === "learn"
            ? "block"
            : "none";


    countContainer.style.display =
        task === "quiz"
            ? "block"
            : "none";

}


document
    .querySelectorAll(".task")
    .forEach(
        (button) => {

            button.addEventListener(
                "click",
                () => {

                    setTask(
                        button.dataset.task
                    );

                }
            );

        }
    );


async function checkHealth() {

    try {

        const response =
            await fetch(
                "/health"
            );


        $("status").textContent =
            response.ok
                ? "● API online"
                : "API unavailable";

    }

    catch {

        $("status").textContent =
            "API unavailable";

    }

}


function escapeHtml(value) {

    return String(value)
        .replace(
            /[&<>'"]/g,
            (character) => {

                const map = {

                    "&": "&amp;",

                    "<": "&lt;",

                    ">": "&gt;",

                    "'": "&#39;",

                    '"': "&quot;"

                };


                return map[character];

            }
        );

}


function renderText(text) {

    return escapeHtml(
        text
    ).replace(
        /\n/g,
        "<br>"
    );

}


function renderQuiz(items) {

    return items
        .map(
            (question, index) => {

                return `

                    <div class="quiz-item">

                        <h3>
                            ${index + 1}.
                            ${escapeHtml(
                                question.question
                            )}
                        </h3>


                        ${question.options
                            .map(
                                (option) => `
                                    <div class="option">
                                        ${escapeHtml(option)}
                                    </div>
                                `
                            )
                            .join("")
                        }


                        <div class="answer">

                            <strong>
                                Correct answer:
                            </strong>

                            ${escapeHtml(
                                question.answer
                            )}

                            <br>

                            ${escapeHtml(
                                question.explanation
                            )}

                        </div>

                    </div>

                `;

            }
        )
        .join("");

}


async function runTask() {

    const text =
        input.value.trim();


    if (!text) {

        result.innerHTML =
            '<span class="error">Please enter some text first.</span>';

        return;

    }


    submitBtn.disabled =
        true;


    copyBtn.disabled =
        true;


    result.className =
        "result muted";


    result.textContent =
        "EduGenie is thinking...";


    let endpoint;

    let body;


    if (
        currentTask === "qa"
    ) {

        endpoint = "/qa";

        body = {
            question: text
        };

    }


    else if (
        currentTask === "explain"
    ) {

        endpoint = "/explain";

        body = {
            text: text
        };

    }


    else if (
        currentTask === "quiz"
    ) {

        endpoint = "/quiz";

        body = {

            text: text,

            count:
                Number(
                    $("count").value
                )

        };

    }


    else if (
        currentTask === "summarize"
    ) {

        endpoint =
            "/summarize";

        body = {
            text: text
        };

    }


    else {

        endpoint =
            "/learn/recommendations";

        body = {

            topic: text,

            level:
                $("level").value,

            weeks:
                Number(
                    $("weeks").value
                )

        };

    }


    try {

        const response =
            await fetch(
                endpoint,
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            body
                        )

                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Request failed."
            );

        }


        if (
            currentTask === "qa"
        ) {

            lastResult =
                data.answer;

        }


        else if (
            currentTask === "explain"
        ) {

            lastResult =
                data.explanation;

        }


        else if (
            currentTask === "summarize"
        ) {

            lastResult =
                data.summary;

        }


        else if (
            currentTask === "learn"
        ) {

            lastResult =
                data.recommendations;

        }


        else if (
            currentTask === "quiz"
        ) {

            lastResult =
                JSON.stringify(
                    data.quiz,
                    null,
                    2
                );

        }


        result.className =
            "result";


        if (
            currentTask === "quiz"
        ) {

            result.innerHTML =
                renderQuiz(
                    data.quiz
                );

        }

        else {

            result.innerHTML =
                renderText(
                    lastResult
                );

        }


        copyBtn.disabled =
            false;

    }


    catch (error) {

        result.className =
            "result error";

        result.textContent =
            error.message;

    }


    finally {

        submitBtn.disabled =
            false;

    }

}


submitBtn.addEventListener(
    "click",
    runTask
);


copyBtn.addEventListener(
    "click",
    async () => {

        if (!lastResult) {
            return;
        }


        try {

            await navigator.clipboard
                .writeText(
                    lastResult
                );


            copyBtn.textContent =
                "Copied!";


            setTimeout(
                () => {

                    copyBtn.textContent =
                        "Copy";

                },
                1200
            );

        }

        catch {

            copyBtn.textContent =
                "Copy failed";

        }

    }
);


setTask("qa");

checkHealth();