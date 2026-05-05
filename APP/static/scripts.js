async function startLevel(level) {
    const response = await fetch('/start-level', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 1, level: level })
    });
    const data = await response.json();

    if (data.repeat) {
        alert(data.message);
    }

    document.getElementById('user-options').style.display = 'none';
    document.getElementById('quiz-container').style.display = 'block';
    displayQuiz(data.questions);
}

function displayQuiz(questions) {
    const quizContainer = document.getElementById('quiz');
    quizContainer.innerHTML = '';

    questions.forEach((q, index) => {
        const questionDiv = document.createElement('div');
        questionDiv.innerHTML = `<p>${index + 1}. ${q.question}</p>`;

        q.options.forEach((option, i) => {
            const radio = document.createElement('input');
            radio.type = 'radio';
            radio.name = `q${index}`;
            radio.value = option;
            questionDiv.appendChild(radio);
            questionDiv.appendChild(document.createTextNode(option));
            questionDiv.appendChild(document.createElement('br'));
        });

        quizContainer.appendChild(questionDiv);
    });
}

async function submitQuiz() {
    const responses = Array.from(document.querySelectorAll('#quiz input:checked')).map(input => input.value);
    const response = await fetch('/submit-level', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_id: 1,
            level: 1, // Example: Modify based on current level
            score: calculateScore(responses)
        })
    });
    const data = await response.json();

    document.getElementById('quiz-container').style.display = 'none';
    document.getElementById('results').style.display = 'block';
    document.getElementById('results-message').innerText = data.message;
}

function calculateScore(responses) {
    // Example score calculation (replace with actual logic)
    return responses.length * 2;
}

async function loadProgress() {
    const response = await fetch('/progress?user_id=1');
    const data = await response.json();

    const tableBody = document.getElementById('progress-data');
    tableBody.innerHTML = '';

    data.scores.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${row.level}</td><td>${row.score}</td>`;
        tableBody.appendChild(tr);
    });

    const badges = document.createElement('tr');
    badges.innerHTML = `<td colspan="3">Badges: ${data.badges.join(', ')}</td>`;
    tableBody.appendChild(badges);
}

function backToHome() {
    window.location.href = '/';
}
