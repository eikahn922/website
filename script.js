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

const expandableGalleryImages = Array.from(document.querySelectorAll(".package-media img"));
const imageLightbox = document.querySelector(".image-lightbox");
const lightboxImage = imageLightbox?.querySelector(".lightbox-image");
const lightboxCaption = imageLightbox?.querySelector(".lightbox-caption");
const lightboxCount = imageLightbox?.querySelector(".lightbox-count");
const lightboxClose = imageLightbox?.querySelector(".lightbox-close");
const lightboxPrevious = imageLightbox?.querySelector(".lightbox-previous");
const lightboxNext = imageLightbox?.querySelector(".lightbox-next");
const galleryOpenButton = document.querySelector(".gallery-open-button");

if (
  expandableGalleryImages.length &&
  imageLightbox &&
  lightboxImage &&
  lightboxCaption &&
  lightboxCount &&
  lightboxClose &&
  lightboxPrevious &&
  lightboxNext
) {
  let currentLightboxIndex = 0;
  let lightboxReturnFocus = null;

  const imageTitle = (image) => {
    const sectionTitle = image.closest(".package-version")?.querySelector(".package-version-title")?.textContent?.trim();
    const imageLabel = image.closest(".case-media-group")?.querySelector(".case-media-label")?.textContent?.trim();
    return [sectionTitle, imageLabel].filter(Boolean).join(" · ");
  };

  const showLightboxImage = (index) => {
    currentLightboxIndex = (index + expandableGalleryImages.length) % expandableGalleryImages.length;
    const sourceImage = expandableGalleryImages[currentLightboxIndex];
    lightboxImage.src = sourceImage.currentSrc || sourceImage.src;
    lightboxImage.alt = sourceImage.alt;
    lightboxCaption.textContent = imageTitle(sourceImage);
    lightboxCount.textContent = `${currentLightboxIndex + 1} / ${expandableGalleryImages.length}`;
  };

  const openLightbox = (index) => {
    lightboxReturnFocus = document.activeElement;
    showLightboxImage(index);
    imageLightbox.hidden = false;
    document.body.classList.add("lightbox-open");
    lightboxClose.focus();
  };

  const closeLightbox = () => {
    imageLightbox.hidden = true;
    lightboxImage.removeAttribute("src");
    document.body.classList.remove("lightbox-open");
    if (lightboxReturnFocus instanceof HTMLElement) {
      lightboxReturnFocus.focus();
    }
  };

  expandableGalleryImages.forEach((image, index) => {
    image.tabIndex = 0;
    image.setAttribute("role", "button");
    image.setAttribute("aria-label", `Expand image: ${imageTitle(image)}`);
    image.addEventListener("click", () => openLightbox(index));
    image.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openLightbox(index);
      }
    });
  });

  galleryOpenButton?.addEventListener("click", () => openLightbox(0));
  lightboxClose.addEventListener("click", closeLightbox);
  lightboxPrevious.addEventListener("click", () => showLightboxImage(currentLightboxIndex - 1));
  lightboxNext.addEventListener("click", () => showLightboxImage(currentLightboxIndex + 1));
  imageLightbox.addEventListener("click", (event) => {
    if (event.target === imageLightbox) {
      closeLightbox();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (imageLightbox.hidden) {
      return;
    }

    if (event.key === "Escape") {
      closeLightbox();
    } else if (event.key === "ArrowLeft") {
      showLightboxImage(currentLightboxIndex - 1);
    } else if (event.key === "ArrowRight") {
      showLightboxImage(currentLightboxIndex + 1);
    }
  });
}
