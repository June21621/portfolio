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

// 3) 프로젝트 상세 팝업. 카드(링크·버튼 제외)나 "자세히 보기"를 누르면 열린다.
//    주소에 #project-... 가 붙어 있으면 해당 팝업을 바로 연다(링크 공유용).
(() => {
  const dialogs = new Map(
    [...document.querySelectorAll("dialog.project-dialog")].map((d) => [d.id, d]),
  );
  if (!dialogs.size || typeof HTMLDialogElement !== "function") return;

  let opener = null;

  const open = (id, from) => {
    const dialog = dialogs.get(id);
    if (!dialog || dialog.open) return;
    opener = from || null;
    dialog.showModal();
    dialog.querySelector(".dialog-body").scrollTop = 0;
    document.documentElement.classList.add("dialog-open");
    if (location.hash !== `#${id}`) history.replaceState(null, "", `#${id}`);
  };

  dialogs.forEach((dialog) => {
    dialog.addEventListener("close", () => {
      document.documentElement.classList.remove("dialog-open");
      if (location.hash === `#${dialog.id}`) {
        history.replaceState(null, "", location.pathname + location.search);
      }
      if (opener) opener.focus({ preventScroll: true });
    });
    // 바깥(배경)을 누르면 닫기
    dialog.addEventListener("click", (e) => {
      if (e.target === dialog) dialog.close();
    });
    dialog.querySelectorAll("[data-close]").forEach((btn) => {
      btn.addEventListener("click", () => dialog.close());
    });
  });

  document.querySelectorAll("[data-open]").forEach((btn) => {
    btn.addEventListener("click", () => open(btn.dataset.open, btn));
  });

  document.querySelectorAll("[data-project]").forEach((card) => {
    card.classList.add("is-clickable");
    card.addEventListener("click", (e) => {
      if (e.target.closest("a, button")) return;
      if (window.getSelection && String(window.getSelection()).length) return;
      open(card.dataset.project, card.querySelector("[data-open]"));
    });
  });

  const fromHash = () => {
    const id = decodeURIComponent(location.hash.slice(1));
    if (dialogs.has(id)) open(id);
  };
  window.addEventListener("hashchange", fromHash);
  fromHash();
})();

// 4) 저작권 연도
document.querySelectorAll("[data-year]").forEach((el) => {
  el.textContent = String(new Date().getFullYear());
});
