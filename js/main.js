// Wrap each letter in spans for all text nodes inside the container
function wrapLetters(containerSelector) {
  const container = document.querySelector(containerSelector);
  if (!container) return;

  function wrapTextNodes(node) {
    node.childNodes.forEach(child => {
      if (child.nodeType === Node.TEXT_NODE) {
        const text = child.textContent;
        const wrapped = text.split('').map(char => `<span>${char}</span>`).join('');
        const spanWrapper = document.createElement('span');
        spanWrapper.innerHTML = wrapped;
        child.replaceWith(spanWrapper);
      } else if (child.nodeType === Node.ELEMENT_NODE) {
        wrapTextNodes(child);
      }
    });
  }

  wrapTextNodes(container);
}
document.querySelectorAll('.timeline__block').forEach(block => {
  const desc = block.querySelector('.timeline__desc');
  
  // Create arrow element and insert it below title
  const arrow = document.createElement('span');
  arrow.classList.add('toggle-arrow');
  block.querySelector('.timeline__header').appendChild(arrow);
  
  // Initially hide description (height=0)
  desc.style.height = '0px';

  let open = false;

  arrow.addEventListener('click', () => {
    if (!open) {
      // Open description: animate height and opacity
      desc.classList.add('open');
      const height = desc.scrollHeight;
      anime({
        targets: desc,
        height: [0, height],
        easing: 'easeOutQuart',
        duration: 150, // was 400
      });
      arrow.classList.add('open');
    } else {
      // Close description: animate height to 0 and fade out opacity
      anime({
        targets: desc,
        height: [desc.scrollHeight, 0],
        easing: 'easeInQuart',
        duration: 150, // was 400
        complete: () => {
          desc.classList.remove('open');
        }
      });
      arrow.classList.remove('open');
    }
    open = !open;
  });
});
// Wrap each letter in spans for all text nodes inside the container
function wrapLetters(containerSelector) {
  const container = document.querySelector(containerSelector);
  if (!container) return;

  function wrapTextNodes(node) {
    node.childNodes.forEach(child => {
      if (child.nodeType === Node.TEXT_NODE) {
        const text = child.textContent;
        const wrapped = text.split('').map(char => `<span>${char}</span>`).join('');
        const spanWrapper = document.createElement('span');
        spanWrapper.innerHTML = wrapped;
        child.replaceWith(spanWrapper);
      } else if (child.nodeType === Node.ELEMENT_NODE) {
        wrapTextNodes(child);
      }
    });
  }

  wrapTextNodes(container);
}

// Call it on your container, e.g. 'body' or '.my-text-container'
wrapLetters('body');

// Call it on your container, e.g. 'body' or '.my-text-container'
wrapLetters('body');

// Select the element with your class
var target = document.querySelector('.text-pretitle.with-line');

// Split the text into individual characters
var textContent = target.textContent;
target.innerHTML = textContent.split('').map(char => `<span class="char">${char}</span>`).join('');

// Animate each character
anime({
  targets: '.text-pretitle.with-line .char',
  translateY: [
    { value: '-2.75rem', easing: 'easeOutExpo', duration: 200 }, // was 600
    { value: 0, easing: 'easeOutBounce', duration: 200, delay: 30 } // was 800, 100
  ],
  rotate: {
    value: '-1turn',
    delay: 0
  },
  delay: anime.stagger(15), // was 50
  easing: 'easeInOutCirc',
  loopDelay: 300, // was 1000
  loop: true
});

/* ===================================================================
 *
 * ------------------------------------------------------------------- */

