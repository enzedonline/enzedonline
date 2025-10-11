class H {
  container;
  images;
  debug;
  modal;
  inner;
  imgEls;
  captionEl;
  prevBtn;
  nextBtn;
  closeBtn;
  currentIndex = 0;
  activeLayer = 0;
  // 0 or 1
  loadId = 0;
  // For touch tracking
  touchStartX = 0;
  touchStartY = 0;
  touchEndX = 0;
  touchEndY = 0;
  constructor(s) {
    this.container = s.container, this.images = s.images, (!this.images || this.images.length === 0) && (this.images = Array.from(this.container.querySelectorAll(":scope > picture, :scope > img"))), this.debug = !!s.debug, this.modal = document.createElement("div"), this.modal.className = "lightbox-modal", this.inner = document.createElement("div"), this.inner.className = "lightbox-inner";
    const i = document.createElement("img"), h = document.createElement("img");
    i.className = "lightbox-img", h.className = "lightbox-img", i.classList.remove("visible"), h.classList.remove("visible"), this.imgEls = [i, h], this.captionEl = document.createElement("div"), this.captionEl.className = "lightbox-caption", this.prevBtn = document.createElement("button"), this.prevBtn.type = "button", this.prevBtn.className = "lightbox-prev", this.nextBtn = document.createElement("button"), this.nextBtn.type = "button", this.nextBtn.className = "lightbox-next", this.closeBtn = document.createElement("button"), this.closeBtn.type = "button", this.closeBtn.className = "lightbox-close", this.inner.appendChild(i), this.inner.appendChild(h), this.inner.appendChild(this.captionEl), this.inner.appendChild(this.prevBtn), this.inner.appendChild(this.nextBtn), this.inner.appendChild(this.closeBtn), this.modal.appendChild(this.inner), document.body.appendChild(this.modal), this.modal.addEventListener("click", (e) => {
      e.target === this.modal && this.hide();
    }), this.prevBtn.addEventListener("click", () => this.prev()), this.nextBtn.addEventListener("click", () => this.next()), i.addEventListener("click", (e) => this.imageClickHandler(e)), h.addEventListener("click", (e) => this.imageClickHandler(e)), i.addEventListener("contextmenu", (e) => e.preventDefault()), h.addEventListener("contextmenu", (e) => e.preventDefault()), this.closeBtn.addEventListener("click", () => this.hide()), document.addEventListener("keydown", (e) => {
      if (this.modal.classList.contains("open"))
        switch (e.key) {
          case "ArrowLeft":
            e.preventDefault(), this.prev();
            break;
          case "ArrowRight":
            e.preventDefault(), this.next();
            break;
          case "Escape":
            e.preventDefault(), this.hide();
            break;
        }
    }), this.modal.addEventListener("touchstart", (e) => {
      e.touches.length === 1 && (this.touchStartX = e.touches[0].clientX, this.touchStartY = e.touches[0].clientY);
    }), this.modal.addEventListener("touchend", (e) => {
      e.changedTouches.length === 1 && (this.touchEndX = e.changedTouches[0].clientX, this.touchEndY = e.changedTouches[0].clientY, this.handleSwipe());
    }), this.container.addEventListener("click", (e) => {
      const b = e.target, n = this.images.find((f) => f === b || f.contains(b));
      if (!n) return;
      const u = this.images.indexOf(n);
      u >= 0 && this.show(u);
    });
  }
  /** Swipe detection helper */
  handleSwipe() {
    const s = this.touchEndX - this.touchStartX, i = this.touchEndY - this.touchStartY, h = Math.abs(s), e = Math.abs(i);
    Math.max(h, e) < 40 || (h > e ? s > 0 ? this.prev() : this.next() : this.hide());
  }
  imageClickHandler = (s) => {
    const h = s.currentTarget.getBoundingClientRect();
    s.clientX - h.left < h.width / 2 ? this.prev() : this.next();
  };
  /** Show index with crossfade between two layers. */
  show(s) {
    if (s < 0 || s >= this.images.length) return;
    this.currentIndex = s;
    const i = this.images[s], h = i.dataset.src, e = i.dataset.caption ?? "";
    if (!h) {
      this.debug && console.warn("Lightbox: clicked element missing data-src", i);
      return;
    }
    this.modal.classList.add("open");
    const b = this.imgEls[this.activeLayer], n = this.imgEls[1 - this.activeLayer];
    this.debug && console.debug(`Lightbox: show index ${s}, src=${h}, caption="${e}"`);
    const u = ++this.loadId;
    n.onload = null, n.onerror = null, n.classList.remove("visible"), n.src = "", n.onload = () => {
      if (u !== this.loadId) return;
      n.classList.add("visible"), b.classList.remove("visible"), this.debug && console.debug("Lightbox: image loaded successfully", n), this.activeLayer = 1 - this.activeLayer, e ? (this.captionEl.textContent = e, this.captionEl.classList.add("visible")) : (this.captionEl.textContent = "", this.captionEl.classList.remove("visible"));
      const f = (this.currentIndex + 1) % this.images.length, l = this.images[f].dataset.src;
      if (l) {
        const y = new Image();
        y.src = l, this.debug && console.debug(`Lightbox: preloading next image ${f} (${l})`);
      }
    }, n.onerror = () => {
      this.debug && console.warn("Lightbox: failed to load", h);
    }, n.src = h;
  }
  hide() {
    this.modal.classList.remove("open"), this.captionEl.classList.remove("visible"), this.imgEls.forEach((s) => s.classList.remove("visible")), this.loadId++;
  }
  next() {
    this.show((this.currentIndex + 1) % this.images.length);
  }
  prev() {
    this.show((this.currentIndex - 1 + this.images.length) % this.images.length);
  }
}
class B extends EventTarget {
  container;
  images = [];
  opts;
  resizeTimer = null;
  lightbox = null;
  constructor(s, i = {}) {
    if (super(), !s) throw new Error("ImageWall: container is required");
    this.container = s, this.images = Array.from(this.container.querySelectorAll(":scope > picture, :scope > img")), this.opts = {
      rowHeight: i.rowHeight ?? 180,
      gap: i.gap ?? 6,
      lastRowAlign: i.lastRowAlign ?? "center",
      enableLightbox: i.enableLightbox ?? !0,
      debounceMs: i.debounceMs ?? 120,
      debug: i.debug ?? !1
    }, this.container.style.position = this.container.style.position || "relative", this.container.style.width = "100%", this.layout(), this.container.classList.add("image-wall-initialized"), window.addEventListener("resize", () => {
      this.resizeTimer && window.clearTimeout(this.resizeTimer), this.resizeTimer = window.setTimeout(() => {
        this.layout(), this.resizeTimer = null;
      }, this.opts.debounceMs);
    }), this.opts.enableLightbox && (this.lightbox = new H({ container: this.container, images: this.images, debug: this.opts.debug }));
  }
  /** Public: recompute layout (useful if DOM changed) */
  refresh() {
    this.layout();
  }
  /** Public: re-collect images and recompute layout (useful if children changed) */
  rebuild() {
    this.images = Array.from(this.container.querySelectorAll(":scope > picture, :scope > img")), this.layout(), this.opts.enableLightbox && this.lightbox && (this.lightbox.images = this.images);
  }
  /** Core: compute & apply layout */
  async layout() {
    if (!this.images.length) {
      this.container.style.height = "0px";
      return;
    }
    const s = await Promise.all(this.images.map(async (t) => {
      const a = t.tagName.toLowerCase() === "img" ? t : t.querySelector("img");
      if (!a) throw new Error("ImageWall: each item must contain an <img>");
      const { width: d, height: r } = await this.loadImageNaturalSize(a), o = d && r ? d / r : 1;
      return { el: t, aspect: o, naturalW: d, naturalH: r, src: a.currentSrc || a.src || "" };
    })), i = this.container.getBoundingClientRect(), h = getComputedStyle(this.container), e = parseFloat(h.paddingLeft) || 0, b = parseFloat(h.paddingRight) || 0, n = Math.max(1, Math.floor(i.width - e - b));
    this.opts.debug && (console.debug("[ImageWall] containerInner:", n), console.debug("[ImageWall] items:", s.map((t) => ({ src: t.src, aspect: +t.aspect.toFixed(3) }))));
    const u = this.opts.gap, f = this.opts.rowHeight, v = [];
    let l = [], y = 0;
    for (const t of s)
      if (l.push(t), y += t.aspect, y * f + u * (l.length - 1) >= n) {
        const d = (n - u * (l.length - 1)) / y, r = l.map((o) => o.aspect * d);
        v.push({ items: l.slice(), floatWidths: r, rowHFloat: d, stretch: !0 }), l = [], y = 0;
      }
    if (l.length)
      if (this.opts.lastRowAlign === "justify") {
        const a = l.reduce((o, m) => o + m.aspect, 0), d = (n - u * (l.length - 1)) / a, r = l.map((o) => o.aspect * d);
        v.push({ items: l.slice(), floatWidths: r, rowHFloat: d, stretch: !0 });
      } else {
        const a = l.map((d) => d.aspect * f);
        v.push({ items: l.slice(), floatWidths: a, rowHFloat: f, stretch: !1 });
      }
    this.opts.debug && console.debug("[ImageWall] rowsTemp:", v.map((t, a) => ({ idx: a, count: t.items.length, stretch: t.stretch, rowH: Math.round(t.rowHFloat) })));
    const L = [];
    for (const t of v) {
      const a = t.items.length, d = u * Math.max(0, a - 1);
      if (t.stretch) {
        const r = n - d, o = t.floatWidths.map((c) => Math.floor(c)), m = t.floatWidths.map((c, g) => ({ idx: g, frac: c - o[g] }));
        let p = o.reduce((c, g) => c + g, 0), x = r - p;
        if (x < 0) {
          let c = -x;
          for (let g = o.length - 1; g >= 0 && c > 0; g--) {
            const W = Math.min(Math.max(0, o[g] - 1), c);
            W > 0 && (o[g] -= W, c -= W);
          }
          p = o.reduce((g, W) => g + W, 0), x = Math.max(0, r - p);
        }
        m.sort((c, g) => g.frac - c.frac);
        const I = new Array(a).fill(0);
        for (let c = 0; c < x; c++) I[m[c % a].idx]++;
        const E = o.map((c, g) => c + I[g]), w = E.reduce((c, g) => c + g, 0);
        w !== r && (E[E.length - 1] += r - w);
        const k = Math.max(1, Math.round(t.rowHFloat));
        L.push({ items: t.items, widths: E, height: k, stretch: !0 });
      } else {
        const r = t.floatWidths.map((m) => Math.max(1, Math.round(m))), o = Math.max(1, Math.round(t.rowHFloat));
        L.push({ items: t.items, widths: r, height: o, stretch: !1 });
      }
    }
    if (this.opts.lastRowAlign !== "justify" && L.length > 0) {
      const t = L[L.length - 1], a = t.widths.length, d = u * Math.max(0, a - 1), r = t.widths.reduce((o, m) => o + m, 0) + d;
      r < n ? t.stretch = !1 : t.stretch = !0, this.opts.debug && console.debug("[ImageWall] post-check last rowInnerWidth:", r, "containerInner:", n, "stretch:", t.stretch);
    }
    this.images.forEach((t) => {
      t.style.position = "", t.style.left = "", t.style.top = "", t.style.width = "", t.style.height = "", t.style.margin = "";
      const a = t.tagName.toLowerCase() === "img" ? t : t.querySelector("img");
      a && (a.style.display = "block", a.style.width = "100%", a.style.height = "100%", a.style.objectFit = "cover");
    });
    let M = 0;
    for (const t of L) {
      const a = t.widths.length, d = u * Math.max(0, a - 1), o = t.widths.reduce((p, x) => p + x, 0) + d;
      let m = 0;
      if (!t.stretch && o < n) {
        const p = this.opts.lastRowAlign;
        p === "center" ? m = Math.round((n - o) / 2) : p === "right" ? m = Math.max(0, n - o) : m = 0;
      } else
        m = 0;
      for (let p = 0; p < t.items.length; p++) {
        const x = t.items[p], I = t.widths[p], E = t.height, w = x.el;
        w.style.position = "absolute", w.style.left = `${m}px`, w.style.top = `${M}px`, w.style.width = `${I}px`, w.style.height = `${E}px`, w.style.margin = "0", m += I + u;
      }
      M += t.height + u;
    }
    this.container.style.height = `${Math.max(0, M - u)}px`, this.dispatchEvent(new Event("layout")), this.opts.debug && console.debug("[ImageWall] layout complete, total height:", this.container.style.height);
  }
  /** Helper: get natural size of an image; resolves immediately if already loaded */
  loadImageNaturalSize(s) {
    return new Promise((i, h) => {
      if (!s.src) {
        i({ width: 1, height: 1 });
        return;
      }
      if (s.complete && s.naturalWidth) {
        i({ width: s.naturalWidth, height: s.naturalHeight });
        return;
      }
      const e = new Image();
      e.onload = () => i({ width: e.naturalWidth, height: e.naturalHeight }), e.onerror = () => {
        const b = s.naturalWidth || s.width || 1, n = s.naturalHeight || s.height || 1;
        i({ width: b, height: n });
      }, e.src = s.currentSrc || s.src;
    });
  }
}
export {
  B as ImageWall,
  H as Lightbox
};
