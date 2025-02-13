let currentSlide = 0;

        const slides = document.querySelectorAll('#highlight .slide');
        const totalSlides = slides.length;
        const slide_time = 7000;

        let auto_slide = setInterval(function() {
            currentSlide = (currentSlide + 1) % totalSlides;
            updateSlidePosition();
        }, slide_time);
        
        document.getElementById('next-slide').addEventListener('click', () => {
            currentSlide = (currentSlide + 1) % totalSlides;
            updateSlidePosition();
            clearInterval(auto_slide);
            auto_slide = setInterval(function() {
                currentSlide = (currentSlide + 1) % totalSlides;
                updateSlidePosition();
            }, slide_time);
        });
        
        document.getElementById('prev-slide').addEventListener('click', () => {
            currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
            updateSlidePosition();
            clearInterval(auto_slide);
            auto_slide = setInterval(function() {
                currentSlide = (currentSlide + 1) % totalSlides;
                updateSlidePosition();
            }, slide_time);
        });

        function updateSlidePosition() {
            const slideContainer = document.querySelector('#highlight .slide-container');
            slideContainer.style.transform = `translateX(-${currentSlide * 100}%)`;
        }