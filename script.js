const currentYear = document.querySelector("#current-year");

if (currentYear) {
  currentYear.textContent = new Date().getFullYear().toString();
}

window.addEventListener("load", () => {
  if (window.lucide) {
    window.lucide.createIcons();
  }
});

const sectionDots = document.querySelector(".section-dots");
const dotLinks = Array.from(document.querySelectorAll(".section-dot"));
const workSection = document.querySelector("#work");
const workSections = dotLinks
  .map((link) => document.getElementById(link.dataset.section))
  .filter(Boolean);

if (sectionDots && workSection && workSections.length) {
  let scheduled = false;

  const updateSectionDots = () => {
    const marker = window.innerHeight * 0.48;
    const workBounds = workSection.getBoundingClientRect();
    const isVisible = workBounds.top < window.innerHeight * 0.72 && workBounds.bottom > window.innerHeight * 0.28;

    sectionDots.classList.toggle("is-visible", isVisible);

    let activeSection = workSections[0];
    workSections.forEach((section) => {
      if (section.getBoundingClientRect().top <= marker) {
        activeSection = section;
      }
    });

    dotLinks.forEach((link) => {
      const isActive = link.dataset.section === activeSection.id;
      link.classList.toggle("is-active", isActive);
      if (isActive) {
        link.setAttribute("aria-current", "true");
      } else {
        link.removeAttribute("aria-current");
      }
    });

    scheduled = false;
  };

  const scheduleUpdate = () => {
    if (!scheduled) {
      scheduled = true;
      window.requestAnimationFrame(updateSectionDots);
    }
  };

  window.addEventListener("scroll", scheduleUpdate, { passive: true });
  window.addEventListener("resize", scheduleUpdate);
  updateSectionDots();
}
