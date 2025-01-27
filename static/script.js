// Get the lightbox elements
const lightbox = document.getElementById('lightbox');
const lightboxVideo = document.getElementById('lightbox-video');
const closeLightbox = document.getElementById('close-lightbox');

// Add click listeners to all videos in the container
const videoElements = document.querySelectorAll('.video');
videoElements.forEach(video => {
    video.addEventListener('click', () => {
        const videoSrc = video.querySelector('source').src;

        // Show the lightbox and set the video source
        lightboxVideo.src = videoSrc;
        lightbox.classList.remove('hidden');
        lightboxVideo.play();
    });
});

// Close the lightbox
closeLightbox.addEventListener('click', () => {
    lightbox.classList.add('hidden');
    lightboxVideo.pause();
    lightboxVideo.src = ""; // Clear the video source to stop playback
});

// Close the lightbox when clicking outside the video
lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) {
        closeLightbox.click();
    }
});

// Automatically scroll to the next video when the last one ends
videoElements.forEach(video => {
    video.addEventListener('ended', () => {
        const nextVideo = video.nextElementSibling;
        if (nextVideo) {
            nextVideo.scrollIntoView({ behavior: 'smooth' });
        }
    });
});
