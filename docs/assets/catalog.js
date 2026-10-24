"use strict";
(() => {
  const grid = document.querySelector(".catalog-grid");
  if (!grid) return;
  const storage = {
    read(key) { try { return JSON.parse(localStorage.getItem(key)); } catch { return null; } },
    write(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch {} }
  };
  const find = selector => document.querySelector(selector);
  const cards = Array.from(grid.querySelectorAll(".catalog-card"));
  const search = find("[data-chapter-search]");
  const sort = find("[data-chapter-sort]");
  const view = find("[data-catalog-view]");
  const picker = find("[data-catalog-picker]");
  const frame = find("[data-picker-frame]");
  const scene = find("[data-picker-scene]");
  const volumeList = find(".picker-volumes");
  const volumes = Array.from(document.querySelectorAll("[data-picker-volume]")).map(button => ({
    id: button.dataset.pickerVolume, label: button.dataset.volumeLabel,
    name: button.dataset.volumeName, button,
    chapters: cards.filter(card => card.dataset.volume === button.dataset.pickerVolume)
  }));
  const track = find("[data-picker-track]");
  const image = find("[data-picker-image]");
  const read = find("[data-picker-read]");
  const remembered = volumes.map(() => 0);
  const motions = ["picker-enter-left", "picker-enter-right", "picker-enter-up", "picker-enter-down"];
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  let activeVolume = 0, renderedVolume = -1, reversed = false, showAll = false, suppressClickUntil = 0;
  const last = storage.read("jiuyu-reading-last");
  const saved = storage.read("jiuyu-catalog-selection");
  let initial = cards.find(card => saved && card.dataset.volume === saved.volume && Number(card.dataset.chapterNumber) === saved.chapter);
  if (!initial && last && typeof last.route === "string") initial = cards.find(card => new URL(card.href).pathname === last.route);
  if (initial) {
    activeVolume = volumes.findIndex(volume => volume.id === initial.dataset.volume);
    remembered[activeVolume] = volumes[activeVolume].chapters.indexOf(initial);
  }
  const render = direction => {
    const volume = volumes[activeVolume], index = remembered[activeVolume], card = volume.chapters[index];
    volumes.forEach((item, i) => item.button.setAttribute("aria-selected", String(i === activeVolume)));
    document.querySelectorAll("[data-picker-volume-step]").forEach(button => {
      button.disabled = Number(button.dataset.pickerVolumeStep) < 0 ? activeVolume === 0 : activeVolume === volumes.length - 1;
    });
    document.querySelectorAll("[data-picker-chapter-step]").forEach(button => {
      button.disabled = Number(button.dataset.pickerChapterStep) < 0 ? index === 0 : index === volume.chapters.length - 1;
    });
    find("[data-picker-volume-title]").textContent = `${volume.label} · ${volume.name}`;
    find("[data-picker-position]").textContent = `${String(index + 1).padStart(2, "0")} / ${String(volume.chapters.length).padStart(2, "0")}`;
    find("[data-picker-number]").textContent = card.dataset.chapterNumber.padStart(2, "0");
    find("[data-picker-chapter-label]").textContent = card.dataset.chapterLabel;
    find("[data-picker-chapter-name]").textContent = card.dataset.chapterName;
    find("[data-picker-art-label]").textContent = card.dataset.chapterImage ? "CHAPTER / 章节印象" : "JIUYU / 九域长卷";
    if (card.dataset.chapterImage) {
      image.src = card.dataset.chapterImage.replace("-480.webp", "-960.webp");
      image.alt = `${card.dataset.chapterTitle}章节插画`;
      image.hidden = false;
    } else { image.hidden = true; image.removeAttribute("src"); }
    read.href = card.href;
    read.setAttribute("aria-label", `阅读${card.dataset.chapterTitle}`);
    frame.setAttribute("aria-label", `${volume.label} ${volume.name}，${card.dataset.chapterTitle}`);
    if (renderedVolume !== activeVolume) {
      track.replaceChildren(...volume.chapters.map((chapter, position) => {
        const button = document.createElement("button");
        button.type = "button"; button.className = "picker-dot";
        button.setAttribute("aria-label", `选择${chapter.dataset.chapterTitle}`);
        button.title = chapter.dataset.chapterTitle;
        button.addEventListener("click", () => selectChapter(position));
        return button;
      }));
      renderedVolume = activeVolume;
    }
    Array.from(track.children).forEach((button, i) => button.setAttribute("aria-pressed", String(i === index)));
    const dot = track.children[index];
    track.scrollTo({ left: dot.offsetLeft - track.offsetWidth / 2 + dot.offsetWidth / 2, behavior: "auto" });
    volumeList.scrollTo({ top: volume.button.offsetTop - volumeList.offsetHeight / 2 + volume.button.offsetHeight / 2, behavior: reducedMotion.matches ? "auto" : "smooth" });
    find("[data-picker-announcement]").textContent = `${volume.label} ${volume.name}，${card.dataset.chapterTitle}，本卷第 ${index + 1} / ${volume.chapters.length} 章`;
    storage.write("jiuyu-catalog-selection", { volume: volume.id, chapter: Number(card.dataset.chapterNumber) });
    scene.classList.remove(...motions);
    if (direction && !reducedMotion.matches) { void scene.offsetWidth; scene.classList.add(`picker-enter-${direction}`); }
  };
  const selectChapter = (index, direction) => {
    const next = Math.max(0, Math.min(volumes[activeVolume].chapters.length - 1, index));
    if (next === remembered[activeVolume]) return false;
    remembered[activeVolume] = next; render(direction); return true;
  };
  const selectVolume = (index, direction) => {
    const next = Math.max(0, Math.min(volumes.length - 1, index));
    if (next === activeVolume) return false;
    activeVolume = next; render(direction); return true;
  };
  const step = (axis, delta) => axis === "x"
    ? selectChapter(remembered[activeVolume] + delta, delta > 0 ? "left" : "right")
    : selectVolume(activeVolume + delta, delta > 0 ? "up" : "down");
  volumes.forEach((volume, index) => volume.button.addEventListener("click", () => {
    if (performance.now() >= suppressClickUntil) selectVolume(index, index > activeVolume ? "up" : "down");
  }));
  document.querySelectorAll("[data-picker-volume-step]").forEach(button => button.addEventListener("click", () => step("y", Number(button.dataset.pickerVolumeStep))));
  document.querySelectorAll("[data-picker-chapter-step]").forEach(button => button.addEventListener("click", () => step("x", Number(button.dataset.pickerChapterStep))));
  frame.addEventListener("keydown", event => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    const directions = { ArrowLeft: ["x", -1], ArrowRight: ["x", 1], ArrowUp: ["y", -1], ArrowDown: ["y", 1] };
    if (directions[event.key]) { event.preventDefault(); step(...directions[event.key]); }
  });
  let gesture = null;
  const clearGesture = () => {
    gesture = null; frame.classList.remove("is-dragging");
    scene.style.removeProperty("--picker-drag-x"); scene.style.removeProperty("--picker-drag-y");
  };
  frame.addEventListener("pointerdown", event => {
    if (!event.isPrimary || event.button !== 0 || event.target.closest("a, .picker-chapter-step, .picker-volume-step, .picker-dot")) return;
    gesture = { pointer: event.pointerId, x: event.clientX, y: event.clientY, axis: null, dx: 0, dy: 0 };
  });
  frame.addEventListener("pointermove", event => {
    if (!gesture || event.pointerId !== gesture.pointer) return;
    gesture.dx = event.clientX - gesture.x; gesture.dy = event.clientY - gesture.y;
    if (!gesture.axis && Math.max(Math.abs(gesture.dx), Math.abs(gesture.dy)) > 10) {
      gesture.axis = Math.abs(gesture.dx) > Math.abs(gesture.dy) ? "x" : "y";
      frame.setPointerCapture(event.pointerId); frame.classList.add("is-dragging");
    }
    if (gesture.axis) {
      scene.style.setProperty("--picker-drag-x", `${gesture.axis === "x" ? Math.max(-65, Math.min(65, gesture.dx * .35)) : 0}px`);
      scene.style.setProperty("--picker-drag-y", `${gesture.axis === "y" ? Math.max(-45, Math.min(45, gesture.dy * .3)) : 0}px`);
    }
  });
  frame.addEventListener("pointerup", event => {
    if (!gesture || event.pointerId !== gesture.pointer) return;
    const { axis, dx, dy } = gesture; clearGesture();
    if (axis) suppressClickUntil = performance.now() + 400;
    const distance = axis === "x" ? dx : dy;
    if (axis && Math.abs(distance) >= 42) step(axis, distance < 0 ? 1 : -1);
  });
  frame.addEventListener("pointercancel", clearGesture);
  frame.addEventListener("lostpointercapture", event => {
    // Touch starts with implicit capture on a child; transferring it to the frame
    // must keep the in-progress gesture alive.
    if (event.target === frame) clearGesture();
  });
  frame.addEventListener("click", event => {
    if (performance.now() < suppressClickUntil) { event.preventDefault(); event.stopPropagation(); }
  }, true);
  frame.addEventListener("dragstart", event => event.preventDefault());
  let wheel = { axis: null, total: 0, time: 0, cooldown: 0 };
  frame.addEventListener("wheel", event => {
    if (event.ctrlKey || event.metaKey) return;
    const axis = Math.abs(event.deltaX) > Math.abs(event.deltaY) ? "x" : "y";
    const value = (axis === "x" ? event.deltaX : event.deltaY) * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? frame.clientHeight : 1);
    if (!value) return;
    const delta = Math.sign(value), position = axis === "x" ? remembered[activeVolume] : activeVolume;
    const length = axis === "x" ? volumes[activeVolume].chapters.length : volumes.length;
    if ((position === 0 && delta < 0) || (position === length - 1 && delta > 0)) return;
    event.preventDefault();
    const now = performance.now();
    if (now < wheel.cooldown) return;
    if (wheel.axis !== axis || now - wheel.time > 180 || Math.sign(wheel.total) !== delta) wheel.total = 0;
    wheel.axis = axis; wheel.time = now; wheel.total += value;
    if (Math.abs(wheel.total) >= 45) { step(axis, delta); wheel.total = 0; wheel.cooldown = now + 360; }
  }, { passive: false });
  const filter = () => {
    const query = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    cards.forEach(card => {
      const volume = volumes.find(item => item.id === card.dataset.volume);
      const terms = `${card.dataset.chapterTitle} ${card.dataset.chapterNumber} ${card.dataset.chapterNumber.padStart(3, "0")} ${volume.label} ${volume.name}`.toLocaleLowerCase();
      card.hidden = !terms.includes(query); if (!card.hidden) visible++;
    });
    const listing = showAll || Boolean(query);
    grid.hidden = !listing; picker.hidden = listing; sort.hidden = !listing;
    find("[data-chapter-count]").textContent = query ? `${visible} / ${cards.length} 章` : `${volumes.length} 卷 · ${cards.length} 章`;
    find("[data-chapter-empty]").hidden = !listing || visible !== 0;
    view.textContent = listing ? "滑动选章" : "全部目录";
    view.setAttribute("aria-expanded", String(listing));
  };
  search.addEventListener("input", filter);
  view.addEventListener("click", () => {
    if (search.value.trim()) { search.value = ""; showAll = false; } else showAll = !showAll;
    filter();
  });
  sort.addEventListener("click", () => {
    reversed = !reversed; (reversed ? [...cards].reverse() : cards).forEach(card => grid.append(card));
    sort.textContent = reversed ? "↓ 倒序" : "↑ 正序"; sort.setAttribute("aria-pressed", String(reversed));
  });
  const shell = find(".catalog-shell");
  const remember = event => {
    const link = event.target.closest("a[href]");
    if (!link || event.defaultPrevented) return;
    const opened = cards.find(card => card.href === link.href);
    if (opened) storage.write("jiuyu-reading-last", { route: new URL(opened.href).pathname });
  };
  shell.addEventListener("click", remember); shell.addEventListener("auxclick", remember);
  if (last && typeof last.route === "string") {
    const previous = cards.find(card => new URL(card.href).pathname === last.route);
    if (previous) {
      const resume = find("[data-resume-reader]"); resume.href = previous.href;
      find("[data-resume-title]").textContent = previous.dataset.chapterTitle; resume.hidden = false;
    }
  }
  find("[data-catalog-controls]").hidden = false;
  filter(); render();
})();
