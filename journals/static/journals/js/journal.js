document.addEventListener('DOMContentLoaded', () => {
    // Gather the save button and journal content elements
    const saveBtn = document.querySelector('.save-btn');
    const journalContent = document.getElementById('journal-content');
    const aiButton = document.getElementById('ai-button');

    // Add event listener to save button
    if (saveBtn) {
        saveBtn.addEventListener('click', (e) => {
            const content = journalContent.innerHTML; // Get content

            // Get CSRF token
            const csrfToken = getCookie('csrftoken');

            // Post to current URL to update the journal
            fetch(window.location.href, {
                method: 'POST',
                // Set the headers to send the content to the server
                headers: {
                    'Content-Type': 'application/json', // Set the content type to JSON
                    'X-CSRFToken': csrfToken            // CSRF token to prevent cross-site request forgery
                },
                // Send the content to the server
                body: JSON.stringify({
                    content: content
                })
            })
            // Handle the response from the server
            .then(response => {
                // Check if the response was successful
                if (response.ok) {
                    console.log('Journal saved successfully');
                    // Change button text to indicate success
                    const originalText = saveBtn.textContent;
                    saveBtn.textContent = 'Saved!';
                    // Revert button text after 8 seconds
                    setTimeout(() => {
                        saveBtn.textContent = originalText;
                    }, 8000);
                } else {
                    console.error('Failed to save journal');
                    alert('Failed to save journal. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while saving.');
            });
        });
    }

    if (aiButton) {
        aiButton.addEventListener('click', function(e) {
            e.preventDefault();

            this.style.opacity = "0.5";
            this.style.pointerEvents = "none"; // Disable clicks while loading
            console.log("Fetching AI suggestion...");
            
            // Get current text from journal div
            const content = journalContent.innerText;

            // Get the speech bubble elements
            const bubble = document.getElementById('ai-bubble');
            const textTarget = document.getElementById('bubble-text');

            // Show "Thinking" state
            textTarget.innerText = "Thinking...";
            bubble.classList.add('show');

            // Get CSRF token
            const csrfToken = getCookie('csrftoken');
            const aiUrl = this.getAttribute('data-url');

            // Send the POST request
            fetch(aiUrl, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({
                    'topic': content
                })
            })
            .then(response => response.json())
            .then(data => {
                // Re-enable button
                this.style.opacity = "1";
                this.style.pointerEvents = "auto";
                
                // TODO: Need to do something with the response
                if (data.response) {
                   textTarget.innerText = data.response; 
                   console.log(data.response);
                }
            })
            .catch(error => {
                textTarget.innerText = "I'm having a little trouble thinking right now. Try again?";
                console.error('Error:', error);
                
                // Re-enable button
                this.style.opacity = "1";
                this.style.pointerEvents = "auto";
            });
        });

        // Close bubble if user clicks anywhere else
        document.addEventListener('click', function(event) {
            const container = document.querySelector('.ai-container');
            if (container && !container.contains(event.target)) {
                const bubble = document.getElementById('ai-bubble');
                if (bubble) bubble.classList.remove('show');
            }
        });
    }

    // Helper function to get cookie by name
    function getCookie(name) {
        let cookieValue = null;
        // Check if the page has a cookie
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            // Loop through the cookies
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Check if the cookie is the one we are looking for
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    // Decode the cookie and set its value
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
