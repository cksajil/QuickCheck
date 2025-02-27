document.addEventListener('DOMContentLoaded', function () {
    const quizCode = "{{ quiz_code }}";
    const username = "{{ username }}";

    const socket = io();

    socket.on('connect', function () {
        socket.emit('join', { username: username, quiz_code: quizCode });
    });

    socket.on('message', function (message) {
        const messages = document.getElementById('messages');
        messages.innerHTML += `<p>${message}</p>`;
    });

    socket.on('answer_received', function (data) {
        const messages = document.getElementById('messages');
        messages.innerHTML += `<p>${data.username} answered: ${data.answer}</p>`;
    });
});

function submitAnswer(answer) {
    const quizCode = "{{ quiz_code }}";
    const username = "{{ username }}";

    const socket = io();
    socket.emit('submit_answer', { username: username, quiz_code: quizCode, answer: answer });
}