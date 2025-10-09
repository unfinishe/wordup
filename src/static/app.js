// WordUp - JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });
    
    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
});

// Learning session functions
function showAnswer() {
    document.getElementById('answer-section').style.display = 'block';
    document.getElementById('show-answer').style.display = 'none';
    document.getElementById('rating-buttons').style.display = 'flex';
}

function submitRating(correct, cardId, direction) {
    // Submit via AJAX
    fetch('/learn/api/answer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            card_id: cardId,
            correct: correct,
            direction: direction
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Move to next card
            window.location.href = '/learn/review';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // Fallback to page reload
        window.location.reload();
    });
}