(function(html) {

    "use strict";

    html.className = html.className.replace(/\bno-js\b/g, '') + ' js ';



   /* Animations
    * -------------------------------------------------- */
    const tl = anime.timeline( {
        easing: 'easeInOutCubic',
        duration: 300, // was 800
        autoplay: false
    })
    .add({
        targets: '#loader',
        opacity: 0,
        duration: 300, // was 1000
        begin: function(anim) {
            window.scrollTo(0, 0);
        }
    })
    .add({
        targets: '#preloader',
        opacity: 0,
        complete: function(anim) {
            document.querySelector("#preloader").style.visibility = "hidden";
            document.querySelector("#preloader").style.display = "none";
        }
    })
    .add({
        targets: '.s-header',
        translateY: [-100, 0],
        opacity: [0, 1]
    }, '-=100') // was '-=200'
    .add({
        targets: [ '.s-intro .text-pretitle', '.s-intro .text-huge-title'],
        translateX: [100, 0],
        opacity: [0, 1],
        delay: anime.stagger(100) // was 400
    })
    .add({
        targets: '.circles span',
        keyframes: [
            {opacity: [0, .3]},
            {opacity: [.3, .1], delay: anime.stagger(30, {direction: 'reverse'})} // was 100
        ],
        delay: anime.stagger(30, {direction: 'reverse'}) // was 100
    })
    .add({
        targets: '.intro-social li',
        translateX: [-50, 0],
        opacity: [0, 1],
        delay: anime.stagger(30, {direction: 'reverse'}) // was 100
    })
    .add({
        targets: '.intro-scrolldown',
        translateY: [100, 0],
        opacity: [0, 1]
    }, '-=300');



   /* Preloader
    * -------------------------------------------------- */
    const ssPreloader = function() {

        const preloader = document.querySelector('#preloader');
        if (!preloader) return;
        
        window.addEventListener('load', function() {
            document.querySelector('html').classList.remove('ss-preload');
            document.querySelector('html').classList.add('ss-loaded');

            document.querySelectorAll('.ss-animated').forEach(function(item){
                item.classList.remove('ss-animated');
            });

            tl.play();
        });

        // force page scroll position to top at page refresh
        // window.addEventListener('beforeunload' , function () {
        //     // window.scrollTo(0, 0);
        // });

    }; // end ssPreloader


   /* Mobile Menu
    * ---------------------------------------------------- */ 
    const ssMobileMenu = function() {

        const toggleButton = document.querySelector('.mobile-menu-toggle');
        const mainNavWrap = document.querySelector('.main-nav-wrap');
        const siteBody = document.querySelector("body");

        if (!(toggleButton && mainNavWrap)) return;

        toggleButton.addEventListener('click', function(event) {
            event.preventDefault();
            toggleButton.classList.toggle('is-clicked');
            siteBody.classList.toggle('menu-is-open');
        });

        mainNavWrap.querySelectorAll('.main-nav a').forEach(function(link) {
            link.addEventListener("click", function(event) {

                // at 800px and below
                if (window.matchMedia('(max-width: 800px)').matches) {
                    toggleButton.classList.toggle('is-clicked');
                    siteBody.classList.toggle('menu-is-open');
                }
            });
        });

        window.addEventListener('resize', function() {

            // above 800px
            if (window.matchMedia('(min-width: 801px)').matches) {
                if (siteBody.classList.contains('menu-is-open')) siteBody.classList.remove('menu-is-open');
                if (toggleButton.classList.contains("is-clicked")) toggleButton.classList.remove("is-clicked");
            }
        });

    }; // end ssMobileMenu


   /* Highlight active menu link on pagescroll
    * ------------------------------------------------------ */
    const ssScrollSpy = function() {

        const sections = document.querySelectorAll(".target-section");

        // Add an event listener listening for scroll
        window.addEventListener("scroll", navHighlight);

        function navHighlight() {
        
            // Get current scroll position
            let scrollY = window.pageYOffset;
        
            // Loop through sections to get height(including padding and border), 
            // top and ID values for each
            sections.forEach(function(current) {
                const sectionHeight = current.offsetHeight;
                const sectionTop = current.offsetTop - 50;
                const sectionId = current.getAttribute("id");
            
               /* If our current scroll position enters the space where current section 
                * on screen is, add .current class to parent element(li) of the thecorresponding 
                * navigation link, else remove it. To know which link is active, we use 
                * sectionId variable we are getting while looping through sections as 
                * an selector
                */
                if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
                    document.querySelector(".main-nav a[href*=" + sectionId + "]").parentNode.classList.add("current");
                } else {
                    document.querySelector(".main-nav a[href*=" + sectionId + "]").parentNode.classList.remove("current");
                }
            });
        }

    }; // end ssScrollSpy


   /* Animate elements if in viewport
    * ------------------------------------------------------ */
    const ssViewAnimate = function() {

        const blocks = document.querySelectorAll("[data-animate-block]");

        window.addEventListener("scroll", viewportAnimation);

        function viewportAnimation() {

            let scrollY = window.pageYOffset;

            blocks.forEach(function(current) {

                const viewportHeight = window.innerHeight;
                const triggerTop = (current.offsetTop + (viewportHeight * .2)) - viewportHeight;
                const blockHeight = current.offsetHeight;
                const blockSpace = triggerTop + blockHeight;
                const inView = scrollY > triggerTop && scrollY <= blockSpace;
                const isAnimated = current.classList.contains("ss-animated");

                if (inView && (!isAnimated)) {
                    anime({
                        targets: current.querySelectorAll("[data-animate-el]"),
                        opacity: [0, 1],
                        translateY: [100, 0],
                        delay: anime.stagger(80, {start: 40}), // was 400, 200
                        duration: 250, // was 800
                        easing: 'easeInOutCubic',
                        begin: function(anim) {
                            current.classList.add("ss-animated");
                        }
                    });
                }
            });
        }

    }; // end ssViewAnimate


   /* Swiper
    * ------------------------------------------------------ */ 
    const ssSwiper = function() {

        const mySwiper = new Swiper('.swiper-container', {

            slidesPerView: 1,
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },
            breakpoints: {
                // when window width is > 400px
                401: {
                    slidesPerView: 1,
                    spaceBetween: 20
                },
                // when window width is > 800px
                801: {
                    slidesPerView: 2,
                    spaceBetween: 32
                },
                // when window width is > 1200px
                1201: {
                    slidesPerView: 2,
                    spaceBetween: 80
                }
            }
         });

    }; // end ssSwiper


   /* Lightbox
    * ------------------------------------------------------ */
    const ssLightbox = function() {

        const folioLinks = document.querySelectorAll('.folio-list__item-link');
        const modals = [];

        folioLinks.forEach(function(link) {
            let modalbox = link.getAttribute('href');
            let instance = basicLightbox.create(
                document.querySelector(modalbox),
                {
                    onShow: function(instance) {
                        //detect Escape key press
                        document.addEventListener("keydown", function(event) {
                            event = event || window.event;
                            if (event.keyCode === 27) {
                                instance.close();
                            }
                        });
                    }
                }
            )
            modals.push(instance);
        });

        folioLinks.forEach(function(link, index) {
            link.addEventListener("click", function(event) {
                event.preventDefault();
                modals[index].show();
            });
        });

    };  // end ssLightbox


   /* Alert boxes
    * ------------------------------------------------------ */
    const ssAlertBoxes = function() {

        const boxes = document.querySelectorAll('.alert-box');
  
        boxes.forEach(function(box){

            box.addEventListener('click', function(event) {
                if (event.target.matches(".alert-box__close")) {
                    event.stopPropagation();
                    event.target.parentElement.classList.add("hideit");

                    setTimeout(function(){
                        box.style.display = "none";
                    }, 500)
                }    
            });

        })

    }; // end ssAlertBoxes


   /* Smoothscroll
    * ------------------------------------------------------ */
    const ssMoveTo = function(){

        const easeFunctions = {
            easeInQuad: function (t, b, c, d) {
                t /= d;
                return c * t * t + b;
            },
            easeOutQuad: function (t, b, c, d) {
                t /= d;
                return -c * t* (t - 2) + b;
            },
            easeInOutQuad: function (t, b, c, d) {
                t /= d/2;
                if (t < 1) return c/2*t*t + b;
                t--;
                return -c/2 * (t*(t-2) - 1) + b;
            },
            easeInOutCubic: function (t, b, c, d) {
                t /= d/2;
                if (t < 1) return c/2*t*t*t + b;
                t -= 2;
                return c/2*(t*t*t + 2) + b;
            }
        }

        const triggers = document.querySelectorAll('.smoothscroll');
        
        const moveTo = new MoveTo({
            tolerance: 0,
            duration: 1200,
            easing: 'easeInOutCubic',
            container: window
        }, easeFunctions);

        triggers.forEach(function(trigger) {
            moveTo.registerTrigger(trigger);
        });

    }; // end ssMoveTo


   /* Initialize
    * ------------------------------------------------------ */
    (function ssInit() {

        ssPreloader();
        ssMobileMenu();
        ssScrollSpy();
        ssViewAnimate();
        ssSwiper();
        ssLightbox();
        ssAlertBoxes();
        ssMoveTo();

    })();

})(document.documentElement);

// Pause rainbow animation on scroll, resume after scrolling stops
let rainbowTimeout;
window.addEventListener('scroll', function() {
  document.querySelectorAll('.rainbow').forEach(el => {
    el.style.animationPlayState = 'paused';
  });
  clearTimeout(rainbowTimeout);
  rainbowTimeout = setTimeout(() => {
    document.querySelectorAll('.rainbow').forEach(el => {
      el.style.animationPlayState = 'running';
    });
  }, 50); // resume after 300ms of no scroll
});