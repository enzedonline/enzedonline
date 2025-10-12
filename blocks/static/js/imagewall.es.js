class k {
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
  constructor(e) {
    this.container = e.container, this.images = e.images ?? [], (!this.images || this.images.length === 0) && (this.images = Array.from(this.container.querySelectorAll(":scope > picture, :scope > img"))), this.debug = !!e.debug, this.modal = document.createElement("div"), this.modal.className = "lightbox-modal", this.modal.style.display = "none", this.inner = document.createElement("div"), this.inner.className = "lightbox-inner";
    const a = document.createElement("div");
    a.className = "lightbox-spinner";
    const c = document.createElement("img"), h = document.createElement("img");
    c.className = "lightbox-img", h.className = "lightbox-img", c.classList.remove("visible"), h.classList.remove("visible"), this.imgEls = [c, h], this.captionEl = document.createElement("div"), this.captionEl.className = "lightbox-caption", this.prevBtn = document.createElement("button"), this.prevBtn.type = "button", this.prevBtn.className = "lightbox-prev", this.nextBtn = document.createElement("button"), this.nextBtn.type = "button", this.nextBtn.className = "lightbox-next", this.closeBtn = document.createElement("button"), this.closeBtn.type = "button", this.closeBtn.className = "lightbox-close", this.inner.append(c, h, this.captionEl, this.prevBtn, this.nextBtn, this.closeBtn, a), this.modal.append(this.inner), document.body.append(this.modal), this.modal.addEventListener("click", (s) => {
      s.target === this.modal && this.hide();
    }), this.prevBtn.addEventListener("click", () => this.prev()), this.nextBtn.addEventListener("click", () => this.next()), c.addEventListener("click", (s) => this.imageClickHandler(s)), h.addEventListener("click", (s) => this.imageClickHandler(s)), c.addEventListener("contextmenu", (s) => s.preventDefault()), h.addEventListener("contextmenu", (s) => s.preventDefault()), this.closeBtn.addEventListener("click", () => this.hide()), document.addEventListener("keydown", (s) => {
      if (this.modal.classList.contains("open"))
        switch (s.key) {
          case "ArrowLeft":
            s.preventDefault(), this.prev();
            break;
          case "ArrowRight":
            s.preventDefault(), this.next();
            break;
          case "Escape":
            s.preventDefault(), this.hide();
            break;
        }
    }), this.modal.addEventListener("touchstart", (s) => {
      s.touches.length === 1 && (this.touchStartX = s.touches[0].clientX, this.touchStartY = s.touches[0].clientY);
    }), this.modal.addEventListener("touchend", (s) => {
      s.changedTouches.length === 1 && (this.touchEndX = s.changedTouches[0].clientX, this.touchEndY = s.changedTouches[0].clientY, this.handleSwipe());
    }), this.container.addEventListener("click", (s) => {
      const i = s.target, p = this.images.find((b) => b === i || b.contains(i));
      if (!p) return;
      const w = this.images.indexOf(p);
      w >= 0 && this.show(w);
    });
  }
  /** Swipe detection helper */
  handleSwipe() {
    const e = this.touchEndX - this.touchStartX, a = this.touchEndY - this.touchStartY, c = Math.abs(e), h = Math.abs(a);
    Math.max(c, h) < 40 || (c > h ? e > 0 ? this.prev() : this.next() : this.hide());
  }
  imageClickHandler = (e) => {
    const c = e.currentTarget.getBoundingClientRect();
    e.clientX - c.left < c.width / 2 ? this.prev() : this.next();
  };
  /** Show index with crossfade between two layers. */
  show(e) {
    if (e < 0 || e >= this.images.length) return;
    this.currentIndex = e;
    const a = this.images[e], c = a.dataset.src, h = a.dataset.caption ?? "";
    if (!c) {
      this.debug && console.warn("LightBox: clicked element missing data-src", a);
      return;
    }
    this.modal.classList.add("open"), this.modal.style.removeProperty("display"), this.inner.classList.remove("loading"), this.inner.classList.add("loading");
    const s = this.imgEls[this.activeLayer], i = this.imgEls[1 - this.activeLayer];
    this.debug && console.debug(`LightBox: show index ${e}, src=${c}, caption="${h}"`);
    const p = ++this.loadId;
    i.onload = null, i.onerror = null, i.classList.remove("visible"), i.src = "", i.onload = () => {
      if (p !== this.loadId) return;
      i.classList.add("visible"), s.classList.remove("visible"), this.inner.classList.remove("loading"), this.debug && console.debug("LightBox: image loaded successfully", i), this.activeLayer = 1 - this.activeLayer, h ? (this.captionEl.textContent = h, this.captionEl.classList.add("visible")) : (this.captionEl.textContent = "", this.captionEl.classList.remove("visible"));
      const w = (this.currentIndex + 1) % this.images.length, d = this.images[w].dataset.src;
      if (d) {
        const v = new Image();
        v.src = d, this.debug && console.debug(`LightBox: preloading next image ${w} (${d})`);
      }
    }, i.onerror = () => {
      this.debug && console.warn("LightBox: failed to load", c);
    }, i.src = c;
  }
  hide() {
    this.modal.classList.remove("open"), this.captionEl.classList.remove("visible"), this.imgEls.forEach((e) => e.classList.remove("visible")), this.loadId++;
  }
  next() {
    this.show((this.currentIndex + 1) % this.images.length);
  }
  prev() {
    this.show((this.currentIndex - 1 + this.images.length) % this.images.length);
  }
}
class H extends EventTarget {
  lightbox = null;
  container;
  images = [];
  opts;
  resizeTimer = null;
  constructor(e, a = {}) {
    if (super(), !e) throw new Error("ImageWall: container is required");
    this.container = e, this.images = Array.from(this.container.querySelectorAll(":scope > picture, :scope > img")), this.opts = {
      rowHeight: a.rowHeight ?? 180,
      gap: a.gap ?? 6,
      lastRowAlign: a.lastRowAlign ?? "center",
      enableLightbox: a.enableLightbox ?? !0,
      debounceMs: a.debounceMs ?? 120,
      debug: a.debug ?? !1
    }, this.container.style.position = this.container.style.position || "relative", this.container.style.width = "100%", this.layout(), this.container.classList.add("image-wall-initialized"), window.addEventListener("resize", () => {
      this.resizeTimer && window.clearTimeout(this.resizeTimer), this.resizeTimer = window.setTimeout(() => {
        this.layout(), this.resizeTimer = null;
      }, this.opts.debounceMs);
    }), this.opts.enableLightbox && (this.lightbox = new k({ container: this.container, images: this.images, debug: this.opts.debug }));
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
    const e = await Promise.all(this.images.map(async (t) => {
      const n = t.tagName.toLowerCase() === "img" ? t : t.querySelector("img");
      if (!n) throw new Error("ImageWall: each item must contain an <img>");
      const { width: g, height: l } = await this.loadImageNaturalSize(n), o = g && l ? g / l : 1;
      return { el: t, aspect: o, naturalW: g, naturalH: l, src: n.currentSrc || n.src || "" };
    })), a = this.container.getBoundingClientRect(), c = getComputedStyle(this.container), h = parseFloat(c.paddingLeft) || 0, s = parseFloat(c.paddingRight) || 0, i = Math.max(1, Math.floor(a.width - h - s));
    this.opts.debug && (console.debug("[ImageWall] containerInner:", i), console.debug("[ImageWall] items:", e.map((t) => ({ src: t.src, aspect: +t.aspect.toFixed(3) }))));
    const p = this.opts.gap, w = this.opts.rowHeight, b = [];
    let d = [], v = 0;
    for (const t of e)
      if (d.push(t), v += t.aspect, v * w + p * (d.length - 1) >= i) {
        const g = (i - p * (d.length - 1)) / v, l = d.map((o) => o.aspect * g);
        b.push({ items: d.slice(), floatWidths: l, rowHFloat: g, stretch: !0 }), d = [], v = 0;
      }
    if (d.length)
      if (this.opts.lastRowAlign === "justify") {
        const n = d.reduce((o, u) => o + u.aspect, 0), g = (i - p * (d.length - 1)) / n, l = d.map((o) => o.aspect * g);
        b.push({ items: d.slice(), floatWidths: l, rowHFloat: g, stretch: !0 });
      } else {
        const n = d.map((g) => g.aspect * w);
        b.push({ items: d.slice(), floatWidths: n, rowHFloat: w, stretch: !1 });
      }
    this.opts.debug && console.debug("[ImageWall] rowsTemp:", b.map((t, n) => ({ idx: n, count: t.items.length, stretch: t.stretch, rowH: Math.round(t.rowHFloat) })));
    const L = [];
    for (const t of b) {
      const n = t.items.length, g = p * Math.max(0, n - 1);
      if (t.stretch) {
        const l = i - g, o = t.floatWidths.map((r) => Math.floor(r)), u = t.floatWidths.map((r, m) => ({ idx: m, frac: r - o[m] }));
        let f = o.reduce((r, m) => r + m, 0), y = l - f;
        if (y < 0) {
          let r = -y;
          for (let m = o.length - 1; m >= 0 && r > 0; m--) {
            const W = Math.min(Math.max(0, o[m] - 1), r);
            W > 0 && (o[m] -= W, r -= W);
          }
          f = o.reduce((m, W) => m + W, 0), y = Math.max(0, l - f);
        }
        u.sort((r, m) => m.frac - r.frac);
        const I = new Array(n).fill(0);
        for (let r = 0; r < y; r++) I[u[r % n].idx]++;
        const E = o.map((r, m) => r + I[m]), x = E.reduce((r, m) => r + m, 0);
        x !== l && (E[E.length - 1] += l - x);
        const S = Math.max(1, Math.round(t.rowHFloat));
        L.push({ items: t.items, widths: E, height: S, stretch: !0 });
      } else {
        const l = t.floatWidths.map((u) => Math.max(1, Math.round(u))), o = Math.max(1, Math.round(t.rowHFloat));
        L.push({ items: t.items, widths: l, height: o, stretch: !1 });
      }
    }
    if (this.opts.lastRowAlign !== "justify" && L.length > 0) {
      const t = L[L.length - 1], n = t.widths.length, g = p * Math.max(0, n - 1), l = t.widths.reduce((o, u) => o + u, 0) + g;
      l < i ? t.stretch = !1 : t.stretch = !0, this.opts.debug && console.debug("[ImageWall] post-check last rowInnerWidth:", l, "containerInner:", i, "stretch:", t.stretch);
    }
    this.images.forEach((t) => {
      t.style.position = "", t.style.left = "", t.style.top = "", t.style.width = "", t.style.height = "", t.style.margin = "";
      const n = t.tagName.toLowerCase() === "img" ? t : t.querySelector("img");
      n && (n.style.display = "block", n.style.width = "100%", n.style.height = "100%", n.style.objectFit = "cover");
    });
    let B = 0;
    for (const t of L) {
      const n = t.widths.length, g = p * Math.max(0, n - 1), o = t.widths.reduce((f, y) => f + y, 0) + g;
      let u = 0;
      if (!t.stretch && o < i) {
        const f = this.opts.lastRowAlign;
        f === "center" ? u = Math.round((i - o) / 2) : f === "right" ? u = Math.max(0, i - o) : u = 0;
      } else
        u = 0;
      for (let f = 0; f < t.items.length; f++) {
        const y = t.items[f], I = t.widths[f], E = t.height, x = y.el;
        x.style.position = "absolute", x.style.left = `${u}px`, x.style.top = `${B}px`, x.style.width = `${I}px`, x.style.height = `${E}px`, x.style.margin = "0", u += I + p;
      }
      B += t.height + p;
    }
    this.container.style.height = `${Math.max(0, B - p)}px`, this.dispatchEvent(new Event("layout")), this.opts.debug && console.debug("[ImageWall] layout complete, total height:", this.container.style.height);
  }
  /** Helper: get natural size of an image; resolves immediately if already loaded */
  loadImageNaturalSize(e) {
    return new Promise((a, c) => {
      if (!e.src) {
        a({ width: 1, height: 1 });
        return;
      }
      if (e.complete && e.naturalWidth) {
        a({ width: e.naturalWidth, height: e.naturalHeight });
        return;
      }
      const h = new Image();
      h.onload = () => a({ width: h.naturalWidth, height: h.naturalHeight }), h.onerror = () => {
        const s = e.naturalWidth || e.width || 1, i = e.naturalHeight || e.height || 1;
        a({ width: s, height: i });
      }, h.src = e.currentSrc || e.src;
    });
  }
}
export {
  H as ImageWall,
  k as LightBox
};
