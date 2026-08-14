/* ══════════════════════════════════════════════════════════════
   django-unfold-rtl — runtime RTL fixes for Unfold admin
   ──────────────────────────────────────────────────────────────
   Only fixes that CSS can't express (reading live layout width,
   mirroring inline styles Unfold sets from JS). Sections:
     1. Guard — bail unless the page is actually rendered RTL
     2. Bulk-actions bar offset (mirror inline `left` → `right`)
     3. Bulk-actions bar width (seed Alpine's changeListWidth)
     4. Dashboard caption alignment
   ══════════════════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", function () {
    // ── 1. Guard ──────────────────────────────────────────────
    // Only touch layout when the page is actually rendered RTL (fa/ar/he/...).
    if (document.documentElement.dir !== 'rtl') return;

    // ── 2. Bulk-actions bar offset ────────────────────────────
    // Unfold pins the bar with `right-0` plus an inline `left: <sidebarWidth>px`.
    // In RTL the sidebar sits on the right, so that offset is on the wrong edge
    // and the bar slides under it (Run button gets clipped off-screen). Mirror
    // the inline offset to `right` instead, and keep mirroring as Unfold updates it.
    const actionsBar = document.getElementById("changelist-actions-wrapper")?.parentElement;
    if (actionsBar) {
        const mirror = () => {
            const left = actionsBar.style.left;
            if (!left) return;
            actionsBar.style.left = "";
            actionsBar.style.right = left;
        };
        new MutationObserver(mirror).observe(actionsBar, {
            attributeFilter: ["style"],
        });
        mirror();
    }

    // ── 3. Bulk-actions bar width ─────────────────────────────
    // The bar sizes itself to the changelist via Alpine's
    // `x-resize="changeListWidth = $width"`. That ResizeObserver often reports 0
    // on first paint and never re-fires (results width doesn't change after
    // load), so the bar collapses and fails to cover the save button. Seed the
    // value from the real width once Alpine and layout are ready, then keep it
    // current with our own observer.
    const changelist = document.getElementById("changelist");
    const resizeEl = changelist?.querySelector("[x-resize]");
    if (changelist && resizeEl) {
        const syncChangeListWidth = () => {
            const width = Math.round(resizeEl.getBoundingClientRect().width);
            const data = window.Alpine && window.Alpine.$data(changelist);
            if (!data || !width) return false;
            if (data.changeListWidth !== width) data.changeListWidth = width;
            return true;
        };
        // Retry until Alpine has initialised and layout has a real width.
        let tries = 0;
        const tick = () => {
            if (syncChangeListWidth() || tries++ > 40) return;
            setTimeout(tick, 50);
        };
        tick();
        new ResizeObserver(syncChangeListWidth).observe(resizeEl);
    }

    // ── 4. Dashboard caption alignment ────────────────────────
    // On the dashboard (path /admin/, possibly with locale prefix or trailing
    // slash), flip caption tags from text-left to text-right for RTL.
    const path = window.location.pathname;
    if (path === '/admin/' || path.endsWith('/admin/')) {
        const captions = document.querySelectorAll('caption');
        captions.forEach(caption => {
            if (caption.classList.contains('text-left')) {
                caption.classList.remove('text-left');
                caption.classList.add('text-right');
                caption.classList.add('mr-2');
            }
        });
    }
});
