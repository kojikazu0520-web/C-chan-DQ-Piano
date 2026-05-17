const locale = document.documentElement.lang === "en" ? "en" : "ja";
const staticContent = window.siteContentData?.[locale];
const uiContent = staticContent?.ui;

const CATEGORY_KEYS = {
  all: "all",
  medley: "medley",
  battle: "battle",
  project: "project",
  series: "series"
};

const SERIES_ORDER = {
  I: 1,
  II: 2,
  III: 3,
  IV: 4,
  V: 5,
  VI: 6,
  VII: 7,
  VIII: 8,
  IX: 9,
  X: 10,
  XI: 11
};

const FALLBACK_MESSAGES = {
  ja: {
    categoryLabels: {
      [CATEGORY_KEYS.all]: "すべて",
      [CATEGORY_KEYS.medley]: "メドレー",
      [CATEGORY_KEYS.battle]: "戦闘曲",
      [CATEGORY_KEYS.project]: "企画",
      [CATEGORY_KEYS.series]: "作品別"
    },
    descriptions: {
      [CATEGORY_KEYS.medley]: "複数曲をまとめて楽しめるプレイリストです。流し聴きや世界観に浸りたいときに向いています。",
      [CATEGORY_KEYS.battle]: "熱量の高いバトル系演奏をまとめたプレイリストです。迫力あるドラクエサウンドを続けて楽しめます。",
      [CATEGORY_KEYS.project]: "演奏以外の企画要素も楽しめるプレイリストです。チャンネルの広がりを感じたい人向けです。",
      [CATEGORY_KEYS.series]: "作品ごとに整理されたプレイリストです。好きなナンバリングから順番にたどれます。"
    },
    sectionTitles: {
      medley: "メドレー",
      series: "作品別",
      other: "その他"
    },
    summary: (total, activeLabel, count) =>
      `公開中のプレイリスト ${total}件を表示中${activeLabel === "すべて" ? "" : ` / ${activeLabel} ${count}件`}`,
    openPlaylist: "プレイリストを開く",
    trackCount: (count) => `${count} tracks`,
    songTableTitle: "収録曲一覧",
    songCategoryAll: "すべて",
    songCategorySummary: (total, activeLabel, count) => `カテゴリ ${total}種 / ${activeLabel} の曲 ${count}件を表示中`,
    headers: {
      number: "曲番号",
      title: "曲タイトル",
      series: "作品",
      category: "カテゴリ",
      difficulty: "難易度"
    },
    noDifficulty: "-"
  },
  en: {
    categoryLabels: {
      [CATEGORY_KEYS.all]: "All",
      [CATEGORY_KEYS.medley]: "Medleys",
      [CATEGORY_KEYS.battle]: "Battle Themes",
      [CATEGORY_KEYS.project]: "Projects",
      [CATEGORY_KEYS.series]: "By Series"
    },
    descriptions: {
      [CATEGORY_KEYS.medley]: "A playlist of medleys for relaxed listening and full Dragon Quest atmosphere.",
      [CATEGORY_KEYS.battle]: "A collection of battle-focused performances with more drive and intensity.",
      [CATEGORY_KEYS.project]: "A playlist for special uploads and side projects beyond the standard series playlists.",
      [CATEGORY_KEYS.series]: "Playlists arranged by game title so you can jump straight into your favorite Dragon Quest entry."
    },
    sectionTitles: {
      medley: "Medleys",
      series: "By Series",
      other: "Other Playlists"
    },
    summary: (total, activeLabel, count) =>
      `Showing ${total} public playlists${activeLabel === "All" ? "" : ` / ${activeLabel}: ${count}`}`,
    openPlaylist: "Open playlist",
    trackCount: (count) => `${count} tracks`,
    songTableTitle: "Track List",
    songCategoryAll: "All",
    songCategorySummary: (total, activeLabel, count) => `Showing ${count} songs in ${activeLabel} across ${total} categories`,
    headers: {
      number: "No.",
      title: "Title",
      series: "Series",
      category: "Category",
      difficulty: "Difficulty"
    },
    noDifficulty: "-"
  }
};

