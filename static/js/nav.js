// Mobile Navigation

const mobileToggle = document.getElementById('mobileToggle');
const mobileNav = document.getElementById('mobileNav');
const mobileClose = document.getElementById('mobileClose');
const mobileOverlay = document.getElementById('mobileOverlay');

function openMobileNav() {
  mobileNav.classList.add('active');
  mobileOverlay.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeMobileNav() {
  mobileNav.classList.remove('active');
  mobileOverlay.classList.remove('active');
  document.body.style.overflow = '';
}

if (mobileToggle) mobileToggle.addEventListener('click', openMobileNav);
if (mobileClose) mobileClose.addEventListener('click', closeMobileNav);
if (mobileOverlay) mobileOverlay.addEventListener('click', closeMobileNav);

document.querySelectorAll('.mobile-nav-menu .nav-link:not([data-dropdown-toggle]), .quick-action, .dropdown-item').forEach(link => {
  link.addEventListener('click', () => {
    setTimeout(closeMobileNav, 150);
  });
});

document.querySelectorAll('[data-dropdown-toggle]').forEach(el => {
  const id = el.getAttribute('data-target');
  let touchStarted = false;
  
  el.addEventListener('touchstart', (e) => {
    touchStarted = true;
    e.preventDefault();
    e.stopPropagation();
    const dropdown = document.getElementById(id);
    const isExpanded = dropdown && dropdown.classList.contains('show');
    document.querySelectorAll('.mobile-dropdown-content.show').forEach(dd => {
      if (dd.id !== id) dd.classList.remove('show');
    });
    if (dropdown) {
      dropdown.classList.toggle('show', !isExpanded);
    }
    el.setAttribute('aria-expanded', !isExpanded ? 'true' : 'false');
    const chevron = el.querySelector('.bi-chevron-down');
    if (chevron) {
      chevron.style.transform = !isExpanded ? 'rotate(180deg)' : 'rotate(0deg)';
    }
  }, { passive: false });
  
  el.addEventListener('click', (e) => {
    if (touchStarted) { touchStarted = false; return; }
    e.preventDefault();
    e.stopPropagation();
    const dropdown = document.getElementById(id);
    const isExpanded = dropdown && dropdown.classList.contains('show');
    document.querySelectorAll('.mobile-dropdown-content.show').forEach(dd => {
      if (dd.id !== id) dd.classList.remove('show');
    });
    if (dropdown) {
      dropdown.classList.toggle('show', !isExpanded);
    }
    el.setAttribute('aria-expanded', !isExpanded ? 'true' : 'false');
    const chevron = el.querySelector('.bi-chevron-down');
    if (chevron) {
      chevron.style.transform = !isExpanded ? 'rotate(180deg)' : 'rotate(0deg)';
    }
  });
});

// Close open mobile dropdowns when clicking/tapping outside them within mobile nav
document.addEventListener('click', (e) => {
  const withinMobileNav = e.target.closest('#mobileNav');
  const isToggle = e.target.closest('[data-dropdown-toggle]');
  if (withinMobileNav && !isToggle) {
    document.querySelectorAll('.mobile-dropdown-content.show').forEach(dd => dd.classList.remove('show'));
    document.querySelectorAll('[data-dropdown-toggle][aria-expanded="true"]').forEach(t => t.setAttribute('aria-expanded', 'false'));
    document.querySelectorAll('.mobile-nav-menu .nav-link .bi-chevron-down').forEach(c => c.style.transform = 'rotate(0deg)');
  }
}, { passive: true });

document.querySelectorAll('.mobile-dropdown-item').forEach(item => {
  item.addEventListener('click', () => {
    document.querySelectorAll('.mobile-dropdown-content.show').forEach(dd => dd.classList.remove('show'));
    document.querySelectorAll('[data-dropdown-toggle][aria-expanded="true"]').forEach(t => t.setAttribute('aria-expanded', 'false'));
    document.querySelectorAll('.mobile-nav-menu .nav-link .bi-chevron-down').forEach(c => c.style.transform = 'rotate(0deg)');
    setTimeout(closeMobileNav, 150);
  });
});

// Header scroll effect
const header = document.getElementById('header');
let lastScroll = 0;
window.addEventListener('scroll', () => {
  const currentScroll = window.pageYOffset;
  if (currentScroll > 50) {
    header && header.classList.add('scrolled');
  } else {
    header && header.classList.remove('scrolled');
  }
  lastScroll = currentScroll;
});

// Close mobile nav on escape
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && mobileNav && mobileNav.classList.contains('active')) {
    closeMobileNav();
  }
});

// Close mobile nav on window resize
let resizeTimer;
window.addEventListener('resize', () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    if (window.innerWidth > 991) {
      closeMobileNav();
    }
  }, 250);
});
