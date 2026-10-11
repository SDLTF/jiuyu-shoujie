"use strict";

const characterScene = document.querySelector(".character-scene");
if (characterScene) {
  const slides = Array.from(characterScene.querySelectorAll(".scene-slide"));
  const controls = characterScene.querySelector(".scene-rotation-controls");
  if (slides.length > 1 && controls) {
    const choices = Array.from(controls.querySelectorAll("[data-scene-select]"));
    const toggle = controls.querySelector(".scene-rotation-toggle");
    const status = controls.querySelector(".scene-current");
    const announcement = controls.querySelector(".scene-announcement");
    const currentViewer = characterScene.querySelector(".scene-view-current");
    const currentOriginal = characterScene.querySelector(".scene-original-current");
    const backdrop = document.querySelector(".page-backdrop");
    const motion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const storageKey = "jiuyu-scene-paused";
    let paused = motion.matches;
    try { paused = paused || window.localStorage.getItem(storageKey) === "true"; } catch {}
    let active = 0;
    let timer;
    let inView = true;
    let focusPaused = false;
    let request = 0;
    const pending = new Map();
    const backgrounds = slides.map((slide, index) => {
      const layer = document.createElement("div");
      layer.className = "scene-backdrop-image" + (index === 0 ? " is-active" : "");
      if (index === 0) layer.style.backgroundImage = `url("${slide.dataset.sceneImage}")`;
      backdrop.append(layer);
      return layer;
    });
    backdrop.classList.add("has-scene-rotation");
    const updateStatus = () => {
      toggle.setAttribute("aria-pressed", String(paused));
      toggle.textContent = paused ? "开启轮换" : "暂停轮换";
      status.textContent = slides[active].dataset.sceneLabel + (paused ? " · 已暂停" : " · 每 12 秒轮换");
    };
    const canPlay = () => !paused && inView && !document.hidden && !focusPaused
      && !document.querySelector("#image-viewer[open]");
    const schedule = () => {
      window.clearTimeout(timer);
      if (!canPlay()) return;
      timer = window.setTimeout(() => show((active + 1) % slides.length, false), 12000);
    };
    const loadSlide = index => {
      if (pending.has(index)) return pending.get(index);
      const slide = slides[index];
      const image = slide.querySelector("img");
      if (image.dataset.sceneSrc) {
        image.srcset = image.dataset.sceneSrcset;
        image.src = image.dataset.sceneSrc;
      }
      const ready = image.decode().then(() => {
        const source = image.currentSrc || image.src;
        backgrounds[index].style.backgroundImage = `url("${source}")`;
      }).catch(error => { pending.delete(index); throw error; });
      pending.set(index, ready);
      return ready;
    };
    const show = async (index, manual) => {
      const version = ++request;
      window.clearTimeout(timer);
      if (manual) announcement.textContent = "正在加载" + slides[index].dataset.sceneLabel;
      try {
        await loadSlide(index);
        if (version !== request) return;
        // A slow download must not resume motion after the visitor pauses it.
        if (!manual && !canPlay()) return;
        active = index;
        slides.forEach((slide, position) => slide.classList.toggle("is-active", position === active));
        backgrounds.forEach((layer, position) => layer.classList.toggle("is-active", position === active));
        choices.forEach(button => button.setAttribute("aria-pressed", String(Number(button.dataset.sceneSelect) === active)));
        const slide = slides[active];
        currentViewer.dataset.image = slide.dataset.sceneImage;
        currentViewer.dataset.original = slide.dataset.sceneOriginal;
        currentViewer.dataset.name = characterScene.dataset.sceneName + " · " + slide.dataset.sceneLabel;
        currentViewer.dataset.kind = slide.dataset.sceneLabel;
        currentOriginal.href = slide.dataset.sceneOriginal;
        characterScene.dataset.sceneActive = String(active);
        updateStatus();
        if (manual) announcement.textContent = "已切换为" + slide.dataset.sceneLabel;
      } catch {
        if (manual && version === request) announcement.textContent = "图片暂时未能加载，请稍后重试。";
      } finally {
        if (version === request) schedule();
      }
    };
    choices.forEach(button => button.addEventListener("click", () => show(Number(button.dataset.sceneSelect), true)));
    controls.addEventListener("keydown", event => {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      event.preventDefault();
      const next = (active + (event.key === "ArrowRight" ? 1 : -1) + slides.length) % slides.length;
      choices[next].focus({preventScroll:true});
      show(next, true);
    });
    toggle.addEventListener("click", () => {
      paused = !paused;
      if (!paused) focusPaused = false;
      try { window.localStorage.setItem(storageKey, String(paused)); } catch {}
      updateStatus();
      schedule();
    });
    controls.addEventListener("focusin", () => { focusPaused = true; schedule(); });
    controls.addEventListener("focusout", () => window.setTimeout(() => {
      if (!controls.contains(document.activeElement)) focusPaused = false;
      schedule();
    }, 0));
    document.addEventListener("visibilitychange", schedule);
    motion.addEventListener("change", event => {
      if (event.matches) paused = true;
      updateStatus();
      schedule();
    });
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(entries => {
        inView = entries[0].isIntersecting;
        schedule();
      }).observe(characterScene);
    }
    const imageViewer = document.getElementById("image-viewer");
    if (imageViewer) new MutationObserver(schedule).observe(imageViewer, {attributes:true, attributeFilter:["open"]});
    controls.hidden = false;
    characterScene.dataset.sceneActive = "0";
    updateStatus();
    schedule();
  }
}