const fallback = FALLBACK_MESSAGES[locale];
const t = {
  ...fallback,
  ...(uiContent || {}),
  summary: fallback.summary,
  trackCount: fallback.trackCount
};
const fallbackPlaylists = [];
const songReferenceData = window.songReferenceData || {};
const translationData = window.songTitleTranslations?.[locale] || {};
const EN_CATEGORY_FALLBACKS = {
  "イベント": "Event",
  "エンディング": "Ending",
  "オープニング": "Opening",
  "カジノ": "Casino",
  "キャラクターテーマ": "Character Theme",
  "ダンジョン": "Dungeon",
  "フィールド": "Field",
  "プロローグ": "Prologue",
  "ボス戦闘": "Boss Battle",
  "全滅": "Game Over",
  "城": "Castle",
  "場面転換": "Interlude",
  "塔": "Tower",
  "教会・ほこら": "Churches & Shrines",
  "海": "Sea",
  "空": "Sky",
  "街・村": "Towns & Villages",
  "通常戦闘": "Normal Battle"
};

const playlists = (window.playlistData || fallbackPlaylists)
  .map((playlist) => ({
    ...playlist,
    categoryKey: inferCategory(playlist.title),
    seriesKey: inferSeriesKey(playlist.title),
    shortDescription: buildDescription(playlist),
    publishedYear: playlist.publishedAt ? new Date(playlist.publishedAt).getFullYear() : "",
    countLabel: playlist.itemCountText || (playlist.itemCount ? `全${playlist.itemCount}本` : ""),
    seriesOrder: inferSeriesOrder(playlist.title)
  }))
  .sort(comparePlaylists);

const songBrowseRows = Object.entries(songReferenceData)
  .flatMap(([seriesKey, rows]) =>
    (rows || []).map((row) => ({
      ...row,
      seriesKey,
      seriesOrder: SERIES_ORDER[seriesKey] ?? Number.POSITIVE_INFINITY
    }))
  )
  .filter((row) => row.category && row.category.trim())
  .sort(compareSongBrowseRows);

const state = {
  activeCategory: CATEGORY_KEYS.all,
  activeSongCategory: "__all__"
};

const SECTION_HASHES = new Set(["#library", "#song-browser"]);

const elements = {
  filterChips: document.getElementById("filterChips"),
  videoGrid: document.getElementById("videoGrid"),
  playlistSummary: document.getElementById("playlistSummary"),
  songCategoryChips: document.getElementById("songCategoryChips"),
  songCategoryResults: document.getElementById("songCategoryResults"),
  songCategorySummary: document.getElementById("songCategorySummary"),
  disclosures: document.querySelectorAll(".section-disclosure")
};

function inferCategory(title) {
  const normalized = title.toLowerCase();

  if (normalized.includes("medley") || title.includes("メドレー")) {
    return CATEGORY_KEYS.medley;
  }

  if (normalized.includes("battle") || title.includes("戦闘")) {
    return CATEGORY_KEYS.battle;
  }

  if (title.includes("ゲームプレイ")) {
    return CATEGORY_KEYS.project;
  }

  return CATEGORY_KEYS.series;
}

function inferSeriesKey(title) {
  const match = title.toUpperCase().match(/DRAGON QUEST\s*(XI|X|IX|VIII|VII|VI|V|IV|III|II|I)\b/);
  return match ? match[1] : "";
}

function inferSeriesOrder(title) {
  const key = inferSeriesKey(title);
  return SERIES_ORDER[key] ?? Number.POSITIVE_INFINITY;
}

function buildDescription(playlist) {
  if (playlist.description && playlist.description.trim()) {
    return playlist.description.trim().split("\n")[0];
  }

  return t.descriptions[playlist.categoryKey] || t.descriptions[CATEGORY_KEYS.series];
}

