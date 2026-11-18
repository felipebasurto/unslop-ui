/*
 * Blueprint: mounts a sheet from a <template> and draws dimensions, rule tags
 * and specs over it. Every number is read from the rendered DOM at 1x, so the
 * drawing cannot drift from the layout it describes.
 */
(function () {
  var NS = 'http://www.w3.org/2000/svg';
  var TICK = 4;

  function q(sel, root) { return (root || document).querySelector(sel); }
  function qa(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }
  function svgEl(name, attrs, parent) {
    var n = document.createElementNS(NS, name);
    Object.keys(attrs).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (parent) parent.appendChild(n);
    return n;
  }
  function box(el, canvas) {
    var c = canvas.getBoundingClientRect();
    var r = el.getBoundingClientRect();
    return {
      l: r.left - c.left, r: r.right - c.left,
      t: r.top - c.top, b: r.bottom - c.top,
      w: r.width, h: r.height
    };
  }
  function num(n) { return String(Math.round(n * 10) / 10); }

  // A value sitting on a dimension line, with a background so the line breaks around it.
  function label(g, x, y, text) {
    var t = svgEl('text', { x: x, y: y, 'text-anchor': 'middle', 'dominant-baseline': 'middle' }, g);
    t.textContent = text;
    var b = t.getBBox();
    var bg = svgEl('rect', { x: b.x - 4, y: b.y - 1, width: b.width + 8, height: b.height + 2 }, g);
    g.insertBefore(bg, t);
  }
  function tick(g, x, y) {
    svgEl('line', { class: 'tick', x1: x - TICK, y1: y + TICK, x2: x + TICK, y2: y - TICK }, g);
  }

  // Horizontal dimension from x1 to x2 on height y. fromY: where the features are,
  // so extension lines run from them to the dimension line.
  function hDim(svg, x1, x2, y, text, fromY) {
    var g = svgEl('g', { class: 'dim' }, svg);
    if (fromY !== undefined) {
      var end = y + (y > fromY ? 4 : -4);
      svgEl('line', { class: 'ext', x1: x1, y1: fromY, x2: x1, y2: end }, g);
      svgEl('line', { class: 'ext', x1: x2, y1: fromY, x2: x2, y2: end }, g);
    }
    svgEl('line', { class: 'dimline', x1: x1, y1: y, x2: x2, y2: y }, g);
    tick(g, x1, y);
    tick(g, x2, y);
    label(g, (x1 + x2) / 2, y, text);
  }

  // Vertical dimension from y1 to y2 at x. fromX: where the features are.
  function vDim(svg, x, y1, y2, text, fromX) {
    var g = svgEl('g', { class: 'dim' }, svg);
    if (fromX !== undefined) {
      var end = x + (x > fromX ? 4 : -4);
      svgEl('line', { class: 'ext', x1: fromX, y1: y1, x2: end, y2: y1 }, g);
      svgEl('line', { class: 'ext', x1: fromX, y1: y2, x2: end, y2: y2 }, g);
    }
    svgEl('line', { class: 'dimline', x1: x, y1: y1, x2: x, y2: y2 }, g);
    tick(g, x, y1);
    tick(g, x, y2);
    label(g, x, (y1 + y2) / 2, text);
  }

  function layout(canvas, svg, sheet, tags) {
    var S = box(sheet, canvas);
    var btn = qa('.btn', sheet)[0];
    var B = box(btn, canvas);
    var CL = B.l, CR = B.r;                       // content edges (inside the padding)
    var title = box(q('.title', sheet), canvas);
    var midY = (title.t + title.b) / 2;           // header row

    // Overall size
    hDim(svg, S.l, S.r, S.t - 48, num(S.w), S.t);
    vDim(svg, S.r + 84, S.t, S.b, num(S.h), S.r);
    hDim(svg, CL, CR, S.b + 34, num(CR - CL), S.b); // content width

    // Paddings on the header row
    hDim(svg, S.l, box(q('.close', sheet), canvas).l, midY, num(CL - S.l));
    hDim(svg, CR, S.r, midY, num(S.r - CR));

    // Every child: its height on the right, and the gap above it on the left
    var prev = S.t;
    Array.prototype.slice.call(sheet.children).forEach(function (k) {
      var K = box(k, canvas);
      if (K.h < 0.5) return;
      if (K.t - prev > 0.5) vDim(svg, S.l - 30, prev, K.t, num(K.t - prev), S.l);
      vDim(svg, S.r + 30, K.t, K.b, num(K.h), CR);
      prev = K.b;
    });
    if (S.b - prev > 0.5) vDim(svg, S.l - 30, prev, S.b, num(S.b - prev), S.l);

    // Rule tags: a column left of the sheet, each with a leader to its element
    qa('[data-tag]', sheet).forEach(function (n, i) {
      var parts = n.getAttribute('data-tag').split('|');
      var R = box(n, canvas);
      var cy = (R.t + R.b) / 2;
      var kind = /^U\d/.test(parts[0]) ? 'rule' : (parts[0] === 'KEEP' ? 'keep' : 'state');

      var tag = document.createElement('div');
      tag.className = 'tag tag--' + kind;
      tag.style.top = (cy - 12) + 'px';
      var b = document.createElement('b');
      b.textContent = parts[0];
      tag.appendChild(b);
      tag.appendChild(document.createTextNode(parts[1]));
      tags.appendChild(tag);

      svgEl('line', { class: 'leader tag-leader', x1: 300, y1: cy, x2: R.l - 2, y2: cy }, svg);
    });

    // Specs: measured font size, line height, weight, button height and radius
    qa('.title, .copy, .btn, .foot', sheet).forEach(function (n) {
      var cs = getComputedStyle(n);
      var R = box(n, canvas);
      var cy = (R.t + R.b) / 2;
      var fs = parseFloat(cs.fontSize);
      var lh = parseFloat(cs.lineHeight);
      var text;
      if (n.classList.contains('btn')) {
        text = 'BTN  h' + num(R.h) + '  ' + fs + 'px w' + cs.fontWeight +
               '  r' + parseFloat(cs.borderTopLeftRadius);
      } else if (n.classList.contains('title')) {
        text = 'H2  ' + fs + '/' + lh + '  w' + cs.fontWeight;
      } else {
        text = 'P  ' + fs + '/' + lh;
      }
      svgEl('line', { class: 'spec-leader', x1: R.r + 6, y1: cy, x2: 952, y2: cy }, svg);
      var t = svgEl('text', { class: 'spec', x: 960, y: cy, 'dominant-baseline': 'middle' }, svg);
      t.textContent = text;
    });
  }

  function mount(name) {
    var canvas = q('#canvas');
    var slot = q('#sheet-slot');
    var svg = q('#dims');
    var tags = q('#tags');
    var tpl = document.getElementById('tpl-' + name);

    slot.innerHTML = '';
    slot.appendChild(tpl.content.cloneNode(true));
    // Copy first: removing from a live HTMLCollection while iterating it skips nodes.
    Array.prototype.slice.call(svg.children).forEach(function (n) { n.parentNode.removeChild(n); });
    tags.innerHTML = '';

    var sheet = q('.sheet', slot);
    layout(canvas, svg, sheet, tags);

    var state = q('#state');
    if (state) state.textContent = name.toUpperCase();
    return sheet;
  }

  window.Blueprint = { mount: mount };
})();
