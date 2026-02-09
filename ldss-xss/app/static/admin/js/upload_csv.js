document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('csv-upload-form');
    const statusDiv = document.getElementById('upload-status');
    const submitBtn = document.getElementById('submit-button');

    if (!form || !submitBtn || !statusDiv) {
        return;
    }

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        console.log('Form submitted');
        
        submitBtn.disabled = true;
        statusDiv.innerHTML = '<p>Processing upload...</p>';

        const formData = new FormData(form);

        console.log(form.dataset.redirectUrl);

        fetch('/api/upload-csv/', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            submitBtn.disabled = false;
            if (data.error) {
                statusDiv.innerHTML = `<p class="errornote">${data.error}</p>`;
            } else {
                statusDiv.innerHTML = `<p class="successnote">${data.message}</p>`;
                setTimeout(() => {
                    window.location.href = form.dataset.redirectUrl;
                }, 2000);
            }
        })
        .catch(error => {
            submitBtn.disabled = false;
            statusDiv.innerHTML = '<p class="errornote">An error occurred while processing the request.</p>';
            console.error('Error:', error);
        });
    });
});
