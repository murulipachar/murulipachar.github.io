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

    this.updateColors();
    this.init();
    this.animate();
    
    window.addEventListener('resize', () => this.handleResize());
    window.addEventListener('mousemove', (e) => this.handleMouseMove(e));
    window.addEventListener('mouseleave', () => this.handleMouseLeave());
    window.addEventListener('theme-changed', () => this.updateColors());
  }

  updateColors() {
    try {
      const style = getComputedStyle(document.documentElement);
      const valCyan = style.getPropertyValue('--accent-cyan');
      const valPurple = style.getPropertyValue('--accent-purple');
      
      const rawCyan = (valCyan ? valCyan.trim() : '') || '#00f2fe';
      const rawPurple = (valPurple ? valPurple.trim() : '') || '#9d4edd';
      
      this.cyanRgb = this.hexToRgb(rawCyan) || { r: 0, g: 242, b: 254 };
      this.purpleRgb = this.hexToRgb(rawPurple) || { r: 157, g: 77, b: 221 };
    } catch (e) {
      console.warn("Could not update dynamic particle colors, falling back:", e);
      this.cyanRgb = { r: 0, g: 242, b: 254 };
      this.purpleRgb = { r: 157, g: 77, b: 221 };
    }
  }

  hexToRgb(hex) {
    if (hex.startsWith('rgb')) {
      const match = hex.match(/\d+/g);
      return match ? { r: parseInt(match[0]), g: parseInt(match[1]), b: parseInt(match[2]) } : null;
    }
    const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
    const fullHex = hex.replace(shorthandRegex, (m, r, g, b) => r + r + g + g + b + b);
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(fullHex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
  }

  init() {
    this.handleResize();
    this.particles = [];
    for (let i = 0; i < this.maxParticles; i++) {
      this.particles.push(new Particle(this.canvas.width, this.canvas.height, this.baseSpeed, this));
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
          this.ctx.strokeStyle = `rgba(${this.cyanRgb.r}, ${this.cyanRgb.g}, ${this.cyanRgb.b}, ${opacity})`;
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
  constructor(canvasWidth, canvasHeight, baseSpeed, network) {
    this.network = network;
    this.x = Math.random() * canvasWidth;
    this.y = Math.random() * canvasHeight;
    this.vx = (Math.random() - 0.5) * baseSpeed;
    this.vy = (Math.random() - 0.5) * baseSpeed;
    this.radius = Math.random() * 2 + 1;
    this.baseSpeed = baseSpeed;
    this.isCyan = Math.random() > 0.4;
  }

  draw(ctx) {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    const rgb = this.isCyan ? this.network.cyanRgb : this.network.purpleRgb;
    ctx.fillStyle = `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${this.isCyan ? 0.5 : 0.4})`;
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
