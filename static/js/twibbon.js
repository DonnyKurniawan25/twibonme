document.addEventListener('DOMContentLoaded', function () {
    const canvas = document.getElementById('twibbon-canvas');
    const ctx = canvas.getContext('2d');
    const frameImage = document.getElementById('frame-image');
    const imageUpload = document.getElementById('image-upload');
    const downloadBtn = document.getElementById('download-btn');
    const zoomSlider = document.getElementById('zoom-slider');
    const loadingOverlay = document.getElementById('loading-overlay');

    let userImage = null;
    let imageX = 0;
    let imageY = 0;
    let imageScale = 1;
    let isDragging = false;
    let startX, startY;

    // Set canvas size to match frame natural size or a fixed square
    function initCanvas() {
        // Wait for frame to load
        if (frameImage.complete) {
            setupCanvas();
        } else {
            frameImage.onload = setupCanvas;
        }
    }

    function setupCanvas() {
        // Use a high resolution for the canvas
        const size = 1080;
        canvas.width = size;
        canvas.height = size;

        // Initial draw
        draw();
    }

    function draw() {
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw user image if exists
        if (userImage) {
            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;

            ctx.save();
            ctx.translate(centerX + imageX, centerY + imageY);
            ctx.scale(imageScale, imageScale);
            ctx.drawImage(userImage, -userImage.width / 2, -userImage.height / 2);
            ctx.restore();
        }

        // Draw frame on top
        // Draw frame to cover the canvas while maintaining aspect ratio if needed, 
        // but usually twibbon frames are square. We'll assume square for now or stretch to fit.
        ctx.drawImage(frameImage, 0, 0, canvas.width, canvas.height);
    }

    // Handle Image Upload
    imageUpload.addEventListener('change', function (e) {
        const file = e.target.files[0];
        if (file) {
            loadingOverlay.classList.remove('hidden');
            const reader = new FileReader();
            reader.onload = function (event) {
                const img = new Image();
                img.onload = function () {
                    userImage = img;
                    // Reset position and scale
                    imageX = 0;
                    imageY = 0;

                    // Calculate initial scale to fit image within canvas
                    const scaleX = canvas.width / img.width;
                    const scaleY = canvas.height / img.height;
                    imageScale = Math.max(scaleX, scaleY); // Cover strategy

                    zoomSlider.value = 1; // Reset slider visual
                    // We map slider 1 to the calculated "cover" scale

                    draw();
                    draw();
                    downloadBtn.disabled = false;
                    const saveBtn = document.getElementById('save-btn');
                    if (saveBtn) saveBtn.disabled = false;
                    zoomSlider.disabled = false;
                    zoomSlider.disabled = false;
                    loadingOverlay.classList.add('hidden');
                };
                img.src = event.target.result;
            };
            reader.readAsDataURL(file);
        }
    });

    // Handle Zoom
    zoomSlider.addEventListener('input', function (e) {
        if (!userImage) return;
        // Base scale is the "cover" scale calculated on load. 
        // But for simplicity, let's just use a multiplier on the current base.
        // Actually, let's make the slider control the scale directly relative to the initial fit.

        // Re-calculate base scale to be safe
        const scaleX = canvas.width / userImage.width;
        const scaleY = canvas.height / userImage.height;
        const baseScale = Math.max(scaleX, scaleY);

        imageScale = baseScale * parseFloat(this.value);
        draw();
    });

    // Handle Dragging
    canvas.addEventListener('mousedown', function (e) {
        if (!userImage) return;
        isDragging = true;
        const rect = canvas.getBoundingClientRect();
        // Calculate scale factor between CSS pixels and Canvas pixels
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;

        startX = (e.clientX - rect.left) * scaleX - imageX;
        startY = (e.clientY - rect.top) * scaleY - imageY;
        canvas.style.cursor = 'grabbing';
    });

    window.addEventListener('mousemove', function (e) {
        if (!isDragging) return;
        e.preventDefault();
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;

        const mouseX = (e.clientX - rect.left) * scaleX;
        const mouseY = (e.clientY - rect.top) * scaleY;

        imageX = mouseX - startX;
        imageY = mouseY - startY;
        draw();
    });

    window.addEventListener('mouseup', function () {
        isDragging = false;
        canvas.style.cursor = 'move';
    });

    // Touch support for mobile
    canvas.addEventListener('touchstart', function (e) {
        if (!userImage) return;
        isDragging = true;
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;

        const touch = e.touches[0];
        startX = (touch.clientX - rect.left) * scaleX - imageX;
        startY = (touch.clientY - rect.top) * scaleY - imageY;
    }, { passive: false });

    window.addEventListener('touchmove', function (e) {
        if (!isDragging) return;
        e.preventDefault(); // Prevent scrolling
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;

        const touch = e.touches[0];
        const mouseX = (touch.clientX - rect.left) * scaleX;
        const mouseY = (touch.clientY - rect.top) * scaleY;

        imageX = mouseX - startX;
        imageY = mouseY - startY;
        draw();
    }, { passive: false });

    window.addEventListener('touchend', function () {
        isDragging = false;
    });

    // Handle Download
    function downloadImage() {
        if (!userImage) return;

        const link = document.createElement('a');
        link.download = 'twibbon.png';
        link.href = canvas.toDataURL('image/png');
        link.click();

        // Track download
        const slug = window.location.pathname.split('/')[2]; // Assumes /campaign/<slug>/
        fetch(`/campaign/${slug}/download/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        });
    }

    downloadBtn.addEventListener('click', downloadImage);

    // Handle Save (Upload to server)
    const saveBtn = document.getElementById('save-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', function () {
            if (!userImage) return;

            // Show loading state
            saveBtn.disabled = true;
            saveBtn.innerHTML = '<svg class="animate-spin h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Menyimpan...';

            const dataURL = canvas.toDataURL('image/png');
            const slug = window.location.pathname.split('/')[2];

            fetch(`/campaign/${slug}/save/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ image: dataURL })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        window.location.href = data.redirect_url;
                    } else {
                        alert('Gagal menyimpan gambar. Silakan coba lagi.');
                        saveBtn.disabled = false;
                        saveBtn.innerHTML = '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path></svg> Simpan';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Terjadi kesalahan. Silakan coba lagi.');
                    saveBtn.disabled = false;
                    saveBtn.innerHTML = '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path></svg> Simpan';
                });
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    initCanvas();
});