const avatarSwitches = Array.from(document.querySelectorAll(".avatar-switch"));
if (avatarSwitches.length) {
  const storageKey = "jiuyu-avatar-style";
  const choices = Array.from(document.querySelectorAll("[data-avatar-choice]"));
  const images = Array.from(document.querySelectorAll("img[data-avatar]"));
  const avatarViewers = Array.from(document.querySelectorAll("[data-avatar-viewer]"));
  const downloads = Array.from(document.querySelectorAll("[data-avatar-download]"));
  const applyStyle = (value) => {
    const style = value === "chibi" ? "chibi" : "original";
    const label = style === "chibi" ? "Q版全身立绘" : "人物头像";
    images.forEach(image => {
      image.srcset = image.dataset[style + "Srcset"];
      image.src = image.dataset[style + "Src"];
      image.alt = image.dataset.avatarName + (style === "chibi" ? "Q版全身立绘" : "头像");
      image.parentElement.dataset.avatarStyle = style;
    });
    choices.forEach(button => button.setAttribute("aria-pressed", String(button.dataset.avatarChoice === style)));
    avatarViewers.forEach(button => {
      button.dataset.image = button.dataset[style + "Image"];
      button.dataset.original = button.dataset[style + "Source"];
      button.dataset.name = button.dataset.avatarName + " · " + label;
      button.dataset.kind = label;
      button.dataset.alt = button.dataset.avatarName + label;
      button.textContent = "查看" + label + " ↗";
    });
    downloads.forEach(link => {
      link.href = link.dataset[style + "Source"];
      link.textContent = style === "chibi" ? "Q版原图" : "头像原图";
    });
  };
  let savedStyle;
  try { savedStyle = window.localStorage.getItem(storageKey); } catch {}
  applyStyle(savedStyle);
  avatarSwitches.forEach(control => { control.hidden = false; });
  choices.forEach(button => button.addEventListener("click", () => {
    const style = button.dataset.avatarChoice;
    applyStyle(style);
    try { window.localStorage.setItem(storageKey, style); } catch {}
  }));
  window.addEventListener("storage", event => {
    if (event.key === storageKey || event.key === null) applyStyle(event.newValue);
  });
  // Restore the preference when returning to a page from the browser's history cache.
  window.addEventListener("pageshow", () => {
    try { applyStyle(window.localStorage.getItem(storageKey)); } catch {}
  });
}

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

