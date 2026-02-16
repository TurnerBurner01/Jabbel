// This file is used to change the modal display to show the create journal form

// DOMContentLoaded ensures the script runs after the HTML is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("journalModal");
    const btn = document.getElementById("openModalBtn");
    
    // If the button and modal exist, add event listeners
    if (btn && modal) {
        // When the user clicks the button, open the modal (Make it show)
        btn.onclick = () => {
            modal.style.display = "block";
        }
        
        // When the user clicks anywhere outside of the modal, close it (Make it hide)
        window.onclick = (event) => {
            if (event.target == modal) modal.style.display = "none";
        }
    }
});