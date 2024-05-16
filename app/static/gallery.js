let carouselContainer;
let slides;
let currentSlideIndex = 0;

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
    const selectedOffer = offer.find(o => o.id == offerId);

    document.getElementById('modalImage').src = `/static/${selectedOffer.image_path}`;
    document.getElementById('modalTitle').textContent = selectedOffer.title;
    document.getElementById('modalDescription').textContent = selectedOffer.description;

    var myModal = new bootstrap.Modal(document.getElementById('offerModal'), {
        keyboard: false
    });
    myModal.show();
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
})
