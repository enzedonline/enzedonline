// src/core/lightbox.ts
var e = class {
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
	loadId = 0;
	touchStartX = 0;
	touchStartY = 0;
	touchEndX = 0;
	touchEndY = 0;
	constructor(e) {
		this.container = e.container, this.images = e.images ?? [], this.images && this.images.length !== 0 || (this.images = Array.from(this.container.querySelectorAll(":scope > picture, :scope > img"))), this.debug = !!e.debug, this.modal = document.createElement("div"), this.modal.className = "lightbox-modal", this.modal.style.display = "none", this.inner = document.createElement("div"), this.inner.className = "lightbox-inner";
		let t = document.createElement("div");
		t.className = "lightbox-spinner";
		let n = document.createElement("img"), r = document.createElement("img");
		n.className = "lightbox-img", r.className = "lightbox-img", n.classList.remove("visible"), r.classList.remove("visible"), this.imgEls = [n, r], this.captionEl = document.createElement("div"), this.captionEl.className = "lightbox-caption", this.prevBtn = document.createElement("button"), this.prevBtn.type = "button", this.prevBtn.className = "lightbox-prev", this.prevBtn.ariaLabel = e.buttonCaptions?.prev || "Previous", this.nextBtn = document.createElement("button"), this.nextBtn.type = "button", this.nextBtn.className = "lightbox-next", this.nextBtn.ariaLabel = e.buttonCaptions?.next || "Next", this.closeBtn = document.createElement("button"), this.closeBtn.type = "button", this.closeBtn.className = "lightbox-close", this.closeBtn.ariaLabel = e.buttonCaptions?.close || "Close", this.inner.append(n, r, this.captionEl, this.prevBtn, this.nextBtn, this.closeBtn, t), this.modal.append(this.inner), document.body.append(this.modal), this.modal.addEventListener("click", (e) => {
			e.target === this.modal && this.hide();
		}), this.prevBtn.addEventListener("click", () => this.prev()), this.nextBtn.addEventListener("click", () => this.next()), n.addEventListener("click", (e) => this.imageClickHandler(e)), r.addEventListener("click", (e) => this.imageClickHandler(e)), n.addEventListener("contextmenu", (e) => e.preventDefault()), r.addEventListener("contextmenu", (e) => e.preventDefault()), this.closeBtn.addEventListener("click", () => this.hide()), document.addEventListener("keydown", (e) => {
			if (this.modal.classList.contains("open")) switch (e.key) {
				case "ArrowLeft":
					e.preventDefault(), this.prev();
					break;
				case "ArrowRight":
					e.preventDefault(), this.next();
					break;
				case "Escape": e.preventDefault(), this.hide();
			}
		}), this.modal.addEventListener("touchstart", (e) => {
			e.touches.length === 1 && (this.touchStartX = e.touches[0].clientX, this.touchStartY = e.touches[0].clientY);
		}), this.modal.addEventListener("touchend", (e) => {
			e.changedTouches.length === 1 && (this.touchEndX = e.changedTouches[0].clientX, this.touchEndY = e.changedTouches[0].clientY, this.handleSwipe());
		}), this.container.addEventListener("click", (e) => {
			let t = e.target, n = this.images.find((e) => e === t || e.contains(t));
			if (!n) return;
			let r = this.images.indexOf(n);
			r >= 0 && this.show(r);
		});
	}
	handleSwipe() {
		let e = this.touchEndX - this.touchStartX, t = this.touchEndY - this.touchStartY, n = Math.abs(e), r = Math.abs(t);
		Math.max(n, r) < 40 || (n > r ? e > 0 ? this.prev() : this.next() : this.hide());
	}
	imageClickHandler = (e) => {
		let t = e.currentTarget.getBoundingClientRect();
		e.clientX - t.left < t.width / 2 ? this.prev() : this.next();
	};
	show(e) {
		if (e < 0 || e >= this.images.length) return;
		this.currentIndex = e;
		let t = this.images[e], n = t.dataset.src, r = t.dataset.caption ?? "";
		if (!n) {
			this.debug && console.warn("LightBox: clicked element missing data-src", t);
			return;
		}
		this.modal.classList.add("open"), this.modal.style.removeProperty("display"), this.inner.classList.remove("loading"), this.inner.classList.add("loading");
		let i = this.imgEls[this.activeLayer], a = this.imgEls[1 - this.activeLayer];
		this.debug && console.debug(`LightBox: show index ${e}, src=${n}, caption="${r}"`);
		let o = ++this.loadId;
		a.onload = null, a.onerror = null, a.classList.remove("visible"), a.src = "", a.onload = () => {
			if (o !== this.loadId) return;
			a.classList.add("visible"), i.classList.remove("visible"), this.inner.classList.remove("loading"), this.debug && console.debug("LightBox: image loaded successfully", a), this.activeLayer = 1 - this.activeLayer, r ? (this.captionEl.textContent = r, this.captionEl.classList.add("visible")) : (this.captionEl.textContent = "", this.captionEl.classList.remove("visible"));
			let e = (this.currentIndex + 1) % this.images.length, t = this.images[e].dataset.src;
			if (t) {
				let n = new Image();
				n.src = t, this.debug && console.debug(`LightBox: preloading next image ${e} (${t})`);
			}
		}, a.onerror = () => {
			this.debug && console.warn("LightBox: failed to load", n);
		}, a.src = n;
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
}, t = class extends EventTarget {
	lightbox = null;
	container;
	images = [];
	opts;
	resizeTimer = null;
	constructor(t, n = {}) {
		if (super(), !t) throw Error("ImageWall: container is required");
		this.container = t, this.images = Array.from(this.container.querySelectorAll(":scope > picture, :scope > img")), this.opts = {
			rowHeight: n.rowHeight ?? 180,
			gap: n.gap ?? 6,
			lastRowAlign: n.lastRowAlign ?? "center",
			enableLightbox: n.enableLightbox ?? !0,
			debounceMs: n.debounceMs ?? 120,
			debug: n.debug ?? !1
		}, this.container.style.position = this.container.style.position || "relative", this.container.style.width = "100%", this.layout(), this.container.classList.add("image-wall-initialized"), window.addEventListener("resize", () => {
			this.resizeTimer && window.clearTimeout(this.resizeTimer), this.resizeTimer = window.setTimeout(() => {
				this.layout(), this.resizeTimer = null;
			}, this.opts.debounceMs);
		}), this.opts.enableLightbox && (this.lightbox = new e({
			container: this.container,
			images: this.images,
			debug: this.opts.debug
		}));
	}
	refresh() {
		this.layout();
	}
	rebuild() {
		this.images = Array.from(this.container.querySelectorAll(":scope > picture, :scope > img")), this.layout(), this.opts.enableLightbox && this.lightbox && (this.lightbox.images = this.images);
	}
	async layout() {
		if (!this.images.length) {
			this.container.style.height = "0px";
			return;
		}
		let e = await Promise.all(this.images.map(async (e) => {
			let t = e.tagName.toLowerCase() === "img" ? e : e.querySelector("img");
			if (!t) throw Error("ImageWall: each item must contain an <img>");
			let { width: n, height: r } = await this.loadImageNaturalSize(t);
			return {
				el: e,
				aspect: n && r ? n / r : 1,
				naturalW: n,
				naturalH: r,
				src: t.currentSrc || t.src || ""
			};
		})), t = this.container.getBoundingClientRect(), n = getComputedStyle(this.container), r = parseFloat(n.paddingLeft) || 0, i = parseFloat(n.paddingRight) || 0, a = Math.max(1, Math.floor(t.width - r - i));
		this.opts.debug && (console.debug("[ImageWall] containerInner:", a), console.debug("[ImageWall] items:", e.map((e) => ({
			src: e.src,
			aspect: +e.aspect.toFixed(3)
		}))));
		let o = this.opts.gap, s = this.opts.rowHeight, c = [], l = [], u = 0;
		for (let t of e) if (l.push(t), u += t.aspect, u * s + o * (l.length - 1) >= a) {
			let e = (a - o * (l.length - 1)) / u, t = l.map((t) => t.aspect * e);
			c.push({
				items: l.slice(),
				floatWidths: t,
				rowHFloat: e,
				stretch: !0
			}), l = [], u = 0;
		}
		if (l.length) {
			if (this.opts.lastRowAlign === "justify") {
				let e = l.reduce((e, t) => e + t.aspect, 0), t = (a - o * (l.length - 1)) / e, n = l.map((e) => e.aspect * t);
				c.push({
					items: l.slice(),
					floatWidths: n,
					rowHFloat: t,
					stretch: !0
				});
			} else {
				let e = l.map((e) => e.aspect * s);
				c.push({
					items: l.slice(),
					floatWidths: e,
					rowHFloat: s,
					stretch: !1
				});
			}
		}
		this.opts.debug && console.debug("[ImageWall] rowsTemp:", c.map((e, t) => ({
			idx: t,
			count: e.items.length,
			stretch: e.stretch,
			rowH: Math.round(e.rowHFloat)
		})));
		let d = [];
		for (let e of c) {
			let t = e.items.length, n = o * Math.max(0, t - 1);
			if (e.stretch) {
				let r = a - n, i = e.floatWidths.map((e) => Math.floor(e)), o = e.floatWidths.map((e, t) => ({
					idx: t,
					frac: e - i[t]
				})), s = i.reduce((e, t) => e + t, 0), c = r - s;
				if (c < 0) {
					let e = -c;
					for (let t = i.length - 1; t >= 0 && e > 0; t--) {
						let n = Math.min(Math.max(0, i[t] - 1), e);
						n > 0 && (i[t] -= n, e -= n);
					}
					s = i.reduce((e, t) => e + t, 0), c = Math.max(0, r - s);
				}
				o.sort((e, t) => t.frac - e.frac);
				let l = Array(t).fill(0);
				for (let e = 0; e < c; e++) l[o[e % t].idx]++;
				let u = i.map((e, t) => e + l[t]), f = u.reduce((e, t) => e + t, 0);
				f !== r && (u[u.length - 1] += r - f);
				let p = Math.max(1, Math.round(e.rowHFloat));
				d.push({
					items: e.items,
					widths: u,
					height: p,
					stretch: !0
				});
			} else {
				let t = e.floatWidths.map((e) => Math.max(1, Math.round(e))), n = Math.max(1, Math.round(e.rowHFloat));
				d.push({
					items: e.items,
					widths: t,
					height: n,
					stretch: !1
				});
			}
		}
		if (this.opts.lastRowAlign !== "justify" && d.length > 0) {
			let e = d[d.length - 1], t = e.widths.length, n = o * Math.max(0, t - 1), r = e.widths.reduce((e, t) => e + t, 0) + n;
			e.stretch = !(r < a), this.opts.debug && console.debug("[ImageWall] post-check last rowInnerWidth:", r, "containerInner:", a, "stretch:", e.stretch);
		}
		this.images.forEach((e) => {
			e.style.position = "", e.style.left = "", e.style.top = "", e.style.width = "", e.style.height = "", e.style.margin = "";
			let t = e.tagName.toLowerCase() === "img" ? e : e.querySelector("img");
			t && (t.style.display = "block", t.style.width = "100%", t.style.height = "100%", t.style.objectFit = "cover");
		});
		let f = 0;
		for (let e of d) {
			let t = e.widths.length, n = o * Math.max(0, t - 1), r = e.widths.reduce((e, t) => e + t, 0) + n, i = 0;
			if (!e.stretch && r < a) {
				let e = this.opts.lastRowAlign;
				i = e === "center" ? Math.round((a - r) / 2) : e === "right" ? Math.max(0, a - r) : 0;
			} else i = 0;
			for (let t = 0; t < e.items.length; t++) {
				let n = e.items[t], r = e.widths[t], a = e.height, s = n.el;
				s.style.position = "absolute", s.style.left = `${i}px`, s.style.top = `${f}px`, s.style.width = `${r}px`, s.style.height = `${a}px`, s.style.margin = "0", i += r + o;
			}
			f += e.height + o;
		}
		this.container.style.height = `${Math.max(0, f - o)}px`, this.dispatchEvent(new Event("layout")), this.opts.debug && console.debug("[ImageWall] layout complete, total height:", this.container.style.height);
	}
	loadImageNaturalSize(e) {
		return new Promise((t, n) => {
			if (!e.src) {
				t({
					width: 1,
					height: 1
				});
				return;
			}
			if (e.complete && e.naturalWidth) {
				t({
					width: e.naturalWidth,
					height: e.naturalHeight
				});
				return;
			}
			let r = new Image();
			r.onload = () => t({
				width: r.naturalWidth,
				height: r.naturalHeight
			}), r.onerror = () => {
				let r = e.naturalWidth || e.width || 1, i = e.naturalHeight || e.height || 1;
				r && i ? t({
					width: r,
					height: i
				}) : n(/* @__PURE__ */ Error("ImageWall: failed to load image " + e.src));
			}, r.src = e.currentSrc || e.src;
		});
	}
};
export { t as ImageWall, e as LightBox };
