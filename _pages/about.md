---
permalink: /
title: ""
excerpt: ""
author_profile: true
redirect_from: 
  - /about/
  - /about.html
---

{% if site.google_scholar_stats_use_cdn %}
{% assign gsDataBaseUrl = "https://cdn.jsdelivr.net/gh/" | append: site.repository | append: "@" %}
{% else %}
{% assign gsDataBaseUrl = "https://raw.githubusercontent.com/" | append: site.repository | append: "/" %}
{% endif %}
{% assign url = gsDataBaseUrl | append: "google-scholar-stats/gs_data_shieldsio.json" %}

<span class='anchor' id='about-me'></span>

I am a second-year PhD student at the University of Science and Technology of China, currently pursuing research as an intern at the Beijing Institute for General Artificial Intelligence under the guidance of Professor <a href='http://staff.ustc.edu.cn/~qiliuql/'>Qi Liu</a> and Researcher <a href='https://zilongzheng.github.io/'>Zilong Zheng</a>. I hold a bachelor's degree from Beihang University.

My research interest includes reward modeling, LLMs alignment and continual learning. <a href='https://scholar.google.com/citations?user=GNO0HzAAAAAJ'><img src="https://img.shields.io/endpoint?url={{ url | url_encode }}&logo=Google%20Scholar&labelColor=f6f6f6&color=9cf&style=flat&label=citations"></a>


# 🔥 News
- *2025.10*: &nbsp;🎉🎉 I will serve as reviewer for ACL ARR October.
- *2025.08*: &nbsp;🎉🎉 <a href='https://www.arxiv.org/abs/2509.10515'>UAPO</a> has been accepted by EMNLP 2025!
- *2025.05*: &nbsp;🎉🎉 <a href='https://arxiv.org/abs/2505.16475'>ReflectEvo</a> has been accepted by ACL 2025!
- *2025.01*: &nbsp;🎉🎉 <a href='https://arxiv.org/abs/2406.11194'>ICE</a> has been accepted by ICLR 2025!

# 📝 Publications 

<div class="carousel-wrap">
<button class="carousel-btn carousel-prev" type="button" aria-label="Previous" hidden>&lsaquo;</button>
<div class="paper-carousel">

<div class="paper-card">
<div class="paper-card-media"><span class="badge">EMNLP 2025</span><img src='images/uapo.png' alt="UAPO paper preview" loading="lazy"></div>
<div class="paper-card-body" markdown="1">

[Adaptive Preference Optimization with Uncertainty-aware Utility Anchor](https://www.arxiv.org/abs/2509.10515)

**Xiaobo Wang**, Zixia Jia, Jiaqi Li, Qi Liu, Zilong Zheng

</div>
</div>

<div class="paper-card">
<div class="paper-card-media"><span class="badge">ACL 2025</span><img src='images/reflectevo.jpg' alt="ReflectEvo paper preview" loading="lazy"></div>
<div class="paper-card-body" markdown="1">

[ReflectEvo: Improving Meta Introspection of Small LLMs by Learning Self-Reflection](https://arxiv.org/abs/2505.16475)

Jiaqi Li, Xinyi Dong, Yang Liu, Zhizhuo Yang, Quansen Wang, **Xiaobo Wang**, SongChun Zhu, Zixia Jia, Zilong Zheng

</div>
</div>

<div class="paper-card">
<div class="paper-card-media"><span class="badge">ICLR 2025</span><img src='images/ice.jpg' alt="ICE paper preview" loading="lazy"></div>
<div class="paper-card-body" markdown="1">

[In-Context Editing: Learning Knowledge from Self-Induced Distributions](https://arxiv.org/abs/2406.11194)

Siyuan Qi\*, Bangcheng Yang\*, Kailin Jiang\*, **Xiaobo Wang**, Jiaqi Li, Yifan Zhong, Yaodong Yang, Zilong Zheng

</div>
</div>

</div>
<button class="carousel-btn carousel-next" type="button" aria-label="Next" hidden>&rsaquo;</button>
</div>

# 📄 Preprints

<!-- Replace the placeholder card below with your real preprints.
     Copy a <div class="paper-card"> ... </div> block for each entry. -->
<div class="carousel-wrap">
<button class="carousel-btn carousel-prev" type="button" aria-label="Previous" hidden>&lsaquo;</button>
<div class="paper-carousel">

<div class="paper-card">
<div class="paper-card-media"><span class="badge">Preprint</span><img src='images/500x300.png' alt="preprint preview" loading="lazy"></div>
<div class="paper-card-body" markdown="1">

[Your preprint title goes here](#)

**Xiaobo Wang**, Co-authors

</div>
</div>

</div>
<button class="carousel-btn carousel-next" type="button" aria-label="Next" hidden>&rsaquo;</button>
</div>


<!-- # 🎖 Honors and Awards
- *2021.10* Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus ornare aliquet ipsum, ac tempus justo dapibus sit amet. 
- *2021.09* Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus ornare aliquet ipsum, ac tempus justo dapibus sit amet.  -->

# 📖 Educations
- *2024.06 - now*, University of Science and Technology of China. 
- *2020.09 - 2024.06*, Beihang University, bachelor's degree. 

# 💻 Internships
- *2025.07 - now*, BIGAI, Beijing, China
- *2023.10 - 2024.01*, ByteDance, Beijing, China.

<script>
(function () {
  function initCarousels() {
    document.querySelectorAll('.carousel-wrap').forEach(function (wrap) {
      var track = wrap.querySelector('.paper-carousel');
      if (!track) return;
      var prev = wrap.querySelector('.carousel-prev');
      var next = wrap.querySelector('.carousel-next');

      function step() {
        var card = track.querySelector('.paper-card');
        var style = getComputedStyle(track);
        var gap = parseFloat(style.columnGap || style.gap || '20') || 20;
        return card ? card.offsetWidth + gap : track.clientWidth * 0.8;
      }

      function update() {
        var scrollable = track.scrollWidth - track.clientWidth > 2;
        var atStart = track.scrollLeft <= 2;
        var atEnd = track.scrollLeft >= track.scrollWidth - track.clientWidth - 2;
        wrap.classList.toggle('is-scrollable', scrollable);
        wrap.classList.toggle('at-start', atStart);
        wrap.classList.toggle('at-end', atEnd);
        if (prev) prev.hidden = !scrollable || atStart;
        if (next) next.hidden = !scrollable || atEnd;
      }

      if (prev) prev.addEventListener('click', function () {
        track.scrollBy({ left: -step(), behavior: 'smooth' });
      });
      if (next) next.addEventListener('click', function () {
        track.scrollBy({ left: step(), behavior: 'smooth' });
      });
      track.addEventListener('scroll', update, { passive: true });
      window.addEventListener('resize', update);
      window.addEventListener('load', update);
      update();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCarousels);
  } else {
    initCarousels();
  }
})();
</script>
