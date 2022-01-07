/*
Made with minimal javascript and canvas understanding by https://github.com/schlopp
Feel free to completely rewrite this code, I'm happy as long as it works.
*/

var pageHeight = 0;

const particlesCanvas = document.getElementById("particles-canvas");
const particlesCtx = particlesCanvas.getContext("2d");
particlesCanvas.width = window.innerWidth - 8;
particlesCanvas.height = document.body.getBoundingClientRect().height;

class FallingParticle {
    constructor(x, y, reverse) {
        this.x = x;
        this.y = y;
        this.reverse = reverse;
        this.size = Math.random() * 0.5 + 1;
        this.weight = Math.random() * 2 + 2;
        this.directionX = Math.random() * 4 - 2;
        this.state = 0;
        this.allowedCycles = Math.random() * 50 + 50;
        this.cycles = 0;
    }
    update() {
        this.cycles++;
        this.weight -= 0.04;
        if (this.reverse) {
            this.y -= this.weight;
        } else {
            this.y += this.weight;
        }
        this.x += this.directionX;
        if (this.cycles > this.allowedCycles) {
            this.state += 1;
        }
    }
    draw() {
        if (this.state === 0) {
            particlesCtx.fillStyle = "#3500d4";
            particlesCtx.beginPath();
            particlesCtx.shadowColor = "#3500d4";
            particlesCtx.shadowBlur = this.size;
            particlesCtx.arc(this.x, this.y, this.size, 0, Math.PI * 2, false);
            particlesCtx.closePath();
            particlesCtx.fill();
        } else if (0 < this.state && this.state < 100) {
            particlesCtx.fillStyle = `rgba(53, 0, 212, ${1 - this.state / 100}`;
            particlesCtx.beginPath();
            particlesCtx.arc(this.x, this.y, this.size, 0, Math.PI * 2, false);
            particlesCtx.closePath();
            particlesCtx.fill();
        } else {
            particlesCtx.clearRect(this.x, this.y, this.size, this.size);
        }
    }
}

function spawnParticles(top) {
    var particleCount = 300;
    var particles = [];
    for (let i = 0; i < particleCount; i++) {
        if (top) {
            particles.push(
                new FallingParticle(
                    Math.random() * particlesCanvas.width,
                    Math.random() * -500 - 10,
                    false
                )
            );
        } else {
            particles.push(
                new FallingParticle(
                    Math.random() * particlesCanvas.width,
                    particlesCanvas.clientHeight + Math.random() * 500 + 10,
                    true
                )
            );
        }
    }
    function animate() {
        particlesCtx.clearRect(
            0,
            0,
            particlesCanvas.width,
            particlesCanvas.height
        );
        particles.forEach((particle) => {
            particle.update();
            particle.draw();
        });
        requestAnimationFrame(animate);
    }
    animate();
}

window.addEventListener("scroll", () => {
    console.log(window.innerHeight + window.scrollY);
    if (!window.scrollY) {
        console.log("TOP!");
        spawnParticles(true);
    }
    if (window.innerHeight + window.scrollY >= document.body.scrollHeight) {
        console.log("BOTTOM!");
        spawnParticles(false);
    }
});

window.addEventListener("resize", () => {
    console.log(window.innerHeight + window.scrollY);
    particlesCanvas.width = window.innerWidth - 8;
    particlesCanvas.height = document.body.getBoundingClientRect().height;
});
