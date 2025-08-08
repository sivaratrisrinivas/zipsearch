// Advanced UI interactions
document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const userIdInput = document.getElementById('user-id');
    const nSlider = document.getElementById('n-slider');
    const nValue = document.getElementById('n-value');
    const valueBubble = document.getElementById('value-bubble');
    const sliderProgress = document.getElementById('slider-progress');
    const getRecsBtn = document.getElementById('get-recs');
    const btnText = getRecsBtn.querySelector('.btn-text');
    const results = document.getElementById('results');
    const emptyState = document.getElementById('empty-state');
    const themeToggle = document.getElementById('theme-toggle');
    const sunIcon = themeToggle.querySelector('.sun-icon');
    const moonIcon = themeToggle.querySelector('.moon-icon');
    
    // Quick select chips
    const chips = document.querySelectorAll('.chip');
    
    // Initialize
    updateSliderProgress();
    checkEmptyState();
    
    // Theme toggle
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('light-theme');
        sunIcon.classList.toggle('hidden');
        moonIcon.classList.toggle('hidden');
        
        // Animate theme transition
        document.body.style.transition = 'background 0.3s ease';
    });
    
    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
        document.body.classList.add('light-theme');
        sunIcon.classList.add('hidden');
        moonIcon.classList.remove('hidden');
    }
    
    // Floating label effect
    userIdInput.addEventListener('focus', () => {
        userIdInput.parentElement.classList.add('focused');
    });
    
    userIdInput.addEventListener('blur', () => {
        if (!userIdInput.value) {
            userIdInput.parentElement.classList.remove('focused');
        }
    });
    
    // Quick select chips
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const id = chip.dataset.id;
            userIdInput.value = id;
            userIdInput.parentElement.classList.add('focused');
            
            // Animate chip selection
            chip.style.transform = 'scale(0.95)';
            chip.style.background = 'var(--primary)';
            chip.style.color = 'white';
            
            setTimeout(() => {
                chip.style.transform = '';
                chip.style.background = '';
                chip.style.color = '';
            }, 200);
            
            // Focus input for better UX
            userIdInput.focus();
        });
    });
    
    // Slider interactions
    nSlider.addEventListener('input', () => {
        nValue.textContent = nSlider.value;
        updateSliderProgress();
        
        // Animate value bubble
        valueBubble.style.transform = 'scale(1.1)';
        setTimeout(() => {
            valueBubble.style.transform = 'scale(1)';
        }, 200);
    });
    
    function updateSliderProgress() {
        const percent = ((nSlider.value - nSlider.min) / (nSlider.max - nSlider.min)) * 100;
        sliderProgress.style.width = `${percent}%`;
    }
    
    // Main functionality
    getRecsBtn.addEventListener('click', async () => {
        const userId = userIdInput.value;
        const n = nSlider.value;
        
        if (!userId) {
            // Shake animation
            userIdInput.parentElement.style.animation = 'shake 0.5s ease-in-out';
            setTimeout(() => {
                userIdInput.parentElement.style.animation = '';
            }, 500);
            userIdInput.focus();
            return;
        }
        
        // Loading state
        getRecsBtn.classList.add('loading');
        getRecsBtn.disabled = true;
        results.innerHTML = '';
        emptyState.classList.add('hidden');
        
        try {
            const response = await fetch(`/recommend?user_id=${userId}&n=${n}`);
            const data = await response.json();
            
            if (data.recommendations && data.recommendations.length > 0) {
                displayResults(data.recommendations);
            } else {
                displayEmptyResults();
            }
        } catch (error) {
            console.error('Error:', error);
            displayError();
        } finally {
            getRecsBtn.classList.remove('loading');
            getRecsBtn.disabled = false;
        }
    });
    
    function displayResults(recommendations) {
        results.innerHTML = '';
        
        recommendations.forEach((rec, index) => {
            const card = createMovieCard(rec);
            results.appendChild(card);
        });
        
        // Trigger reflow for animations
        results.offsetHeight;
        
        // Add intersection observer for viewport animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, { threshold: 0.1 });
        
        document.querySelectorAll('.movie-card').forEach(card => {
            observer.observe(card);
        });
    }
    
    function createMovieCard(rec) {
        const card = document.createElement('div');
        card.className = 'movie-card';
        
        // Generate star rating
        const fullStars = Math.floor(rec.predicted_rating);
        const hasHalfStar = rec.predicted_rating % 1 >= 0.5;
        const stars = '★'.repeat(fullStars) + (hasHalfStar ? '☆' : '');
        
        card.innerHTML = `
            <h3 class="movie-title">${rec.movie_title}</h3>
            <div class="movie-rating">
                <span class="rating-value">${rec.predicted_rating.toFixed(1)}</span>
                <span class="stars">${stars}</span>
            </div>
        `;
        
        // Add click interaction
        card.addEventListener('click', () => {
            // Create ripple effect
            const ripple = document.createElement('div');
            ripple.className = 'ripple';
            card.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
        
        return card;
    }
    
    function displayEmptyResults() {
        results.innerHTML = `
            <div class="empty-results">
                <div class="empty-icon">🎯</div>
                <h3>No recommendations found</h3>
                <p>Try a different user ID or select from the quick options above</p>
            </div>
        `;
    }
    
    function displayError() {
        results.innerHTML = `
            <div class="error-state">
                <div class="error-icon">⚠️</div>
                <h3>Oops! Something went wrong</h3>
                <p>Please check your connection and try again</p>
            </div>
        `;
    }
    
    function checkEmptyState() {
        if (results.children.length === 0) {
            emptyState.classList.remove('hidden');
        } else {
            emptyState.classList.add('hidden');
        }
    }
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Enter to submit
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            getRecsBtn.click();
        }
        
        // Escape to clear input
        if (e.key === 'Escape' && document.activeElement === userIdInput) {
            userIdInput.value = '';
            userIdInput.blur();
        }
    });
    
    // Add custom styles for animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }
        
        .input-group.focused .modern-input {
            transform: scale(1.02);
        }
        
        .ripple {
            position: absolute;
            width: 100px;
            height: 100px;
            background: rgba(255, 255, 255, 0.6);
            border-radius: 50%;
            transform: translate(-50%, -50%) scale(0);
            animation: ripple-effect 0.6s ease-out;
            pointer-events: none;
        }
        
        @keyframes ripple-effect {
            to {
                transform: translate(-50%, -50%) scale(4);
                opacity: 0;
            }
        }
        
        .empty-results, .error-state {
            text-align: center;
            padding: 3rem;
            color: var(--text-secondary);
            animation: fadeIn 0.5s ease-out;
        }
        
        .empty-results h3, .error-state h3 {
            color: var(--text-primary);
            margin: 1rem 0 0.5rem;
        }
        
        .error-icon {
            font-size: 3rem;
            opacity: 0.5;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    `;
    document.head.appendChild(style);
    
    // Performance optimization: Debounce resize events
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            updateSliderProgress();
        }, 250);
    });
});