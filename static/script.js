// Assuming you want some basic interaction, like handling the flash messages.
document.addEventListener('DOMContentLoaded', function() {
    // Hide flash messages after 3 seconds
    const flashMessages = document.querySelectorAll('.alert');

    flashMessages.forEach((message) =>
        setTimeout(() => message.style.display = 'none', 3000)
    );
});
