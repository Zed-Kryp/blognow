// Share blog functionality
function shareBlog(blogId) {
    const url = `${window.location.origin}/blog/${blogId}`;
    
    if (navigator.share) {
        navigator.share({
            title: 'Check out this blog post!',
            url: url
        })
        .catch(error => console.log('Error sharing:', error));
    } else {
        // Fallback for browsers that don't support Web Share API
        const dummy = document.createElement('input');
        document.body.appendChild(dummy);
        dummy.value = url;
        dummy.select();
        document.execCommand('copy');
        document.body.removeChild(dummy);
        
        alert('Link copied to clipboard!');
    }
}

// Like functionality
async function likeBlog(blogId) {
    try {
        const response = await fetch(`/blog/${blogId}/like`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to like blog');
        }
        
        const data = await response.json();
        const likeCount = document.querySelector(`#blog-${blogId} .likes`);
        if (likeCount) {
            likeCount.textContent = data.count;
        }
        
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to like blog. Please try again.');
    }
}

// Initialize any interactive elements
document.addEventListener('DOMContentLoaded', () => {
    // Add click event listeners to like buttons
    document.querySelectorAll('.like-icon').forEach(icon => {
        icon.addEventListener('click', (e) => {
            const blogId = e.target.closest('.blog-card').dataset.blogId;
            likeBlog(blogId);
        });
    });
}); 