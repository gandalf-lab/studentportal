// Global JavaScript for interactive features

document.addEventListener('DOMContentLoaded', function() {
    // Add fade-in animation to all cards
    const cards = document.querySelectorAll('.card, .dashboard-card, .course');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });

    // Add active state to current page in navigation
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let valid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    valid = false;
                    field.style.borderColor = '#e53e3e';
                } else {
                    field.style.borderColor = '#c6f6d5';
                }
            });
            
            if (!valid) {
                e.preventDefault();
                showNotification('Please fill in all required fields', 'error');
            }
        });
    });

    // Course registration confirmation
    const registerButtons = document.querySelectorAll('.btn.register');
    registerButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to register for this course?')) {
                e.preventDefault();
            }
        });
    });

    // Auto-hide success messages after 5 seconds
    const successMessages = document.querySelectorAll('.alert.success');
    successMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transition = 'opacity 0.5s ease';
            setTimeout(() => message.remove(), 500);
        }, 5000);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Dynamic greeting based on time of day
    const greetingElement = document.querySelector('.welcome h2');
    if (greetingElement) {
        const hour = new Date().getHours();
        let greeting = 'Welcome';
        
        if (hour < 12) greeting = 'Good morning';
        else if (hour < 18) greeting = 'Good afternoon';
        else greeting = 'Good evening';
        
        const studentName = greetingElement.textContent.split(', ')[1];
        if (studentName) {
            greetingElement.textContent = `${greeting}`, `${studentName.replace('!', '')}!`;
        }
    }
});

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = alert `${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '10000';
    notification.style.minWidth = '300px';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Course search functionality
function searchCourses() {
    const input = document.getElementById('courseSearch');
    const filter = input.value.toLowerCase();
    const courses = document.querySelectorAll('.course');
    
    courses.forEach(course => {
        const text = course.textContent.toLowerCase();
        course.style.display = text.includes(filter) ? 'block' : 'none';
    });
}