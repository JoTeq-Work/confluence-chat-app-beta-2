const chatBtn = document.querySelector('button');
const aiListening = document.getElementById('ai-listening');

chatBtn.addEventListener('click', () => {
    // Change colour of button and disable it
    chatBtn.className = "btn btn-danger mt-1 disabled";

    // Add text to indicate AI is listening
    // aiListening.innerText = "Listening...";
})

