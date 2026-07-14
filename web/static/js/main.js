// ============================================================================
// DevSeek - Main JavaScript Interactions & Micro-animations
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const clearBtn = document.getElementById('clearBtn');

    if (searchInput && clearBtn) {
        // Show/hide clear button based on input content
        const toggleClearBtn = () => {
            if (searchInput.value.trim().length > 0) {
                clearBtn.style.display = 'block';
            } else {
                clearBtn.style.display = 'none';
            }
        };

        searchInput.addEventListener('input', toggleClearBtn);
        toggleClearBtn();

        clearBtn.addEventListener('click', () => {
            searchInput.value = '';
            clearBtn.style.display = 'none';
            searchInput.focus();
        });
    }

    // Add subtle hover sound or card animation effect
    const resultCards = document.querySelectorAll('.result-card');
    resultCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateX(6px)';
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateX(0)';
        });
    });

    console.log('[DevSeek] Vertical Search Engine Frontend initialized with rich interactions.');
});
