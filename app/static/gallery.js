let carouselContainer;
let slides;
let currentSlideIndex = 0;

let selectedOffer;

function nextSlide() {
    currentSlideIndex = (currentSlideIndex + 1) % slides.length; // Move to the next slide
    const translateValue = `translateX(-${currentSlideIndex * 100}%)`;
    slides.forEach(slide => slide.style.transform = translateValue);
}

function prevSlide() {
    currentSlideIndex = currentSlideIndex > 0 ? currentSlideIndex - 1 : slides.length - 1; // Move to the previous slide
    const translateValue = `translateX(-${currentSlideIndex * 100}%)`;
    slides.forEach(slide => slide.style.transform = translateValue);
}

function openOfferModal(offerId) {
    selectedOffer = offer.find(o => o.id == offerId);

    document.getElementById('modalImage').src = `/static/${selectedOffer.image_path}`;
    document.getElementById('modalTitle').textContent = selectedOffer.title;
    document.getElementById('modalDescription').textContent = selectedOffer.description;

    if (!isSelf) {
        const messageInput = document.getElementById('contact-artist-message')
        if (messageInput) {
            messageInput.hidden = false;
            messageInput.disabled = false;
        }
        const sendBtn = document.getElementById('contact-artist-btn')
        if (sendBtn) {
            sendBtn.disabled = false;
            sendBtn.value = 'Send (Ctrl+Enter)'
        }
    }

    var myModal = new bootstrap.Modal(document.getElementById('offerModal'), {
        keyboard: false
    });
    myModal.show();
}

function sendMessageFromInput() {
    const messageInput = document.getElementById('contact-artist-message')
    const sendBtn = document.getElementById('contact-artist-btn')
    const message = messageInput.value

    if (message.length <= 0) {
        return
    }

    if (selectedOffer === undefined) {
        return
    }

    send_message(message, [], selectedOffer.artist_id, () => {
        messageInput.hidden = true;
        messageInput.value = '';
        sendBtn.value = 'Sent!'
    })

    messageInput.disabled = true;
    sendBtn.disabled = true;
    sendBtn.value = 'Sending...'
}

document.addEventListener('DOMContentLoaded', function () {
    carouselContainer = document.querySelector(".carousel-container");
    slides = [...document.querySelectorAll(".slide")];

    const galleryImages = document.querySelectorAll('.gallery img');
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('enlargedImage');
    const modalTitle = document.getElementById('imageTitle');
    const modalDesc = document.getElementById('imageDesc');

    galleryImages.forEach(img => {
        img.addEventListener('click', function () {
            modal.hidden = false;
            modalImage.src = this.src;
            modalTitle.textContent = this.alt;
            modalDesc.textContent = 'Description for ' + this.alt;
        });
    });

    modal.addEventListener('click', function () {
        modal.hidden = true;
    });

    if (!isSelf) {
        document.getElementById('contact-artist-btn')?.addEventListener('click', sendMessageFromInput)
        document.getElementById('contact-artist-message')?.addEventListener('keydown', e => {
            if (e.target.disabled) {
                return
            }

            if (e.key === 'Enter' && e.ctrlKey) {
                sendMessageFromInput()
            }
        })
    }
})
