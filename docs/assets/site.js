"use strict";

// Align incoming scene links after the chapter's fonts have settled.
window.addEventListener("load", () => {
  const fragment = window.location.hash;
  if (!/^#illustration-\d+-\d+$/.test(fragment)) return;
  document.fonts.ready.then(() => {
    if (window.location.hash !== fragment) return;
    document.getElementById(fragment.slice(1))?.scrollIntoView({block: "start", behavior: "instant"});
  });
}, {once: true});

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

const artFilters = Array.from(document.querySelectorAll(".art-filter"));
if (artFilters.length) {
  const cards = Array.from(document.querySelectorAll(".art-card"));
  const count = document.getElementById("art-count");
  const filter = (chapter) => {
    if (!artFilters.some(button => button.dataset.chapter === chapter)) chapter = "all";
    let visible = 0;
    cards.forEach(card => {
      card.hidden = chapter !== "all" && card.dataset.chapter !== chapter;
      if (!card.hidden) visible += 1;
    });
    artFilters.forEach(button => button.setAttribute("aria-pressed", String(button.dataset.chapter === chapter)));
    count.textContent = String(visible);
    const url = new URL(window.location.href);
    if (chapter === "all") url.searchParams.delete("chapter");
    else url.searchParams.set("chapter", chapter);
    window.history.replaceState(null, "", url);
  };
  artFilters.forEach(button => button.addEventListener("click", () => filter(button.dataset.chapter)));
  filter(new URL(window.location.href).searchParams.get("chapter") || "all");
}

const viewer = document.getElementById("image-viewer");
if (viewer) {
  const image = document.getElementById("viewer-image");
  const title = document.getElementById("viewer-name");
  const original = document.getElementById("viewer-original");
  const zoom = document.getElementById("viewer-zoom");
  const buttons = Array.from(document.querySelectorAll(".image-open"));
  const position = document.getElementById("viewer-position");
  const available = () => buttons.filter(button => !button.closest(".character-card, .art-card")?.hidden);
  let selected = 0;
  const show = (index) => {
    selected = index;
    const button = buttons[index];
    image.src = button.dataset.image;
    image.alt = button.dataset.name + (button.dataset.kind || "人物展示卡");
    title.textContent = button.dataset.name;
    original.href = button.dataset.original;
    if (position) {
      const visible = available();
      position.textContent = `${visible.indexOf(button) + 1} / ${visible.length}`;
      document.getElementById("viewer-prev").disabled = visible.length < 2;
      document.getElementById("viewer-next").disabled = visible.length < 2;
    }
    viewer.classList.remove("is-zoomed");
    zoom.textContent = "放大细节";
    zoom.setAttribute("aria-pressed", "false");
  };
  buttons.forEach((button, index) => {
    button.addEventListener("click", () => {
      show(index);
      viewer.showModal();
      document.body.style.overflow = "hidden";
    });
  });
  document.getElementById("viewer-close").addEventListener("click", () => viewer.close());
  zoom.addEventListener("click", () => {
    const enlarged = viewer.classList.toggle("is-zoomed");
    zoom.textContent = enlarged ? "适合屏幕" : "放大细节";
    zoom.setAttribute("aria-pressed", String(enlarged));
  });
  viewer.addEventListener("click", (event) => {
    if (event.target !== viewer) return;
    const bounds = viewer.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) viewer.close();
  });
  viewer.addEventListener("close", () => { document.body.style.overflow = ""; });
  const move = (direction) => {
    if (buttons.length < 2) return;
    let next = selected;
    for (let step = 0; step < buttons.length; step += 1) {
      next = (next + direction + buttons.length) % buttons.length;
      const card = buttons[next].closest(".character-card, .art-card");
      if (!card || !card.hidden) { show(next); break; }
    }
  };
  document.getElementById("viewer-prev")?.addEventListener("click", () => move(-1));
  document.getElementById("viewer-next")?.addEventListener("click", () => move(1));
  viewer.addEventListener("keydown", (event) => {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
    event.preventDefault();
    move(event.key === "ArrowRight" ? 1 : -1);
  });
}

