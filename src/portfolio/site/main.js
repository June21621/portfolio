// 순수 JS. 서버 기능에 기대지 않으며, 아래 두 기능 모두 실패해도 페이지는 그대로 보인다.
document.documentElement.classList.add("js");

// 1) 스크롤 진입 시 살짝 나타나기
(() => {
  const items = document.querySelectorAll(".reveal");
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce || !("IntersectionObserver" in window)) {
    items.forEach((el) => el.classList.add("is-visible"));
    return;
  }
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        io.unobserve(entry.target);
      });
    },
    { rootMargin: "0px 0px -10% 0px", threshold: 0.1 },
  );
  items.forEach((el) => io.observe(el));
})();

// 2) 클러스터에서 배포 정보 표시. /version이 없으면(S3 등) 조용히 숨긴 채로 둔다.
//    기대하는 응답: { "version": "<git sha>", "build_time": "...", "pod_name": "..." }
(async () => {
  const el = document.querySelector("[data-deploy]");
  if (!el) return;
  try {
    const res = await fetch("/version", { cache: "no-store" });
    if (!res.ok) return;
    const info = await res.json();
    if (!info || !info.version) return;
    const parts = [`배포 ${String(info.version).slice(0, 7)}`];
    if (info.pod_name) parts.push(info.pod_name);
    el.textContent = parts.join(" / ");
    el.hidden = false;
  } catch {
    // 정적 호스팅에서는 정상적인 경우다
  }
})();

// 3) 저작권 연도
document.querySelectorAll("[data-year]").forEach((el) => {
  el.textContent = String(new Date().getFullYear());
});