function escapeHtml(value = "") {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll('"', "&quot;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function renderThumbnail(playlist) {
  const primarySrc = escapeHtml(playlist.thumbnail || "");
  const alt = escapeHtml(playlist.title || "");
  const fallbackHandler = `this.onerror=null;this.closest('article')?.classList.add('thumb-missing');this.remove();`;

  return `<img class="playlist-thumb" src="${primarySrc}" alt="${alt}" loading="lazy" onerror="${fallbackHandler}">`;
}

function comparePlaylists(a, b) {
  if (a.categoryKey === CATEGORY_KEYS.medley && b.categoryKey !== CATEGORY_KEYS.medley) {
    return -1;
  }

  if (a.categoryKey !== CATEGORY_KEYS.medley && b.categoryKey === CATEGORY_KEYS.medley) {
    return 1;
  }

  if (a.categoryKey === CATEGORY_KEYS.series && b.categoryKey === CATEGORY_KEYS.series && a.seriesOrder !== b.seriesOrder) {
    return a.seriesOrder - b.seriesOrder;
  }

  if (a.categoryKey === CATEGORY_KEYS.series && b.categoryKey !== CATEGORY_KEYS.series) {
    return -1;
  }

  if (a.categoryKey !== CATEGORY_KEYS.series && b.categoryKey === CATEGORY_KEYS.series) {
    return 1;
  }

  return a.title.localeCompare(b.title, "ja");
}

function compareSongBrowseRows(a, b) {
  if (a.seriesOrder !== b.seriesOrder) {
    return a.seriesOrder - b.seriesOrder;
  }

  if (a.sortNumber !== b.sortNumber) {
    return a.sortNumber - b.sortNumber;
  }

  return `${a.id}`.localeCompare(`${b.id}`, "ja");
}

function categoriesFrom(items) {
  return [CATEGORY_KEYS.all, ...new Set(items.map((item) => item.categoryKey))];
}

function filteredPlaylists() {
  if (state.activeCategory === CATEGORY_KEYS.all) {
    return playlists;
  }

  return playlists.filter((playlist) => playlist.categoryKey === state.activeCategory);
}

function songCategoriesFrom(items) {
  const categories = [...new Set(items.map((item) => item.category).filter(Boolean))];
  return categories.sort((a, b) => a.localeCompare(b, "ja"));
}

function filteredSongBrowseRows() {
  if (state.activeSongCategory === "__all__") {
    return songBrowseRows;
  }

  return songBrowseRows.filter((row) => row.category === state.activeSongCategory);
}

function updateDisclosureLabel(details) {
  const label = details?.querySelector(".section-toggle-label");
  if (!label) {
    return;
  }

  label.textContent = details.open ? label.dataset.closeLabel : label.dataset.openLabel;
}

function openDisclosureByHash(hash) {
  if (!SECTION_HASHES.has(hash)) {
    return;
  }

  const section = document.querySelector(hash);
  const details = section?.querySelector(".section-disclosure");
  if (!details) {
    return;
  }

  details.open = true;
  updateDisclosureLabel(details);
}

function setupDisclosures() {
  elements.disclosures.forEach((details) => {
    updateDisclosureLabel(details);
    details.addEventListener("toggle", () => updateDisclosureLabel(details));
  });

  openDisclosureByHash(window.location.hash);
  window.addEventListener("hashchange", () => openDisclosureByHash(window.location.hash));
}

function renderSummary(items) {
  if (!elements.playlistSummary) {
    return;
  }

  const activeLabel = t.categoryLabels[state.activeCategory];
  elements.playlistSummary.textContent = t.summary(playlists.length, activeLabel, items.length);
}

function renderSongCategorySummary(items) {
  if (!elements.songCategorySummary) {
    return;
  }

  const activeLabel =
    state.activeSongCategory === "__all__"
      ? t.songCategoryAll
      : translateSongCategory(state.activeSongCategory);

  elements.songCategorySummary.textContent = t.songCategorySummary(songCategoriesFrom(songBrowseRows).length, activeLabel, items.length);
}

function renderChips() {
  elements.filterChips.innerHTML = categoriesFrom(playlists)
    .map((category) => {
      const className = category === state.activeCategory ? "chip is-active" : "chip";
      return `<button class="${className}" type="button" data-category="${category}">${t.categoryLabels[category]}</button>`;
    })
    .join("");
}

function renderSongCategoryChips() {
  if (!elements.songCategoryChips) {
    return;
  }

  const categories = ["__all__", ...songCategoriesFrom(songBrowseRows)];
  elements.songCategoryChips.innerHTML = categories
    .map((category) => {
      const label = category === "__all__" ? t.songCategoryAll : translateSongCategory(category);
      const className = category === state.activeSongCategory ? "chip is-active" : "chip";
      return `<button class="${className}" type="button" data-song-category="${escapeHtml(category)}">${escapeHtml(label)}</button>`;
    })
    .join("");
}

function renderListCard(playlist) {
  return `
    <article class="video-card video-card-list">
      ${renderThumbnail(playlist)}
      <div class="video-card-body">
        <p class="video-meta">${t.categoryLabels[playlist.categoryKey]}${playlist.publishedYear ? ` / ${playlist.publishedYear}` : ""}</p>
        <h3>${playlist.title}</h3>
        <p>${playlist.shortDescription}</p>
        ${playlist.countLabel ? `<span class="playlist-count">${playlist.countLabel}</span>` : ""}
        <div class="video-tags">
          <span>${t.categoryLabels[playlist.categoryKey]}</span>
          ${playlist.itemCount ? `<span>${t.trackCount(playlist.itemCount)}</span>` : ""}
          ${playlist.publishedYear ? `<span>${playlist.publishedYear}</span>` : ""}
        </div>
        <a class="video-link" href="${playlist.url}" target="_blank" rel="noreferrer">${t.openPlaylist}</a>
      </div>
    </article>
  `;
}

function renderGridCard(playlist) {
  const tableMarkup = playlist.categoryKey === CATEGORY_KEYS.series ? renderSongTable(playlist.seriesKey) : "";

  return `
    <article class="video-card video-card-grid">
      ${renderThumbnail(playlist)}
      <p class="video-meta">${t.categoryLabels[playlist.categoryKey]}${playlist.publishedYear ? ` / ${playlist.publishedYear}` : ""}</p>
      <h3>${playlist.title}</h3>
      <p>${playlist.shortDescription}</p>
      ${playlist.countLabel ? `<span class="playlist-count">${playlist.countLabel}</span>` : ""}
      <div class="video-tags">
        ${playlist.itemCount ? `<span>${t.trackCount(playlist.itemCount)}</span>` : ""}
        ${playlist.publishedYear ? `<span>${playlist.publishedYear}</span>` : ""}
      </div>
      ${tableMarkup}
      <a class="video-link" href="${playlist.url}" target="_blank" rel="noreferrer">${t.openPlaylist}</a>
    </article>
  `;
}

function renderSongTable(seriesKey) {
  const rows = songReferenceData[seriesKey] || [];
  if (!rows.length) {
    return "";
  }

  return `
    <div class="song-table-wrap">
      <p class="song-table-title">${t.songTableTitle}</p>
      <div class="song-table-scroll">
        <table class="song-table">
          <thead>
            <tr>
              <th>${t.headers.number}</th>
              <th>${t.headers.title}</th>
              <th>${t.headers.category}</th>
              <th>${t.headers.difficulty}</th>
            </tr>
          </thead>
          <tbody>
            ${rows.map(renderSongRow).join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function renderSongBrowseTable() {
  const rows = filteredSongBrowseRows();
  renderSongCategorySummary(rows);

  if (!elements.songCategoryResults) {
    return;
  }

  elements.songCategoryResults.innerHTML = `
    <div class="song-table-wrap song-browser-table-wrap">
      <div class="song-table-scroll">
        <table class="song-table song-browser-table">
          <thead>
            <tr>
              <th>${t.headers.number}</th>
              <th>${t.headers.title}</th>
              <th>${t.headers.category}</th>
              <th>${t.headers.difficulty}</th>
            </tr>
          </thead>
          <tbody>
            ${rows.map(renderSongBrowseRow).join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function renderSongRow(row) {
  const displayTitle = translateSongTitle(row);
  const displayCategory = translateSongCategory(row.category);
  const displayDifficulty = translateDifficulty(row.difficultyLabel);
  const number = row.videoUrl
    ? `<a class="song-link song-number-link" href="${row.videoUrl}" target="_blank" rel="noreferrer">${row.id}</a>`
    : row.id;
  const title = row.videoUrl
    ? `<a class="song-link" href="${row.videoUrl}" target="_blank" rel="noreferrer">${displayTitle}</a>`
    : `<span class="song-text">${displayTitle}</span>`;

  const difficulty = renderDifficultyCell(displayDifficulty, row.difficultyStars);

  return `
    <tr>
      <td class="song-number">${number}</td>
      <td class="song-title-cell">${title}</td>
      <td>${displayCategory || ""}</td>
      <td>${difficulty}</td>
    </tr>
  `;
}

function renderSongBrowseRow(row) {
  const displayTitle = translateSongTitle(row);
  const displayCategory = translateSongCategory(row.category);
  const displayDifficulty = translateDifficulty(row.difficultyLabel);
  const number = row.videoUrl
    ? `<a class="song-link song-number-link" href="${row.videoUrl}" target="_blank" rel="noreferrer">${row.id}</a>`
    : row.id;
  const title = row.videoUrl
    ? `<a class="song-link" href="${row.videoUrl}" target="_blank" rel="noreferrer">${displayTitle}</a>`
    : `<span class="song-text">${displayTitle}</span>`;

  const difficulty = renderDifficultyCell(displayDifficulty, row.difficultyStars);

  return `
    <tr>
      <td class="song-number">${number}</td>
      <td class="song-title-cell">${title}</td>
      <td>${displayCategory || ""}</td>
      <td>${difficulty}</td>
    </tr>
  `;
}

function translateSongTitle(rowOrValue) {
  if (typeof rowOrValue === "object" && rowOrValue) {
    const byId = translationData.titlesById?.[rowOrValue.id];
    if (byId) {
      return byId;
    }

    const byTitle = translationData.titles?.[rowOrValue.songTitle];
    return byTitle || rowOrValue.songTitle;
  }

  return translationData.titles?.[rowOrValue] || rowOrValue;
}

function renderDifficultyCell(label, stars) {
  if (!label) {
    return `<span class="difficulty-text">${t.noDifficulty}</span>`;
  }

  const filled = Number.isFinite(stars) ? Math.max(0, Math.min(5, stars)) : 0;
  const empty = 5 - filled;
  const starText = `${"★".repeat(filled)}${"☆".repeat(empty)}`;
  const meter = filled
    ? `<span class="difficulty-stars" aria-label="${label} ${filled}/5">${starText}</span>`
    : `<span class="difficulty-stars is-empty" aria-label="${label}">${"☆".repeat(5)}</span>`;

  return `<span class="difficulty-cell"><span class="difficulty-text">${label}</span>${meter}</span>`;
}

function translateSongCategory(value) {
  if (translationData.categories?.[value]) {
    return translationData.categories[value];
  }

  if (locale === "en" && EN_CATEGORY_FALLBACKS[value]) {
    return EN_CATEGORY_FALLBACKS[value];
  }

  return value;
}

function translateDifficulty(value) {
  return translationData.difficulties?.[value] || value;
}

function renderSection(title, className, items, renderer) {
  if (!items.length) {
    return "";
  }

  return `
    <section class="playlist-section ${className}">
      <h3 class="playlist-group-title">${title}</h3>
      <div class="${className}-items">
        ${items.map(renderer).join("")}
      </div>
    </section>
  `;
}

function renderPlaylists() {
  const items = filteredPlaylists();
  renderSummary(items);

  if (state.activeCategory !== CATEGORY_KEYS.all) {
    if (state.activeCategory === CATEGORY_KEYS.medley) {
      elements.videoGrid.innerHTML = renderSection(t.sectionTitles.medley, "playlist-list-stack", items, renderListCard);
      return;
    }

    if (state.activeCategory === CATEGORY_KEYS.series) {
      elements.videoGrid.innerHTML = renderSection(t.sectionTitles.series, "playlist-grid-2", items, renderGridCard);
      return;
    }

    elements.videoGrid.innerHTML = renderSection(t.categoryLabels[state.activeCategory], "playlist-grid-3", items, renderGridCard);
    return;
  }

  const medleys = items.filter((item) => item.categoryKey === CATEGORY_KEYS.medley);
  const series = items.filter((item) => item.categoryKey === CATEGORY_KEYS.series);
  const others = items.filter((item) => item.categoryKey !== CATEGORY_KEYS.medley && item.categoryKey !== CATEGORY_KEYS.series);

  elements.videoGrid.innerHTML = [
    renderSection(t.sectionTitles.medley, "playlist-list-stack", medleys, renderListCard),
    renderSection(t.sectionTitles.series, "playlist-grid-2", series, renderGridCard),
    renderSection(t.sectionTitles.other, "playlist-grid-3", others, renderGridCard)
  ].join("");
}

if (elements.filterChips && elements.videoGrid) {
  elements.filterChips.addEventListener("click", (event) => {
    const button = event.target.closest("[data-category]");
    if (!button) {
      return;
    }

    state.activeCategory = button.dataset.category;
    renderChips();
    renderPlaylists();
  });

  renderChips();
  renderPlaylists();
}

setupDisclosures();

if (elements.songCategoryChips && elements.songCategoryResults) {
  elements.songCategoryChips.addEventListener("click", (event) => {
    const button = event.target.closest("[data-song-category]");
    if (!button) {
      return;
    }

    state.activeSongCategory = button.dataset.songCategory;
    renderSongCategoryChips();
    renderSongBrowseTable();
  });

  renderSongCategoryChips();
  renderSongBrowseTable();
}




