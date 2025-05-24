document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.blog-form');
    const titleInput = document.getElementById('title');
    const contentInput = document.getElementById('content');
    const tagsInput = document.getElementById('tags');

    // Auto-save functionality
    let autoSaveTimeout;
    const autoSave = () => {
        clearTimeout(autoSaveTimeout);
        autoSaveTimeout = setTimeout(() => {
            const draft = {
                title: titleInput.value,
                content: contentInput.value,
                tags: tagsInput.value
            };
            localStorage.setItem('blog_draft', JSON.stringify(draft));
        }, 1000);
    };

    // Load draft if exists
    const loadDraft = () => {
        const draft = localStorage.getItem('blog_draft');
        if (draft) {
            const { title, content, tags } = JSON.parse(draft);
            titleInput.value = title || '';
            contentInput.value = content || '';
            tagsInput.value = tags || '';
        }
    };

    // Clear draft when form is submitted
    form.addEventListener('submit', () => {
        localStorage.removeItem('blog_draft');
    });

    // Add auto-save listeners
    titleInput.addEventListener('input', autoSave);
    contentInput.addEventListener('input', autoSave);
    tagsInput.addEventListener('input', autoSave);

    // Load draft on page load
    loadDraft();

    // Form validation
    form.addEventListener('submit', (e) => {
        if (!titleInput.value.trim()) {
            e.preventDefault();
            alert('Please enter a title for your blog post.');
            titleInput.focus();
            return;
        }

        if (!contentInput.value.trim()) {
            e.preventDefault();
            alert('Please enter some content for your blog post.');
            contentInput.focus();
            return;
        }
    });

    // Character count for content
    const updateCharCount = () => {
        const charCount = contentInput.value.length;
        const maxChars = 50000; // Set a reasonable limit
        const remaining = maxChars - charCount;
        
        if (remaining < 0) {
            contentInput.value = contentInput.value.substring(0, maxChars);
        }
    };

    contentInput.addEventListener('input', updateCharCount);
}); 