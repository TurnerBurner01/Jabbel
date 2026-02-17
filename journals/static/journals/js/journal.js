document.addEventListener('DOMContentLoaded', () => {
    // Gather the save button and journal content elements
    const saveBtn = document.querySelector('.save-btn');
    const journalContent = document.getElementById('journal-content');

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