const carousel = document.getElementById("hero-carousel");
if (carousel) {
  const slides = Array.from(carousel.querySelectorAll(".hero-slide"));
  const status = document.getElementById("carousel-status");
  let active = 0;
  const showSlide = (index) => {
    active = (index + slides.length) % slides.length;
    slides.forEach((slide, position) => {
      slide.hidden = position !== active;
      if (!slide.hidden) slide.querySelectorAll("img").forEach(image => { image.loading = "eager"; });
    });
    status.textContent = `${String(active + 1).padStart(2, "0")} / ${String(slides.length).padStart(2, "0")}`;
  };
  document.getElementById("carousel-prev").addEventListener("click", () => showSlide(active - 1));
  document.getElementById("carousel-next").addEventListener("click", () => showSlide(active + 1));
  carousel.addEventListener("keydown", event => {
    if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
      event.preventDefault();
      showSlide(active + (event.key === "ArrowRight" ? 1 : -1));
    }
  });
  let touchStart;
  carousel.addEventListener("touchstart", event => {
    if (event.touches.length !== 1) { touchStart = undefined; return; }
    touchStart = {x:event.touches[0].clientX,y:event.touches[0].clientY};
  }, {passive:true});
  carousel.addEventListener("touchend", event => {
    if (!touchStart || event.changedTouches.length !== 1) return;
    const dx = event.changedTouches[0].clientX - touchStart.x;
    const dy = event.changedTouches[0].clientY - touchStart.y;
    touchStart = undefined;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) showSlide(active + (dx < 0 ? 1 : -1));
  }, {passive:true});
  carousel.addEventListener("touchcancel", () => { touchStart = undefined; }, {passive:true});
}

const wikiSearch = document.getElementById("wiki-search");
if (wikiSearch) {
  const terms = Array.from(document.querySelectorAll(".wiki-term"));
  const filters = Array.from(document.querySelectorAll("[data-wiki-category]"));
  const count = document.getElementById("wiki-count");
  const clear = document.getElementById("wiki-clear");
  const advanced = document.getElementById("wiki-advanced");
  const notice = document.getElementById("wiki-spoiler-notice");
  const reveal = document.getElementById("wiki-reveal");
  let category = "all";
  let includeSpoilers = false;
  const update = () => {
    const query = wikiSearch.value.trim().toLocaleLowerCase();
    let visible = 0;
    for (const term of terms) {
      const allowed = includeSpoilers || term.dataset.spoiler !== "true";
      const matchesCategory = category === "all" || term.dataset.category === category;
      term.hidden = !(allowed && matchesCategory && term.dataset.search.toLocaleLowerCase().includes(query));
      if (!term.hidden) visible += 1;
    }
    count.textContent = `${visible} 条${includeSpoilers ? "词条 · 含剧透" : "基础词条"}`;
    document.getElementById("wiki-no-results").hidden = visible !== 0;
    clear.hidden = !query && category === "all";
    for (const filter of filters) filter.setAttribute("aria-pressed", String(filter.dataset.wikiCategory === category));
  };
  const resetFilters = () => { wikiSearch.value = ""; category = "all"; update(); };
  wikiSearch.addEventListener("input", update);
  filters.forEach(filter => filter.addEventListener("click", () => { category = filter.dataset.wikiCategory; update(); }));
  clear.addEventListener("click", () => { resetFilters(); wikiSearch.focus({preventScroll:true}); });
  reveal.addEventListener("click", () => {
    includeSpoilers = true;
    advanced.hidden = false;
    notice.hidden = true;
    reveal.setAttribute("aria-expanded", "true");
    update();
    document.getElementById("wiki-hide").focus({preventScroll:true});
  });
  document.getElementById("wiki-hide").addEventListener("click", () => {
    includeSpoilers = false;
    advanced.hidden = true;
    notice.hidden = false;
    reveal.setAttribute("aria-expanded", "false");
    update();
    reveal.focus({preventScroll:true});
    notice.scrollIntoView({block:"center"});
  });
  const visitTerm = (ident) => {
    const target = document.getElementById(`term-${ident}`);
    if (!target) return;
    if (target.dataset.spoiler === "true" && !includeSpoilers) {
      notice.scrollIntoView({block:"center"});
      reveal.focus({preventScroll:true});
      return;
    }
    resetFilters();
    target.scrollIntoView({block:"start"});
    target.focus({preventScroll:true});
  };
  document.querySelectorAll("[data-term-link]").forEach(link => link.addEventListener("click", (event) => {
    event.preventDefault();
    const ident = link.dataset.termLink;
    const target = document.getElementById(`term-${ident}`);
    if (target.dataset.spoiler !== "true" || includeSpoilers) history.replaceState(null, "", `#term-${ident}`);
    visitTerm(ident);
  }));
  const visitHash = () => {
    if (location.hash.startsWith("#term-")) visitTerm(location.hash.slice(6));
  };
  window.addEventListener("hashchange", visitHash);
  update();
  visitHash();
}
