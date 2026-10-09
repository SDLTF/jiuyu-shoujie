"use strict";

const search = document.getElementById("character-search");
if (search) {
  const cards = Array.from(document.querySelectorAll(".character-card"));
  const count = document.getElementById("character-count");
  const noResults = document.getElementById("no-results");
  search.addEventListener("input", () => {
    const query = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    for (const card of cards) {
      card.hidden = !card.dataset.search.toLocaleLowerCase().includes(query);
      if (!card.hidden) visible += 1;
    }
    count.textContent = String(visible);
    noResults.hidden = visible !== 0;
  });
}

const viewer = document.getElementById("image-viewer");
if (viewer) {
  const image = document.getElementById("viewer-image");
  const title = document.getElementById("viewer-name");
  const original = document.getElementById("viewer-original");
  const buttons = Array.from(document.querySelectorAll(".image-open"));
  let selected = 0;
  const show = (index) => {
    selected = index;
    const button = buttons[index];
    image.src = button.dataset.image;
    image.alt = button.dataset.name + "人物展示卡";
    title.textContent = button.dataset.name;
    original.href = button.dataset.original;
  };
  buttons.forEach((button, index) => {
    button.addEventListener("click", () => {
      show(index);
      viewer.showModal();
      document.body.style.overflow = "hidden";
    });
  });
  document.getElementById("viewer-close").addEventListener("click", () => viewer.close());
  viewer.addEventListener("click", (event) => {
    if (event.target !== viewer) return;
    const bounds = viewer.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) viewer.close();
  });
  viewer.addEventListener("close", () => { document.body.style.overflow = ""; });
  viewer.addEventListener("keydown", (event) => {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
    event.preventDefault();
    const direction = event.key === "ArrowRight" ? 1 : -1;
    let next = selected;
    for (let step = 0; step < buttons.length; step += 1) {
      next = (next + direction + buttons.length) % buttons.length;
      if (!buttons[next].closest("article").hidden) { show(next); break; }
    }
  });
}

const revealOutline = document.getElementById("reveal-outline");
if (revealOutline) {
  revealOutline.addEventListener("click", () => {
    document.getElementById("spoiler-notice").hidden = true;
    document.getElementById("outline-content").hidden = false;
    const heading = document.querySelector("#outline-content .prose h2");
    if (heading) { heading.tabIndex = -1; heading.focus({ preventScroll: true }); }
  });
}
