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

<div class='paper-box'><div class='paper-box-image'><div><div class="badge">TMLR</div><img src='images/memory.png' alt="The AI Hippocampus framework overview" width="100%" loading="lazy"></div></div>
<div class='paper-box-text' markdown="1">

[The AI Hippocampus: How Far are We From Human Memory?](https://arxiv.org/abs/2601.09113)

Zixia Jia, Jiaqi Li, Yipeng Kang, Yuxuan Wang, Tong Wu, Quansen Wang, **Xiaobo Wang**, Shuyi Zhang, Junzhe Shen, Qing Li, Siyuan Qi, Yitao Liang, Di He, Zilong Zheng, Song-Chun Zhu

</div>
</div>

<div class='paper-box'><div class='paper-box-image'><div><div class="badge">ICLR 2026</div><img src='images/policon.png' alt="PoliCon framework overview" width="100%" loading="lazy"></div></div>
<div class='paper-box-text' markdown="1">

[PoliCon: Evaluating LLMs on Achieving Diverse Political Consensus Objectives](https://arxiv.org/abs/2505.19558)

Zhaowei Zhang, **Xiaobo Wang**, Minghua Yi, Mengmeng Wang, Fengshuo Bai, Zilong Zheng, Yipeng Kang, Yaodong Yang

</div>
</div>

<div class='paper-box'><div class='paper-box-image'><div><div class="badge">EMNLP 2025</div><img src='images/uapo.png' alt="UAPO paper preview" width="100%" loading="lazy"></div></div>
<div class='paper-box-text' markdown="1">

[Adaptive Preference Optimization with Uncertainty-aware Utility Anchor](https://www.arxiv.org/abs/2509.10515)

**Xiaobo Wang**, Zixia Jia, Jiaqi Li, Qi Liu, Zilong Zheng

</div>
</div>

<div class='paper-box'><div class='paper-box-image'><div><div class="badge">ACL 2025</div><img src='images/reflectevo.jpg' alt="ReflectEvo paper preview" width="100%" loading="lazy"></div></div>
<div class='paper-box-text' markdown="1">

[ReflectEvo: Improving Meta Introspection of Small LLMs by Learning Self-Reflection](https://arxiv.org/abs/2505.16475)

Jiaqi Li, Xinyi Dong, Yang Liu, Zhizhuo Yang, Quansen Wang, **Xiaobo Wang**, SongChun Zhu, Zixia Jia, Zilong Zheng

</div>
</div>

<div class='paper-box'><div class='paper-box-image'><div><div class="badge">ICLR 2025</div><img src='images/ice.jpg' alt="ICE paper preview" width="100%" loading="lazy"></div></div>
<div class='paper-box-text' markdown="1">

[In-Context Editing: Learning Knowledge from Self-Induced Distributions](https://arxiv.org/abs/2406.11194)

Siyuan Qi\*, Bangcheng Yang\*, Kailin Jiang\*, **Xiaobo Wang**, Jiaqi Li, Yifan Zhong, Yaodong Yang, Zilong Zheng

</div>
</div>

# 📄 Preprints

<div class='paper-box'><div class='paper-box-image'><div><div class="badge">Preprint</div><img src='images/save.png' alt="SAVE framework overview" width="100%" loading="lazy"></div></div>
<div class='paper-box-text' markdown="1">

[The Flip Side of RLHF: On-Policy Feedback for Reward Model Self-Supervised Improvement](https://arxiv.org/abs/2605.30888)

**Xiaobo Wang**, Tong Wu, Min Tang, Jiaqi Li, Qi Liu, Zilong Zheng

</div>
</div>

<div class='paper-box'><div class='paper-box-image'><div><div class="badge">Preprint</div><img src='images/ram.png' alt="RAM framework overview" width="100%" loading="lazy"></div></div>
<div class='paper-box-text' markdown="1">

[RAM: Towards an Ever-Improving Memory System by Learning from Communications](https://arxiv.org/abs/2404.12045)

Jiaqi Li, **Xiaobo Wang**, Wentao Ding, Zihao Wang, Yipeng Kang, Zixia Jia, Zilong Zheng

</div>
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
