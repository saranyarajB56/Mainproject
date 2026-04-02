document.addEventListener("DOMContentLoaded", () => {
    // Like button toggle
    const likeButtons = document.querySelectorAll(".like-btn");
    likeButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            btn.classList.toggle("liked");
            if (btn.classList.contains("liked")) {
                btn.style.color = "red";
            } else {
                btn.style.color = "black";
            }
        });
    });

    // Simple alert for messages sent
    const messageForm = document.querySelector("form[action*='messages']");
    if (messageForm) {
        messageForm.addEventListener("submit", () => {
            alert("Message sent!");
        });
    }
});

document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("nav-toggle");
    const links = document.getElementById("nav-links");

    toggle.addEventListener("click", () => {
        links.classList.toggle("active");
    });
});