const stickerSearch = document.getElementById("sticker-search");
if (stickerSearch) {
  const groups = Array.from(document.querySelectorAll(".sticker-character"));
  stickerSearch.addEventListener("input", () => {
    const query = stickerSearch.value.trim().toLocaleLowerCase();
    let visible = 0;
    groups.forEach(group => {
      group.hidden = !group.dataset.search.toLocaleLowerCase().includes(query);
      if (!group.hidden) visible += 1;
    });
    document.getElementById("sticker-count").textContent = String(visible);
    document.getElementById("sticker-no-results").hidden = visible !== 0;
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

const fanworkSearch = document.getElementById("fanwork-search");
if (fanworkSearch) {
  const cards = Array.from(document.querySelectorAll(".fanwork-card"));
  const filters = Array.from(document.querySelectorAll(".fanwork-filter"));
  const count = document.getElementById("fanwork-count");
  const noResults = document.getElementById("fanwork-no-results");
  const tagButtons = Array.from(document.querySelectorAll("[data-fanwork-tag]"));
  const cardTags = new Map(cards.map(card => [card, new Set(JSON.parse(card.dataset.tags || "[]"))]));
  const validTags = new Set(Array.from(cardTags.values()).flatMap(tags => Array.from(tags)));
  const requestedTag = new URL(window.location.href).searchParams.get("tag") || "";
  let tag = validTags.has(requestedTag) ? requestedTag : "";
  let type = "all";
  const update = () => {
    const query = fanworkSearch.value.trim().toLocaleLowerCase();
    let visible = 0;
    cards.forEach(card => {
      card.hidden = !(type === "all" || card.dataset.type === type)
        || !card.dataset.search.toLocaleLowerCase().includes(query)
        || (tag !== "" && !cardTags.get(card).has(tag));
      if (!card.hidden) visible += 1;
    });
    filters.forEach(button => button.setAttribute("aria-pressed", String(button.dataset.type === type)));
    tagButtons.forEach(button => button.setAttribute("aria-pressed", String(button.dataset.fanworkTag === tag)));
    count.textContent = String(visible);
    noResults.hidden = visible !== 0 || cards.length === 0;
  };
  filters.forEach(button => button.addEventListener("click", () => { type = button.dataset.type; update(); }));
  const tagList = document.getElementById("fanwork-tag-list");
  const tagPrevious = document.getElementById("fanwork-tags-prev");
  const tagNext = document.getElementById("fanwork-tags-next");
  const updateTagScroll = () => {
    if (!tagList) return;
    tagPrevious.disabled = tagList.scrollLeft <= 2;
    tagNext.disabled = tagList.scrollLeft + tagList.clientWidth >= tagList.scrollWidth - 2;
  };
  const revealSelectedTag = () => {
    if (!tagList) return;
    const button = Array.from(tagList.querySelectorAll("[data-fanwork-tag]")).find(button => button.dataset.fanworkTag === tag);
    if (!button) return;
    const left = button.offsetLeft;
    const right = left + button.offsetWidth;
    if (left < tagList.scrollLeft) tagList.scrollLeft = left;
    else if (right > tagList.scrollLeft + tagList.clientWidth) tagList.scrollLeft = right - tagList.clientWidth;
    updateTagScroll();
  };
  tagButtons.forEach(button => button.addEventListener("click", () => {
    const selected = button.dataset.fanworkTag;
    tag = selected === tag ? "" : selected;
    const url = new URL(window.location.href);
    if (tag) url.searchParams.set("tag", tag);
    else url.searchParams.delete("tag");
    window.history.replaceState(null, "", url);
    update();
    revealSelectedTag();
  }));
  if (tagList) {
    const scrollTags = direction => {
      const behavior = window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth";
      tagList.scrollBy({left: direction * tagList.clientWidth * 0.75, behavior});
    };
    tagPrevious.addEventListener("click", () => scrollTags(-1));
    tagNext.addEventListener("click", () => scrollTags(1));
    tagList.addEventListener("scroll", updateTagScroll, {passive: true});
    window.addEventListener("resize", updateTagScroll);
    document.fonts.ready.then(revealSelectedTag);
    revealSelectedTag();
  }
  fanworkSearch.addEventListener("input", update);
  update();
}

const viewer = document.getElementById("image-viewer");
if (viewer) {
  const image = document.getElementById("viewer-image");
  const title = document.getElementById("viewer-name");
  const original = document.getElementById("viewer-original");
  const zoom = document.getElementById("viewer-zoom");
  image.addEventListener("load", () => viewer.style.setProperty("--viewer-native-width", image.naturalWidth + "px"));
  const buttons = Array.from(document.querySelectorAll(".image-open"));
  const position = document.getElementById("viewer-position");
  const available = () => buttons.filter(button => !button.closest(".character-card, .art-card, .fanwork-card, .sticker-character")?.hidden);
  let selected = 0;
  const show = (index) => {
    selected = index;
    const button = buttons[index];
    image.src = button.dataset.image;
    image.alt = button.dataset.alt || button.dataset.name + (button.dataset.kind || "人物展示卡");
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
      const card = buttons[next].closest(".character-card, .art-card, .fanwork-card, .sticker-character");
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
