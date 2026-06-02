/**
 * Premium Canvas Particle Network Engine
 * Engineered for high-fps background animation and cursor-drift interaction.
 */

class ParticleNetwork {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.particles = [];
    this.mouse = { x: null, y: null, radius: 120 };
    
    // Performance presets based on screen dimensions
    this.maxParticles = window.innerWidth < 768 ? 25 : 60;
    this.connectionDistance = 100;
    this.baseSpeed = 0.4;

    this.init();
    this.animate();
    
    window.addEventListener('resize', () => this.handleResize());
    window.addEventListener('mousemove', (e) => this.handleMouseMove(e));
    window.addEventListener('mouseleave', () => this.handleMouseLeave());
  }

  init() {
    this.handleResize();
    this.particles = [];
    for (let i = 0; i < this.maxParticles; i++) {
      this.particles.push(new Particle(this.canvas.width, this.canvas.height, this.baseSpeed));
    }
  }

  handleResize() {
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
    this.maxParticles = window.innerWidth < 768 ? 25 : 60;
  }

  handleMouseMove(e) {
    this.mouse.x = e.clientX;
    this.mouse.y = e.clientY;
  }

  handleMouseLeave() {
    this.mouse.x = null;
    this.mouse.y = null;
  }

  animate() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    // Update and draw particles
    for (let i = 0; i < this.particles.length; i++) {
      this.particles[i].update(this.canvas.width, this.canvas.height, this.mouse);
      this.particles[i].draw(this.ctx);
    }
    
    this.drawConnections();
    requestAnimationFrame(() => this.animate());
  }

  drawConnections() {
    for (let i = 0; i < this.particles.length; i++) {
      for (let j = i + 1; j < this.particles.length; j++) {
        const dx = this.particles[i].x - this.particles[j].x;
        const dy = this.particles[i].y - this.particles[j].y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < this.connectionDistance) {
          // Fade opacity as distance increases
          const opacity = (1 - distance / this.connectionDistance) * 0.15;
          this.ctx.strokeStyle = `rgba(0, 240, 255, ${opacity})`;
          this.ctx.lineWidth = 0.8;
          this.ctx.beginPath();
          this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
          this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
          this.ctx.stroke();
        }
      }
    }
  }
}

class Particle {
  constructor(canvasWidth, canvasHeight, baseSpeed) {
    this.x = Math.random() * canvasWidth;
    this.y = Math.random() * canvasHeight;
    this.vx = (Math.random() - 0.5) * baseSpeed;
    this.vy = (Math.random() - 0.5) * baseSpeed;
    this.radius = Math.random() * 2 + 1;
    this.baseSpeed = baseSpeed;
    
    // Choose color (cyber-cyan or deep purple nodes)
    this.color = Math.random() > 0.4 ? 'rgba(0, 240, 255, 0.5)' : 'rgba(139, 92, 246, 0.4)';
  }

  draw(ctx) {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.fillStyle = this.color;
    ctx.fill();
  }

  update(canvasWidth, canvasHeight, mouse) {
    // Bounce off walls
    if (this.x < 0 || this.x > canvasWidth) this.vx = -this.vx;
    if (this.y < 0 || this.y > canvasHeight) this.vy = -this.vy;
    
    // Move particle
    this.x += this.vx;
    this.y += this.vy;

    // Mouse Interaction (Push/Drift away slightly)
    if (mouse.x !== null && mouse.y !== null) {
      const dx = this.x - mouse.x;
      const dy = this.y - mouse.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      
      if (dist < mouse.radius) {
        const force = (mouse.radius - dist) / mouse.radius;
        const angle = Math.atan2(dy, dx);
        this.x += Math.cos(angle) * force * 1.5;
        this.y += Math.sin(angle) * force * 1.5;
      }
    }
  }
}

// Initialise particle canvas on DOM content load
document.addEventListener('DOMContentLoaded', () => {
  new ParticleNetwork('particle-canvas');
});
