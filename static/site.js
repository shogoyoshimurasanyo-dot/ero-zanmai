(function () {
  var grid = document.querySelector('.grid');

  // 年齢確認
  var age = document.getElementById('age');
  var ok = false;
  try { ok = localStorage.getItem('age_ok') === '1'; } catch (e) {}
  if (!ok) age.classList.add('show');
  age.querySelector('.yes').addEventListener('click', function () {
    try { localStorage.setItem('age_ok', '1'); } catch (e) {}
    age.classList.remove('show');
    scrollToHash();
  });

  // 固定メニュー: 外側をタップしたら閉じる
  var menu = document.querySelector('.menu');
  document.addEventListener('click', function (ev) {
    if (menu.open && !menu.contains(ev.target)) menu.open = false;
  });

  // 固定メニューの高さに合わせてアンカー位置をずらす
  var topbar = document.querySelector('.topbar');
  function setTopbarHeight() {
    document.documentElement.style.setProperty('--topbar-h', topbar.offsetHeight + 'px');
  }
  setTopbarHeight();
  window.addEventListener('resize', setTopbarHeight);

  var toastTimer;
  function toast(msg) {
    var t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.classList.remove('show'); }, 1600);
  }

  grid.addEventListener('click', function (ev) {
    // サムネイルをタップしたらサンプル動画プレイヤーに差し替える
    var btn = ev.target.closest('button.media');
    if (btn) {
      var box = document.createElement('div');
      box.className = 'media';
      var f = document.createElement('iframe');
      f.src = btn.dataset.player;
      f.title = btn.getAttribute('aria-label');
      f.allow = 'autoplay; fullscreen; encrypted-media; picture-in-picture';
      f.allowFullscreen = true;
      f.setAttribute('scrolling', 'no');
      f.referrerPolicy = 'no-referrer-when-downgrade';
      box.appendChild(f);
      btn.replaceWith(box);
      return;
    }
    // このブロックへの直リンクをコピー（SNS 用）
    var copy = ev.target.closest('button.copy');
    if (copy) {
      var url = location.origin + location.pathname + '#' + copy.dataset.id;
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(url).then(function () { toast('リンクをコピーしました'); },
          function () { window.prompt('このリンクをコピーしてください', url); });
      } else {
        window.prompt('このリンクをコピーしてください', url);
      }
    }
  });

  // #v-xxx のブロックへ移動。今日のページにない場合は catalog.json から先頭に差し込む
  function scrollToHash() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (!/^v-[0-9a-z_-]+$/.test(id)) return;
    var el = document.getElementById(id);
    if (el) { el.scrollIntoView(); return; }
    fetch(grid.dataset.catalog, { cache: 'no-cache' })
      .then(function (r) { return r.ok ? r.json() : {}; })
      .then(function (catalog) {
        if (!catalog[id] || document.getElementById(id)) return;
        grid.insertAdjacentHTML('afterbegin', catalog[id].html);
        var card = document.getElementById(id);
        card.classList.add('shared');
        card.insertAdjacentHTML('afterbegin', '<div class="shared-label">シェアされた動画</div>');
        card.scrollIntoView();
      })
      .catch(function () {});
  }
  window.addEventListener('hashchange', scrollToHash);
  scrollToHash();
})();
