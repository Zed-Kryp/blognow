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
        const likeBtn = document.querySelector('.like-btn');
        const likeCount = document.querySelector('.like-count');
        
        if (likeBtn && likeCount) {
            likeCount.textContent = data.count;
            if (data.liked) {
                likeBtn.classList.add('liked');
            } else {
                likeBtn.classList.remove('liked');
            }
        }
        
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to like blog. Please try again.');
    }
}

// Share functionality
function shareBlog(blogId) {
    const url = `${window.location.origin}/blog/${blogId}`;
    
    if (navigator.share) {
        navigator.share({
            title: document.querySelector('.blog-title').textContent,
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

// Initialize any interactive elements
document.addEventListener('DOMContentLoaded', () => {
    // Add any initialization code here
}); 