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
const projectCards = Array.from(document.querySelectorAll("[data-scroll-project]"));
const workCategories = Array.from(document.querySelectorAll(".work-category"));
const projectGroups = dotLinks
  .map((link) => ({
    name: link.dataset.project,
    link,
    cards: projectCards.filter((card) => card.dataset.scrollProject === link.dataset.project),
  }))
  .filter((group) => group.cards.length);

if (sectionDots && workSection && projectGroups.length) {
  let scheduled = false;

  const updateSectionDots = () => {
    const marker = window.innerHeight * 0.5;
    const firstCardBounds = projectGroups[0].cards[0].getBoundingClientRect();
    const lastGroup = projectGroups[projectGroups.length - 1];
    const lastCardBounds = lastGroup.cards[lastGroup.cards.length - 1].getBoundingClientRect();
    const isVisible = firstCardBounds.top <= marker && lastCardBounds.bottom >= marker;

    sectionDots.classList.toggle("is-visible", isVisible);
    document.body.classList.toggle("project-focus-enabled", isVisible);

    if (!isVisible) {
      workCategories.forEach((category) => category.classList.remove("is-scroll-active-section"));
      projectGroups.forEach((group) => {
        group.link.classList.remove("is-active");
        group.link.removeAttribute("aria-current");
        group.cards.forEach((card) => card.classList.remove("is-scroll-active"));
      });
      scheduled = false;
      return;
    }

    const activeGroup = projectGroups.reduce((closest, group) => {
      const groupCenter = group.cards.reduce((total, card) => {
        const bounds = card.getBoundingClientRect();
        return total + bounds.top + bounds.height / 2;
      }, 0) / group.cards.length;
      const distance = Math.abs(groupCenter - marker);

      return distance < closest.distance ? { group, distance } : closest;
    }, { group: projectGroups[0], distance: Number.POSITIVE_INFINITY }).group;

    workCategories.forEach((category) => category.classList.remove("is-scroll-active-section"));
    activeGroup.cards[0].closest(".work-category")?.classList.add("is-scroll-active-section");

    projectGroups.forEach((group) => {
      const isActive = group === activeGroup;
      group.link.classList.toggle("is-active", isActive);
      if (isActive) {
        group.link.setAttribute("aria-current", "true");
      } else {
        group.link.removeAttribute("aria-current");
      }

      group.cards.forEach((card) => card.classList.toggle("is-scroll-active", isActive));
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
