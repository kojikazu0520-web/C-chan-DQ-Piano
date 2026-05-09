const videos = [
  {
    title: "はじめての人におすすめの代表演奏",
    category: "序曲・代表曲",
    summary: "チャンネルの世界観が最初に伝わる、勇者の旅立ちを思わせる代表演奏の入口です。",
    audience: "初見ユーザー",
    tags: ["代表作", "冒険の入口", "おすすめ"],
    url: "https://www.youtube.com/@chamberd_piano"
  },
  {
    title: "町や村を思わせる、やさしい演奏",
    category: "街・安らぎ",
    summary: "落ち着いた街曲や温かい場面を連想させる演奏をまとめるための枠です。",
    audience: "癒やされたい人",
    tags: ["静か", "安心感", "BGM向け"],
    url: "https://www.youtube.com/@chamberd_piano"
  },
  {
    title: "フィールドを旅したくなる演奏",
    category: "冒険・フィールド",
    summary: "広がりのあるメロディで、旅の高揚感や世界の広さを感じられる演奏を想定しています。",
    audience: "冒険感を味わいたい人",
    tags: ["旅", "広がり", "世界観"],
    url: "https://www.youtube.com/@chamberd_piano"
  },
  {
    title: "戦闘シーンの熱量を感じる演奏",
    category: "バトル",
    summary: "緊張感や勢いのある演奏をまとめて、テンションの高い曲を探しやすくするカテゴリです。",
    audience: "熱い曲を聴きたい人",
    tags: ["バトル", "迫力", "盛り上がる"],
    url: "https://www.youtube.com/@chamberd_piano"
  },
  {
    title: "印象深い名曲をじっくり味わう演奏",
    category: "名曲・人気曲",
    summary: "印象に残りやすい人気曲や、繰り返し聴きたくなる名曲をまとめる想定です。",
    audience: "好きな曲を探す人",
    tags: ["名曲", "人気", "リピート向け"],
    url: "https://www.youtube.com/@chamberd_piano"
  },
  {
    title: "最新投稿から追いかけたい人向け",
    category: "最新投稿",
    summary: "新しい投稿を追う視聴者向けに、更新導線を分かりやすく見せるための枠です。",
    audience: "継続視聴者",
    tags: ["新着", "更新", "フォロー向け"],
    url: "https://www.youtube.com/@chamberd_piano"
  },
  {
    title: "長く聴けるBGM向けまとめ",
    category: "癒やし・作業用",
    summary: "しっとりした演奏や穏やかな空気の曲をまとめて、作業用や休憩時間に使いやすくします。",
    audience: "作業用に聴きたい人",
    tags: ["長時間", "BGM", "集中"],
    url: "https://www.youtube.com/@chamberd_piano"
  }
];

const state = {
  activeCategory: "すべて"
};

const elements = {
  filterChips: document.getElementById("filterChips"),
  videoGrid: document.getElementById("videoGrid")
};

function categoriesFrom(items) {
  return ["すべて", ...new Set(items.map((item) => item.category))];
}

function filteredVideos() {
  if (state.activeCategory === "すべて") {
    return videos;
  }

  return videos.filter((video) => video.category === state.activeCategory);
}

function renderChips() {
  elements.filterChips.innerHTML = categoriesFrom(videos)
    .map((category) => {
      const className = category === state.activeCategory ? "chip is-active" : "chip";
      return `<button class="${className}" type="button" data-category="${category}">${category}</button>`;
    })
    .join("");
}

function renderVideos() {
  const items = filteredVideos();

  elements.videoGrid.innerHTML = items
    .map((video) => `
      <article class="video-card">
        <p class="video-meta">${video.category} / ${video.audience}</p>
        <h3>${video.title}</h3>
        <p>${video.summary}</p>
        <div class="video-tags">
          ${video.tags.map((tag) => `<span>${tag}</span>`).join("")}
        </div>
        <a class="video-link" href="${video.url}" target="_blank" rel="noreferrer">YouTubeで見る</a>
      </article>
    `)
    .join("");
}

elements.filterChips.addEventListener("click", (event) => {
  const button = event.target.closest("[data-category]");
  if (!button) {
    return;
  }

  state.activeCategory = button.dataset.category;
  renderChips();
  renderVideos();
});

renderChips();
renderVideos();
