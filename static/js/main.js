/* ===========================================================================
   GACHI FOUNDATION — main.js
   Modules (each guarded by an existence check so it is safe on every page):
     1. Sticky header darken + mobile drawer
     2. Rotating word in the hero headline (index)
     3. Scroll reveal + count-up stats
     4. FAQ accordion
     5. Mahua-flower drift (2D canvas, #leafcanvas)
     6. Caustic water background (WebGL, #bg-water)   — needs THREE
     7. Caustic river footer (WebGL, #foot-water canvas) — needs THREE
   three.js is loaded from a CDN in base.html before this file.
   =========================================================================== */
(function () {
  "use strict";

  /* 1 — header + mobile menu ------------------------------------------------ */
  var header = document.getElementById("site-header");
  if (header) {
    addEventListener("scroll", function () {
      header.classList.toggle("scrolled", scrollY > 20);
    }, { passive: true });
  }
  var burger = document.getElementById("burger");
  var drawer = document.getElementById("mobileMenu");
  if (burger && drawer) {
    burger.addEventListener("click", function () {
      burger.classList.toggle("open");
      drawer.classList.toggle("open");
    });
    drawer.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        burger.classList.remove("open");
        drawer.classList.remove("open");
      });
    });
  }

  /* 2 — rotating word ------------------------------------------------------- */
  var rot = document.querySelector("[data-rotate]");
  if (rot) {
    var words = (rot.getAttribute("data-rotate") || "").split("|");
    var k = 0;
    if (words.length > 1) {
      setInterval(function () {
        rot.style.opacity = 0;
        setTimeout(function () {
          k = (k + 1) % words.length;
          rot.textContent = words[k];
          rot.style.opacity = 1;
        }, 400);
      }, 2300);
    }
  }

  /* 3 — reveal + stats count-up -------------------------------------------- */
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { threshold: 0.12 });
    document.querySelectorAll(".reveal").forEach(function (el) { io.observe(el); });
    document.querySelectorAll(".t").forEach(function (t, i) {
      t.style.transitionDelay = (i % 4) * 70 + "ms";
      t.style.setProperty("--dl", (i * 0.45) + "s");
      io.observe(t);
    });

    var band = document.querySelector(".stats-band");
    if (band) {
      var ran = false;
      new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (e.isIntersecting && !ran) {
            ran = true;
            document.querySelectorAll(".sb .num").forEach(function (n) {
              if (n.dataset.static) return;
              var to = +n.dataset.to, suf = n.dataset.suffix || "", t0 = null;
              (function step(ts) {
                if (!t0) t0 = ts;
                var p = Math.min((ts - t0) / 1200, 1);
                n.textContent = Math.floor(p * to) + suf;
                if (p < 1) requestAnimationFrame(step);
              })();
            });
          }
        });
      }, { threshold: 0.4 }).observe(band);
    }
  } else {
    document.querySelectorAll(".reveal,.t").forEach(function (el) { el.classList.add("in"); });
  }

  /* 4 — FAQ accordion ------------------------------------------------------- */
  document.querySelectorAll(".faq-item").forEach(function (item) {
    item.addEventListener("click", function () { item.classList.toggle("open"); });
  });

  /* current year stamps */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  var reduce = matchMedia("(prefers-reduced-motion:reduce)").matches;

  /* 5 — mahua-flower drift (2D canvas) ------------------------------------- */
  var lc = document.getElementById("leafcanvas");
  if (lc && !reduce) {
    var x = lc.getContext("2d");
    var srcs = (window.GACHI_FLOWERS || []);
    var imgs = srcs.map(function (s) { var im = new Image(); im.src = s; return im; });
    function size() { lc.width = innerWidth; lc.height = innerHeight; }
    size(); addEventListener("resize", size);
    var N = innerWidth < 700 ? 12 : 26, P = [];
    for (var i = 0; i < N; i++) P.push({
      x: Math.random() * innerWidth, y: Math.random() * innerHeight,
      s: 13 + Math.random() * 15, a: Math.random() * 6.28, va: (Math.random() - .5) * .018,
      vy: .3 + Math.random() * .7, sw: .4 + Math.random() * 1.3, ph: Math.random() * 6.28,
      img: imgs.length ? imgs[Math.floor(Math.random() * imgs.length)] : null
    });
    function draw(o) {
      if (!o.img || !o.img.complete || !o.img.naturalWidth) return;
      var w = o.s * 1.5, h = w * 1.25;
      x.save(); x.translate(o.x, o.y); x.rotate(o.a); x.globalAlpha = .85;
      x.drawImage(o.img, -w / 2, -h / 2, w, h); x.restore();
    }
    var t = 0;
    (function loop() {
      t += .02; x.clearRect(0, 0, lc.width, lc.height);
      P.forEach(function (o) {
        o.y += o.vy; o.x += Math.sin(t + o.ph) * o.sw; o.a += o.va;
        if (o.y > lc.height + 26) { o.y = -26; o.x = Math.random() * lc.width; }
        draw(o);
      });
      requestAnimationFrame(loop);
    })();
  }

  /* shared GLSL caustic shader factory (used by bg + footer) ---------------- */
  function caustic(canvas, opts) {
    if (!window.THREE || !canvas) return;
    opts = opts || {};
    var r = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
    r.setPixelRatio(Math.min(devicePixelRatio, 2));
    var sc = new THREE.Scene();
    var cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    var deep = opts.deep || "vec3(.13,.45,.55)";
    var shal = opts.shal || "vec3(.62,.86,.85)";
    var mat = new THREE.ShaderMaterial({
      uniforms: { t: { value: 0 }, res: { value: new THREE.Vector2(1, 1) } },
      vertexShader: "varying vec2 vu;void main(){vu=uv;gl_Position=vec4(position,1.);}",
      fragmentShader:
        "precision highp float;varying vec2 vu;uniform float t;uniform vec2 res;" +
        "float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}" +
        "float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);" +
        "return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}" +
        "float fbm(vec2 p){float v=0.,a=.5;for(int i=0;i<5;i++){v+=a*noise(p);p*=2.02;a*=.5;}return v;}" +
        "void main(){vec2 uv=vu;uv.x*=res.x/res.y;vec2 fl=vec2(t*.6,0.);" +
        "vec2 q=vec2(fbm(uv*4.+fl),fbm(uv*4.+vec2(5.2,0.)+fl));" +
        "float f=fbm(uv*4.+q*1.6+fl);vec3 deep=" + deep + ",shal=" + shal + ";" +
        "vec3 col=mix(deep,shal,smoothstep(.3,.85,f));" +
        "col+=pow(smoothstep(.7,.97,f),3.)*vec3(.7,.92,.95)*.7;gl_FragColor=vec4(col," + (opts.alpha || "0.95") + ");}"
    });
    sc.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), mat));
    var host = opts.host || null;
    function sz() {
      var w = host ? host.clientWidth : innerWidth;
      var h = host ? host.clientHeight : innerHeight;
      r.setSize(w, h, false); mat.uniforms.res.value.set(w, h);
    }
    if (host && "ResizeObserver" in window) new ResizeObserver(sz).observe(host);
    else addEventListener("resize", sz);
    sz();
    (function loop(ts) { mat.uniforms.t.value = ts * 0.001; r.render(sc, cam); requestAnimationFrame(loop); })(0);
  }

  /* 6 — background water */
  caustic(document.getElementById("bg-water"), { alpha: "0.95" });
  /* 7 — footer river (darker palette, fits inside the footer element) */
  var fw = document.getElementById("foot-water");
  if (fw) caustic(fw, { host: fw.closest(".site-footer"), alpha: "1.0",
    deep: "vec3(.04,.20,.26)", shal: "vec3(.20,.55,.60)" });
})();
