document.addEventListener("DOMContentLoaded", () => {
    const videos = document.querySelectorAll(".video");
    const likeButtons = document.querySelectorAll(".like-btn");
    const commentButtons = document.querySelectorAll(".comment-btn");
    const commentBox = document.querySelector(".comment-box");
    const postButton = document.querySelector(".post-btn");
    const cancelButton = document.querySelector(".cancel-btn");
    const commentInput = document.querySelector(".comment-box textarea");

    let currentVideoIndex = 0;
    let currentVideoId = null;
    
    // Remove muted attribute from all videos
    videos.forEach(video => {
        video.muted = false;
    });

    // Auto-play first video
    if (videos.length > 0) {
        const firstVideo = videos[0];
        firstVideo.muted = false;
        firstVideo.play().catch(error => {
            console.log("Autoplay failed:", error);
        });
    }

    function handleVideoPlayback() {
        let closestVideo = null;
        let minDistance = Infinity;

        videos.forEach((video, index) => {
            const rect = video.getBoundingClientRect();
            const distance = Math.abs(rect.top);
            
            // Pause videos that are out of view
            if (Math.abs(rect.top) > window.innerHeight * 0.5) {
                video.pause();
            }

            if (distance < minDistance) {
                minDistance = distance;
                closestVideo = { video, index };
            }
        });

        if (closestVideo && closestVideo.index !== currentVideoIndex) {
            // Pause the currently playing video
            videos[currentVideoIndex].pause();
            currentVideoIndex = closestVideo.index;
            
            // Play the new video
            const videoToPlay = closestVideo.video;
            videoToPlay.muted = false;
            videoToPlay.play().catch(error => {
                console.log("Playback failed:", error);
                // If autoplay fails, show a play button or handle it appropriately
            });
        }
    }

    // Debounce the scroll handler to improve performance
    let scrollTimeout;
    window.addEventListener("scroll", () => {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            handleVideoPlayback();
        }, 50);
    });

    // Add click-to-play/pause functionality
    videos.forEach(video => {
        video.addEventListener('click', () => {
            if (video.paused) {
                // Pause all other videos first
                videos.forEach(v => {
                    if (v !== video) v.pause();
                });
                video.muted = false;
                video.play();
            } else {
                video.pause();
            }
        });
    });

    // Like button handler
    likeButtons.forEach((btn) => {
        btn.addEventListener("click", async () => {
            const videoId = btn.dataset.videoId;
            const likeCountElement = document.getElementById(`likes-count-${videoId}`);
            const likeImg = btn.querySelector('img');

            try {
                const response = await fetch("/like", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ video_id: videoId })
                });

                const data = await response.json();
                
                if (data.success) {
                    likeCountElement.textContent = data.likes;
                    
                    // Update like button appearance
                    if (data.action === 'liked') {
                        likeImg.style.filter = 'brightness(0) saturate(100%) invert(23%) sepia(91%) saturate(6645%) hue-rotate(356deg) brightness(101%) contrast(121%)'; // Red color
                    } else {
                        likeImg.style.filter = ''; // Reset to original color
                    }
                } else {
                    alert(data.message || "Error updating like");
                }
            } catch (error) {
                console.error("Error liking video:", error);
            }
        });
    });

    // Comment button handler
    commentButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
            currentVideoId = btn.dataset.videoId;
            commentBox.style.display = "block";
        });
    });

    // Cancel comment handler
    cancelButton.addEventListener("click", () => {
        commentBox.style.display = "none";
        commentInput.value = "";
    });

    // Post comment handler
    postButton.addEventListener("click", async () => {
        const commentText = commentInput.value.trim();

        if (commentText) {
            try {
                const response = await fetch("/comment", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ video_id: currentVideoId, comment: commentText })
                });

                const data = await response.json();
                if (data.success) {
                    alert("Comment posted!");
                    commentInput.value = "";
                }
            } catch (error) {
                console.error("Error posting comment:", error);
            }
        }

        commentBox.style.display = "none";
    });

    // Add login/register button handlers
    const loginBtn = document.getElementById("login-btn");
    const registerBtn = document.getElementById("register-btn");
    const logoutBtn = document.getElementById("logout-btn");

    if (loginBtn) {
        loginBtn.addEventListener("click", () => {
            const username = prompt("Enter username:");
            const password = prompt("Enter password:");

            if (username && password) {
                fetch("/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, password })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.reload(); // Reload the page after successful login
                    } else {
                        alert(data.message || "Login failed");
                    }
                })
                .catch(error => {
                    console.error("Error logging in:", error);
                    alert("Error logging in. Please try again.");
                });
            }
        });
    }

    if (registerBtn) {
        registerBtn.addEventListener("click", () => {
            const username = prompt("Choose a username:");
            const password = prompt("Choose a password:");

            if (username && password) {
                fetch("/register", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, password })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert("Registration successful! Please log in.");
                    } else {
                        alert(data.message || "Registration failed");
                    }
                })
                .catch(error => {
                    console.error("Error registering:", error);
                    alert("Error registering. Please try again.");
                });
            }
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            window.location.href = "/logout";  // Use direct navigation for logout
        });
    }
});