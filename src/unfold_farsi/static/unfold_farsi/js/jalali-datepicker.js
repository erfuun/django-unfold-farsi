/**
 * Self-contained Jalali Date & Time Picker for Behinab & Unfold Admin
 * Zero external dependencies. Self-contained scoped styling (.jdp-*) ensuring
 * 100% consistent rendering across both Django Unfold Admin and Behinab Dashboard.
 * Full RTL support, Dark/Light theme awareness, Persian calendar math, and compact HH:MM time picker.
 */
(function () {
  'use strict';

  // ── 1. Suppress Django's Default DateTimeShortcuts (Admin only) ─
  function suppressDjangoShortcuts() {
    if (window.DateTimeShortcuts) {
      window.DateTimeShortcuts.init = function () {};
      window.DateTimeShortcuts.openCalendar = function () {};
      window.DateTimeShortcuts.openClock = function () {};
    }
    try {
      Object.defineProperty(window, 'DateTimeShortcuts', {
        configurable: true,
        enumerable: true,
        get: function () {
          return this._dateTimeShortcuts;
        },
        set: function (val) {
          if (val && typeof val === 'object') {
            val.init = function () {};
            val.openCalendar = function () {};
            val.openClock = function () {};
          }
          this._dateTimeShortcuts = val;
        },
      });
    } catch (e) {
      // Ignore if already non-configurable
    }

    // Hide any rogue Django popups or shortcut spans
    const rogueShortcuts = document.querySelectorAll('.datetimeshortcuts');
    rogueShortcuts.forEach(el => el.style.display = 'none');
    const roguePopups = document.querySelectorAll('[id^="calendarbox"], [id^="clockbox"]');
    roguePopups.forEach(el => el.style.display = 'none');
  }

  suppressDjangoShortcuts();
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', suppressDjangoShortcuts);
  }

  // ── 2. Self-Contained Scoped Styles (.jdp-*) ───────────────────
  const styleEl = document.createElement('style');
  styleEl.id = 'jdp-styles';
  styleEl.textContent = `
    .jdp-popup {
      position: absolute;
      z-index: 99999;
      background: #ffffff;
      color: #1f2937;
      border: 1px solid #e5e7eb;
      border-radius: 1rem;
      padding: 1rem;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.08);
      font-family: inherit;
      font-size: 0.875rem;
      box-sizing: border-box;
      animation: jdp-pop 0.15s cubic-bezier(0.16, 1, 0.3, 1);
      user-select: none;
      direction: rtl;
    }
    :is([data-theme="behinab-dark"], .dark, [data-theme="dark"]) .jdp-popup {
      background: #111827;
      color: #f3f4f6;
      border-color: #374151;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
    }
    @keyframes jdp-pop {
      from { opacity: 0; transform: scale(0.96) translateY(-4px); }
      to { opacity: 1; transform: scale(1) translateY(0); }
    }
    .jdp-date-popup {
      width: 290px;
      min-width: 290px;
      max-width: 290px;
    }
    .jdp-time-popup {
      width: 240px;
      min-width: 240px;
      max-width: 240px;
    }
    .jdp-scroll {
      scrollbar-width: thin;
      scrollbar-color: rgba(156, 163, 175, 0.5) transparent;
    }
    .jdp-scroll::-webkit-scrollbar {
      width: 4px;
    }
    .jdp-scroll::-webkit-scrollbar-track {
      background: transparent;
    }
    .jdp-scroll::-webkit-scrollbar-thumb {
      background: rgba(156, 163, 175, 0.5);
      border-radius: 4px;
    }
    .jdp-btn {
      border: none;
      outline: none;
      background: transparent;
      cursor: pointer;
      border-radius: 0.5rem;
      transition: background 0.12s ease, color 0.12s ease;
      font-family: inherit;
      font-size: 0.75rem;
      padding: 0.25rem 0.5rem;
      color: inherit;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      box-sizing: border-box;
    }
    .jdp-btn:hover {
      background: #f3f4f6;
    }
    :is([data-theme="behinab-dark"], .dark, [data-theme="dark"]) .jdp-btn:hover {
      background: #1f2937;
    }
    .jdp-btn-primary {
      background-color: #059669 !important;
      color: #ffffff !important;
      font-weight: 700 !important;
      box-shadow: 0 2px 6px rgba(5, 150, 105, 0.35) !important;
    }
    .jdp-btn-primary:hover {
      background-color: #047857 !important;
      color: #ffffff !important;
    }
    .jdp-btn-today {
      border: 1px solid #059669 !important;
      color: #059669 !important;
      font-weight: 600 !important;
    }
    :is([data-theme="behinab-dark"], .dark, [data-theme="dark"]) .jdp-btn-today {
      border-color: #10b981 !important;
      color: #34d399 !important;
    }
    .jdp-btn-danger {
      color: #ef4444 !important;
    }
    .jdp-btn-danger:hover {
      background: rgba(239, 68, 68, 0.1) !important;
    }
    .jdp-badge {
      background: rgba(5, 150, 105, 0.1);
      border: 1px solid rgba(5, 150, 105, 0.25);
      color: #059669;
      font-weight: 700;
      font-size: 0.875rem;
      padding: 0.15rem 0.6rem;
      border-radius: 0.5rem;
      letter-spacing: 0.05em;
    }
    :is([data-theme="behinab-dark"], .dark, [data-theme="dark"]) .jdp-badge {
      background: rgba(5, 150, 105, 0.2);
      color: #34d399;
      border-color: rgba(5, 150, 105, 0.4);
    }
    /* Time Grid & Columns */
    .jdp-time-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.625rem;
      margin-top: 0.625rem;
    }
    .jdp-time-col {
      display: flex;
      flex-direction: column;
      min-width: 0;
    }
    .jdp-time-label {
      font-size: 0.75rem;
      font-weight: 600;
      color: #9ca3af;
      text-align: center;
      margin-bottom: 0.35rem;
    }
    .jdp-time-list {
      height: 160px !important;
      max-height: 160px !important;
      overflow-y: auto !important;
      overflow-x: hidden !important;
      padding-right: 0.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }
    .jdp-time-btn {
      width: 100%;
      height: 28px !important;
      min-height: 28px !important;
      font-size: 0.75rem;
      font-weight: 500;
      border-radius: 0.375rem;
      border: none;
      background: transparent;
      cursor: pointer;
      text-align: center;
      color: inherit;
      transition: background 0.1s, color 0.1s;
    }
    .jdp-time-btn:hover {
      background: #f3f4f6;
    }
    :is([data-theme="behinab-dark"], .dark, [data-theme="dark"]) .jdp-time-btn:hover {
      background: #1f2937;
    }
    /* Days Grid */
    .jdp-days-grid {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      gap: 0.25rem;
      text-align: center;
    }
    .jdp-day-cell {
      width: 2rem;
      height: 2rem;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 0.5rem;
      font-size: 0.75rem;
      font-weight: 500;
      border: none;
      background: transparent;
      cursor: pointer;
      color: inherit;
      transition: background 0.1s, color 0.1s;
    }
    .jdp-day-cell:hover {
      background: #f3f4f6;
    }
    :is([data-theme="behinab-dark"], .dark, [data-theme="dark"]) .jdp-day-cell:hover {
      background: #1f2937;
    }
    .jdp-friday {
      color: #ef4444;
    }
    :is([data-theme="behinab-dark"], .dark, [data-theme="dark"]) .jdp-friday {
      color: #f87171;
    }
    /* Months & Years Grid */
    .jdp-select-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 0.5rem;
      margin: 0.5rem 0;
    }
    .jdp-grid-btn {
      padding: 0.5rem 0.25rem;
      font-size: 0.75rem;
      font-weight: 600;
      border-radius: 0.5rem;
      border: 1px solid #e5e7eb;
      background: #f9fafb;
      color: #374151;
      cursor: pointer;
      text-align: center;
      transition: border 0.1s, color 0.1s, background 0.1s;
    }
    :is([data-theme="behinab-dark"], .dark, [data-theme="dark"]) .jdp-grid-btn {
      border-color: #374151;
      background: #1f2937;
      color: #e5e7eb;
    }
    .jdp-grid-btn:hover {
      border-color: #059669;
      color: #059669;
    }
    /* Hide lingering Django Admin shortcut popups */
    .datetimeshortcuts, [id^="calendarbox"], [id^="clockbox"] {
      display: none !important;
    }
  `;
  document.head.appendChild(styleEl);

  // ── 3. Persian & Jalali Math Utilities ─────────────────────────
  const PERSIAN_MONTHS = [
    'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
    'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
  ];

  const PERSIAN_WEEKDAYS = ['ش', 'ی', 'د', 'س', 'چ', 'پ', 'ج'];

  function toPersianDigits(str) {
    const p = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    return String(str).replace(/[0-9]/g, w => p[+w]);
  }

  function toAsciiDigits(str) {
    return String(str)
      .replace(/[۰-۹]/g, d => d.charCodeAt(0) - 1776)
      .replace(/[٠-٩]/g, d => d.charCodeAt(0) - 1632);
  }

  function jalaliToGregorian(jy, jm, jd) {
    let gy = (jy <= 979) ? 621 : 1600;
    jy -= (jy <= 979) ? 0 : 979;
    let days = (365 * jy) + Math.floor(jy / 33) * 8 + Math.floor(((jy % 33) + 3) / 4) + 78 + jd + ((jm < 7) ? (jm - 1) * 31 : ((jm - 7) * 30) + 186);
    gy += 400 * Math.floor(days / 146097);
    days %= 146097;
    if (days > 36524) {
      gy += 100 * Math.floor(--days / 36524);
      days %= 36524;
      if (days >= 365) days++;
    }
    gy += 4 * Math.floor(days / 1461);
    days %= 1461;
    if (days > 365) {
      gy += Math.floor((days - 1) / 365);
      days = (days - 1) % 365;
    }
    let gd = days + 1;
    const sal_a = [0, 31, ((gy % 4 === 0 && gy % 100 !== 0) || (gy % 400 === 0)) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    let gm;
    for (gm = 0; gm < 13 && gd > sal_a[gm]; gm++) gd -= sal_a[gm];
    return [gy, gm, gd];
  }

  function gregorianToJalali(gy, gm, gd) {
    const g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
    let gy2 = (gm > 2) ? (gy + 1) : gy;
    let days = 355666 + (365 * gy) + Math.floor((gy2 + 3) / 4) - Math.floor((gy2 + 99) / 100) + Math.floor((gy2 + 399) / 400) + gd + g_d_m[gm - 1];
    let jy = -1595 + (33 * Math.floor(days / 12053));
    days %= 12053;
    jy += 4 * Math.floor(days / 1461);
    days %= 1461;
    if (days > 365) {
      jy += Math.floor((days - 1) / 365);
      days = (days - 1) % 365;
    }
    let jm = (days < 186) ? 1 + Math.floor(days / 31) : 7 + Math.floor((days - 186) / 30);
    let jd = 1 + ((days < 186) ? (days % 31) : ((days - 186) % 30));
    return [jy, jm, jd];
  }

  function isJalaliLeapYear(jy) {
    const [gy, gm, gd] = jalaliToGregorian(jy, 12, 30);
    const [jy2, jm2, jd2] = gregorianToJalali(gy, gm, gd);
    return jd2 === 30;
  }

  function getDaysInMonth(jy, jm) {
    if (jm <= 6) return 31;
    if (jm <= 11) return 30;
    return isJalaliLeapYear(jy) ? 30 : 29;
  }

  function getFirstWeekdayOfMonth(jy, jm) {
    const [gy, gm, gd] = jalaliToGregorian(jy, jm, 1);
    const gDay = new Date(gy, gm - 1, gd).getDay();
    // In JS: 0=Sun, 1=Mon, ..., 6=Sat.
    // In Jalali: 0=Sat, 1=Sun, ..., 6=Fri.
    return (gDay + 1) % 7;
  }

  function getTodayJalali() {
    const now = new Date();
    return gregorianToJalali(now.getFullYear(), now.getMonth() + 1, now.getDate());
  }

  function getYesterdayJalali() {
    const d = new Date();
    d.setDate(d.getDate() - 1);
    return gregorianToJalali(d.getFullYear(), d.getMonth() + 1, d.getDate());
  }

  function parseInputDate(val) {
    if (!val) return null;
    const clean = toAsciiDigits(val).replace(/[-.]/g, '/').trim();
    const parts = clean.split('/');
    if (parts.length === 3) {
      const y = parseInt(parts[0], 10);
      const m = parseInt(parts[1], 10);
      const d = parseInt(parts[2], 10);
      if (y > 1200 && y < 1600 && m >= 1 && m <= 12 && d >= 1 && d <= 31) {
        return [y, m, d];
      }
      if (y >= 1600 && m >= 1 && m <= 12 && d >= 1 && d <= 31) {
        return gregorianToJalali(y, m, d);
      }
    }
    return null;
  }

  function parseInputTime(val) {
    if (!val) return null;
    const clean = toAsciiDigits(val).trim();
    const parts = clean.split(':');
    if (parts.length >= 2) {
      const h = parseInt(parts[0], 10);
      const m = parseInt(parts[1], 10);
      if (!isNaN(h) && !isNaN(m) && h >= 0 && h <= 23 && m >= 0 && m <= 59) {
        return [h, m];
      }
    }
    return null;
  }

  // ── 4. Position Helper ─────────────────────────────────────────
  function positionPopup(input, container) {
    if (!container || !input) return;
    const rect = input.getBoundingClientRect();
    const scrollY = window.scrollY || window.pageYOffset;
    const scrollX = window.scrollX || window.pageXOffset;
    const popupWidth = container.offsetWidth || 280;
    const popupHeight = container.offsetHeight || 320;

    const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
    const viewportWidth = window.innerWidth || document.documentElement.clientWidth;

    const spaceBelow = viewportHeight - rect.bottom;
    const spaceAbove = rect.top;
    let top;
    if (spaceBelow >= popupHeight + 10 || spaceBelow >= spaceAbove) {
      top = rect.bottom + scrollY + 6;
    } else {
      top = rect.top + scrollY - popupHeight - 6;
    }

    const isRtl = document.dir === 'rtl' ||
                  document.documentElement.getAttribute('dir') === 'rtl' ||
                  (window.getComputedStyle && window.getComputedStyle(document.body).direction === 'rtl');

    let left;
    if (isRtl) {
      left = rect.right + scrollX - popupWidth;
    } else {
      left = rect.left + scrollX;
    }

    const maxLeft = viewportWidth + scrollX - popupWidth - 12;
    const minLeft = scrollX + 12;
    left = Math.max(minLeft, Math.min(left, maxLeft));

    container.style.position = 'absolute';
    container.style.top = `${Math.round(top)}px`;
    container.style.left = `${Math.round(left)}px`;
    container.style.zIndex = '99999';
  }

  // ── 5. JalaliDatePicker Component ──────────────────────────────
  class JalaliDatePicker {
    constructor(input) {
      this.input = input;
      this.container = null;
      this.isOpen = false;
      this.viewMode = 'days';

      const today = getTodayJalali();
      const initial = parseInputDate(this.input.value) || today;
      this.viewYear = initial[0];
      this.viewMonth = initial[1];
      this.selectedDate = parseInputDate(this.input.value);

      this.init();
    }

    init() {
      if (this.input.type === 'date') {
        this.input.type = 'text';
      }
      this.input.setAttribute('autocomplete', 'off');
      this.input.setAttribute('dir', 'ltr');

      this.input.addEventListener('focus', () => this.open());
      this.input.addEventListener('click', (e) => {
        e.stopPropagation();
        this.open();
      });

      this.findAndBindToggle();

      document.addEventListener('click', (e) => {
        if (
          this.isOpen &&
          this.container &&
          !this.container.contains(e.target) &&
          e.target !== this.input &&
          !(this.toggleBtn && this.toggleBtn.contains(e.target))
        ) {
          this.close();
        }
      });

      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.isOpen) {
          this.close();
        }
      });

      window.addEventListener('resize', () => {
        if (this.isOpen) positionPopup(this.input, this.container);
      });
    }

    findAndBindToggle() {
      const parent = this.input.parentElement;
      if (!parent) return;

      let toggle = parent.querySelector('[data-datepicker-toggle]');
      if (!toggle) {
        const shortcutLink = parent.querySelector('.date-icon, #calendarlink0');
        if (shortcutLink) {
          toggle = shortcutLink.closest('a') || shortcutLink;
        }
      }

      if (toggle) {
        this.toggleBtn = toggle;
        toggle.addEventListener('click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          if (this.isOpen) {
            this.close();
          } else {
            this.open();
          }
        });
      }
    }

    open() {
      if (this.isOpen) return;
      if (window._activeJalaliPicker && window._activeJalaliPicker !== this) {
        window._activeJalaliPicker.close();
      }
      window._activeJalaliPicker = this;

      const current = parseInputDate(this.input.value);
      if (current) {
        this.viewYear = current[0];
        this.viewMonth = current[1];
        this.selectedDate = current;
      }
      this.viewMode = 'days';
      this.yearPageStart = Math.floor(this.viewYear / 12) * 12;

      this.render();
      positionPopup(this.input, this.container);
      this.isOpen = true;
    }

    close() {
      if (!this.isOpen) return;
      if (this.container && this.container.parentNode) {
        this.container.parentNode.removeChild(this.container);
      }
      this.container = null;
      this.isOpen = false;
      this.viewMode = 'days';
      if (window._activeJalaliPicker === this) {
        window._activeJalaliPicker = null;
      }
    }

    render() {
      if (!this.container) {
        this.container = document.createElement('div');
        this.container.className = 'jdp-popup jdp-date-popup';
        document.body.appendChild(this.container);
      }

      this.container.innerHTML = '';

      if (this.viewMode === 'days') {
        this.renderCalendarDays(this.container);
      } else if (this.viewMode === 'months') {
        this.renderMonthSelector(this.container);
      } else if (this.viewMode === 'years') {
        this.renderYearSelector(this.container);
      }
    }

    renderCalendarDays(el) {
      // Header
      const header = document.createElement('div');
      header.style.display = 'flex';
      header.style.alignItems = 'center';
      header.style.justifyContent = 'space-between';
      header.style.marginBottom = '0.75rem';

      const prevBtn = document.createElement('button');
      prevBtn.type = 'button';
      prevBtn.className = 'jdp-btn';
      prevBtn.title = 'ماه قبل';
      prevBtn.innerHTML = '<svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>';
      prevBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.prevMonth();
      });

      const titleWrap = document.createElement('div');
      titleWrap.style.display = 'flex';
      titleWrap.style.alignItems = 'center';
      titleWrap.style.gap = '0.35rem';

      const monthBtn = document.createElement('button');
      monthBtn.type = 'button';
      monthBtn.className = 'jdp-btn';
      monthBtn.style.fontWeight = '700';
      monthBtn.style.fontSize = '0.875rem';
      monthBtn.textContent = PERSIAN_MONTHS[this.viewMonth - 1];
      monthBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.viewMode = 'months';
        this.render();
      });

      const yearBtn = document.createElement('button');
      yearBtn.type = 'button';
      yearBtn.className = 'jdp-btn';
      yearBtn.style.fontWeight = '700';
      yearBtn.style.fontSize = '0.875rem';
      yearBtn.textContent = toPersianDigits(this.viewYear);
      yearBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.yearPageStart = Math.floor(this.viewYear / 12) * 12;
        this.viewMode = 'years';
        this.render();
      });

      titleWrap.appendChild(monthBtn);
      titleWrap.appendChild(yearBtn);

      const nextBtn = document.createElement('button');
      nextBtn.type = 'button';
      nextBtn.className = 'jdp-btn';
      nextBtn.title = 'ماه بعد';
      nextBtn.innerHTML = '<svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>';
      nextBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.nextMonth();
      });

      header.appendChild(prevBtn);
      header.appendChild(titleWrap);
      header.appendChild(nextBtn);
      el.appendChild(header);

      // Weekdays
      const weekdaysGrid = document.createElement('div');
      weekdaysGrid.className = 'jdp-days-grid';
      weekdaysGrid.style.marginBottom = '0.25rem';
      PERSIAN_WEEKDAYS.forEach((w, idx) => {
        const span = document.createElement('span');
        span.style.fontSize = '0.75rem';
        span.style.fontWeight = '600';
        span.style.color = idx === 6 ? '#ef4444' : '#9ca3af';
        span.style.padding = '0.2rem 0';
        span.textContent = w;
        weekdaysGrid.appendChild(span);
      });
      el.appendChild(weekdaysGrid);

      // Days Grid
      const daysGrid = document.createElement('div');
      daysGrid.className = 'jdp-days-grid';

      const firstWeekday = getFirstWeekdayOfMonth(this.viewYear, this.viewMonth);
      const daysInMonth = getDaysInMonth(this.viewYear, this.viewMonth);
      const today = getTodayJalali();

      for (let i = 0; i < firstWeekday; i++) {
        const empty = document.createElement('div');
        empty.style.width = '2rem';
        empty.style.height = '2rem';
        daysGrid.appendChild(empty);
      }

      for (let d = 1; d <= daysInMonth; d++) {
        const btn = document.createElement('button');
        btn.type = 'button';
        const isToday = today[0] === this.viewYear && today[1] === this.viewMonth && today[2] === d;
        const isSelected = this.selectedDate &&
          this.selectedDate[0] === this.viewYear &&
          this.selectedDate[1] === this.viewMonth &&
          this.selectedDate[2] === d;
        const isFriday = (firstWeekday + d - 1) % 7 === 6;

        let cls = 'jdp-day-cell ';
        if (isSelected) {
          cls += 'jdp-btn-primary ';
        } else if (isToday) {
          cls += 'jdp-btn-today ';
        } else if (isFriday) {
          cls += 'jdp-friday ';
        }

        btn.className = cls;
        btn.textContent = toPersianDigits(d);
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          this.selectDate(this.viewYear, this.viewMonth, d);
        });
        daysGrid.appendChild(btn);
      }
      el.appendChild(daysGrid);

      // Footer Action Bar
      const footer = document.createElement('div');
      footer.style.display = 'flex';
      footer.style.alignItems = 'center';
      footer.style.justifyContent = 'space-between';
      footer.style.paddingTop = '0.625rem';
      footer.style.marginTop = '0.625rem';
      footer.style.borderTop = '1px solid #e5e7eb';

      const leftActions = document.createElement('div');
      leftActions.style.display = 'flex';
      leftActions.style.alignItems = 'center';
      leftActions.style.gap = '0.25rem';

      const todayBtn = document.createElement('button');
      todayBtn.type = 'button';
      todayBtn.className = 'jdp-btn';
      todayBtn.style.color = '#059669';
      todayBtn.style.fontWeight = '600';
      todayBtn.textContent = 'امروز';
      todayBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const [ty, tm, td] = getTodayJalali();
        this.selectDate(ty, tm, td);
      });

      const yestBtn = document.createElement('button');
      yestBtn.type = 'button';
      yestBtn.className = 'jdp-btn';
      yestBtn.style.color = '#6b7280';
      yestBtn.textContent = 'دیروز';
      yestBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const [yy, ym, yd] = getYesterdayJalali();
        this.selectDate(yy, ym, yd);
      });

      const clearBtn = document.createElement('button');
      clearBtn.type = 'button';
      clearBtn.className = 'jdp-btn jdp-btn-danger';
      clearBtn.textContent = 'پاک کردن';
      clearBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.input.value = '';
        this.selectedDate = null;
        this.input.dispatchEvent(new Event('input', { bubbles: true }));
        this.input.dispatchEvent(new Event('change', { bubbles: true }));
        this.close();
      });

      leftActions.appendChild(todayBtn);
      leftActions.appendChild(yestBtn);
      leftActions.appendChild(clearBtn);

      const closeBtn = document.createElement('button');
      closeBtn.type = 'button';
      closeBtn.className = 'jdp-btn';
      closeBtn.style.color = '#9ca3af';
      closeBtn.textContent = 'بستن';
      closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.close();
      });

      footer.appendChild(leftActions);
      footer.appendChild(closeBtn);
      el.appendChild(footer);
    }

    renderMonthSelector(el) {
      const header = document.createElement('div');
      header.style.display = 'flex';
      header.style.alignItems = 'center';
      header.style.justifyContent = 'space-between';
      header.style.marginBottom = '0.625rem';

      const title = document.createElement('span');
      title.style.fontWeight = '700';
      title.style.fontSize = '0.875rem';
      title.textContent = `انتخاب ماه (${toPersianDigits(this.viewYear)})`;

      const backBtn = document.createElement('button');
      backBtn.type = 'button';
      backBtn.className = 'jdp-btn';
      backBtn.textContent = 'بازگشت';
      backBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.viewMode = 'days';
        this.render();
      });

      header.appendChild(title);
      header.appendChild(backBtn);
      el.appendChild(header);

      const grid = document.createElement('div');
      grid.className = 'jdp-select-grid';

      PERSIAN_MONTHS.forEach((mName, idx) => {
        const mNum = idx + 1;
        const btn = document.createElement('button');
        btn.type = 'button';
        const isSelected = mNum === this.viewMonth;

        btn.className = isSelected ? 'jdp-grid-btn jdp-btn-primary' : 'jdp-grid-btn';
        btn.textContent = mName;
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          this.viewMonth = mNum;
          this.viewMode = 'days';
          this.render();
        });
        grid.appendChild(btn);
      });

      el.appendChild(grid);
    }

    renderYearSelector(el) {
      const header = document.createElement('div');
      header.style.display = 'flex';
      header.style.alignItems = 'center';
      header.style.justifyContent = 'space-between';
      header.style.marginBottom = '0.625rem';

      const prevPage = document.createElement('button');
      prevPage.type = 'button';
      prevPage.className = 'jdp-btn';
      prevPage.innerHTML = '<svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>';
      prevPage.addEventListener('click', (e) => {
        e.stopPropagation();
        this.yearPageStart -= 12;
        this.render();
      });

      const title = document.createElement('span');
      title.style.fontWeight = '700';
      title.style.fontSize = '0.875rem';
      title.textContent = `${toPersianDigits(this.yearPageStart)} - ${toPersianDigits(this.yearPageStart + 11)}`;

      const nextPage = document.createElement('button');
      nextPage.type = 'button';
      nextPage.className = 'jdp-btn';
      nextPage.innerHTML = '<svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>';
      nextPage.addEventListener('click', (e) => {
        e.stopPropagation();
        this.yearPageStart += 12;
        this.render();
      });

      header.appendChild(prevPage);
      header.appendChild(title);
      header.appendChild(nextPage);
      el.appendChild(header);

      const grid = document.createElement('div');
      grid.className = 'jdp-select-grid';

      for (let y = this.yearPageStart; y < this.yearPageStart + 12; y++) {
        const btn = document.createElement('button');
        btn.type = 'button';
        const isSelected = y === this.viewYear;

        btn.className = isSelected ? 'jdp-grid-btn jdp-btn-primary' : 'jdp-grid-btn';
        btn.textContent = toPersianDigits(y);
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          this.viewYear = y;
          this.viewMode = 'days';
          this.render();
        });
        grid.appendChild(btn);
      }

      el.appendChild(grid);

      const footer = document.createElement('div');
      footer.style.textAlign = 'center';
      footer.style.marginTop = '0.5rem';
      const backBtn = document.createElement('button');
      backBtn.type = 'button';
      backBtn.className = 'jdp-btn';
      backBtn.textContent = 'بازگشت به تقویم';
      backBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.viewMode = 'days';
        this.render();
      });
      footer.appendChild(backBtn);
      el.appendChild(footer);
    }

    prevMonth() {
      if (this.viewMonth === 1) {
        this.viewMonth = 12;
        this.viewYear--;
      } else {
        this.viewMonth--;
      }
      this.render();
    }

    nextMonth() {
      if (this.viewMonth === 12) {
        this.viewMonth = 1;
        this.viewYear++;
      } else {
        this.viewMonth++;
      }
      this.render();
    }

    selectDate(y, m, d) {
      const mm = String(m).padStart(2, '0');
      const dd = String(d).padStart(2, '0');
      this.input.value = `${y}/${mm}/${dd}`;
      this.selectedDate = [y, m, d];
      this.input.dispatchEvent(new Event('input', { bubbles: true }));
      this.input.dispatchEvent(new Event('change', { bubbles: true }));
      this.close();
    }
  }

  // ── 6. JalaliTimePicker Component (Compact & Scoped) ───────────
  class JalaliTimePicker {
    constructor(input) {
      this.input = input;
      this.container = null;
      this.isOpen = false;

      const now = new Date();
      const parsed = parseInputTime(this.input.value);
      this.selectedHour = parsed ? parsed[0] : now.getHours();
      this.selectedMinute = parsed ? parsed[1] : now.getMinutes();

      this.init();
    }

    init() {
      if (this.input.type === 'time') {
        this.input.type = 'text';
      }
      this.input.setAttribute('autocomplete', 'off');
      this.input.setAttribute('dir', 'ltr');

      this.input.addEventListener('focus', () => this.open());
      this.input.addEventListener('click', (e) => {
        e.stopPropagation();
        this.open();
      });

      this.findAndBindToggle();

      document.addEventListener('click', (e) => {
        if (
          this.isOpen &&
          this.container &&
          !this.container.contains(e.target) &&
          e.target !== this.input &&
          !(this.toggleBtn && this.toggleBtn.contains(e.target))
        ) {
          this.close();
        }
      });

      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.isOpen) {
          this.close();
        }
      });

      window.addEventListener('resize', () => {
        if (this.isOpen) positionPopup(this.input, this.container);
      });
    }

    findAndBindToggle() {
      const parent = this.input.parentElement;
      if (!parent) return;

      let toggle = parent.querySelector('[data-timepicker-toggle]');
      if (!toggle) {
        const shortcutLink = parent.querySelector('.clock-icon, #clocklink0');
        if (shortcutLink) {
          toggle = shortcutLink.closest('a') || shortcutLink;
        }
      }

      if (toggle) {
        this.toggleBtn = toggle;
        toggle.addEventListener('click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          if (this.isOpen) {
            this.close();
          } else {
            this.open();
          }
        });
      }
    }

    open() {
      if (this.isOpen) return;
      if (window._activeJalaliPicker && window._activeJalaliPicker !== this) {
        window._activeJalaliPicker.close();
      }
      window._activeJalaliPicker = this;

      const parsed = parseInputTime(this.input.value);
      if (parsed) {
        this.selectedHour = parsed[0];
        this.selectedMinute = parsed[1];
      } else {
        const now = new Date();
        this.selectedHour = now.getHours();
        this.selectedMinute = now.getMinutes();
      }

      this.render();
      positionPopup(this.input, this.container);
      this.isOpen = true;

      setTimeout(() => this.scrollToActive(), 20);
    }

    close() {
      if (!this.isOpen) return;
      if (this.container && this.container.parentNode) {
        this.container.parentNode.removeChild(this.container);
      }
      this.container = null;
      this.isOpen = false;
      if (window._activeJalaliPicker === this) {
        window._activeJalaliPicker = null;
      }
    }

    scrollToActive() {
      if (!this.container) return;
      const activeH = this.container.querySelector('[data-hour-active]');
      const activeM = this.container.querySelector('[data-minute-active]');
      if (activeH) activeH.scrollIntoView({ block: 'center' });
      if (activeM) activeM.scrollIntoView({ block: 'center' });
    }

    render() {
      if (!this.container) {
        this.container = document.createElement('div');
        this.container.className = 'jdp-popup jdp-time-popup';
        document.body.appendChild(this.container);
      }

      this.container.innerHTML = '';

      // Header Preview
      const header = document.createElement('div');
      header.style.display = 'flex';
      header.style.alignItems = 'center';
      header.style.justifyContent = 'space-between';
      header.style.paddingBottom = '0.5rem';
      header.style.borderBottom = '1px solid #e5e7eb';

      const title = document.createElement('span');
      title.style.fontSize = '0.75rem';
      title.style.fontWeight = '700';
      title.style.color = '#6b7280';
      title.textContent = 'انتخاب زمان';

      const badge = document.createElement('div');
      badge.className = 'jdp-badge';
      badge.textContent = `${toPersianDigits(String(this.selectedHour).padStart(2, '0'))} : ${toPersianDigits(String(this.selectedMinute).padStart(2, '0'))}`;
      this.badge = badge;

      header.appendChild(title);
      header.appendChild(badge);
      this.container.appendChild(header);

      // Grid for Hours & Minutes
      const grid = document.createElement('div');
      grid.className = 'jdp-time-grid';

      // Hours Column
      const hourCol = document.createElement('div');
      hourCol.className = 'jdp-time-col';

      const hourLabel = document.createElement('div');
      hourLabel.className = 'jdp-time-label';
      hourLabel.textContent = 'ساعت';
      hourCol.appendChild(hourLabel);

      const hourList = document.createElement('div');
      hourList.className = 'jdp-time-list jdp-scroll';
      for (let h = 0; h < 24; h++) {
        const btn = document.createElement('button');
        btn.type = 'button';
        const isSelected = h === this.selectedHour;
        btn.className = isSelected ? 'jdp-time-btn jdp-btn-primary' : 'jdp-time-btn';
        if (isSelected) btn.setAttribute('data-hour-active', 'true');
        btn.textContent = toPersianDigits(String(h).padStart(2, '0'));
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          this.selectedHour = h;
          this.render();
          this.scrollToActive();
        });
        hourList.appendChild(btn);
      }
      hourCol.appendChild(hourList);

      // Minutes Column
      const minCol = document.createElement('div');
      minCol.className = 'jdp-time-col';

      const minLabel = document.createElement('div');
      minLabel.className = 'jdp-time-label';
      minLabel.textContent = 'دقیقه';
      minCol.appendChild(minLabel);

      const minList = document.createElement('div');
      minList.className = 'jdp-time-list jdp-scroll';
      for (let m = 0; m < 60; m++) {
        const btn = document.createElement('button');
        btn.type = 'button';
        const isSelected = m === this.selectedMinute;
        btn.className = isSelected ? 'jdp-time-btn jdp-btn-primary' : 'jdp-time-btn';
        if (isSelected) btn.setAttribute('data-minute-active', 'true');
        btn.textContent = toPersianDigits(String(m).padStart(2, '0'));
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          this.selectedMinute = m;
          this.render();
          this.scrollToActive();
        });
        minList.appendChild(btn);
      }
      minCol.appendChild(minList);

      grid.appendChild(hourCol);
      grid.appendChild(minCol);
      this.container.appendChild(grid);

      // Action Bar
      const footer = document.createElement('div');
      footer.style.display = 'flex';
      footer.style.alignItems = 'center';
      footer.style.justifyContent = 'space-between';
      footer.style.paddingTop = '0.625rem';
      footer.style.marginTop = '0.625rem';
      footer.style.borderTop = '1px solid #e5e7eb';

      const leftActions = document.createElement('div');
      leftActions.style.display = 'flex';
      leftActions.style.alignItems = 'center';
      leftActions.style.gap = '0.25rem';

      const nowBtn = document.createElement('button');
      nowBtn.type = 'button';
      nowBtn.className = 'jdp-btn';
      nowBtn.style.color = '#059669';
      nowBtn.style.fontWeight = '600';
      nowBtn.textContent = 'اکنون';
      nowBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const d = new Date();
        this.applyTime(d.getHours(), d.getMinutes());
      });

      const clearBtn = document.createElement('button');
      clearBtn.type = 'button';
      clearBtn.className = 'jdp-btn jdp-btn-danger';
      clearBtn.textContent = 'پاک کردن';
      clearBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.input.value = '';
        this.input.dispatchEvent(new Event('input', { bubbles: true }));
        this.input.dispatchEvent(new Event('change', { bubbles: true }));
        this.close();
      });

      leftActions.appendChild(nowBtn);
      leftActions.appendChild(clearBtn);

      const applyBtn = document.createElement('button');
      applyBtn.type = 'button';
      applyBtn.className = 'jdp-btn jdp-btn-primary';
      applyBtn.style.padding = '0.35rem 0.85rem';
      applyBtn.textContent = 'تایید';
      applyBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.applyTime(this.selectedHour, this.selectedMinute);
      });

      footer.appendChild(leftActions);
      footer.appendChild(applyBtn);
      this.container.appendChild(footer);
    }

    applyTime(h, m) {
      const hh = String(h).padStart(2, '0');
      const mm = String(m).padStart(2, '0');
      this.input.value = `${hh}:${mm}`;
      this.input.dispatchEvent(new Event('input', { bubbles: true }));
      this.input.dispatchEvent(new Event('change', { bubbles: true }));
      this.close();
    }
  }

  // ── 7. Safe Auto-Initialization ────────────────────────────────
  function initDatePickers(root = document) {
    suppressDjangoShortcuts();

    const dateInputs = root.querySelectorAll('[data-jalali-datepicker], input.jalali-datepicker, input.vDateField');
    dateInputs.forEach(input => {
      if (!input._jalaliPicker) {
        input._jalaliPicker = new JalaliDatePicker(input);
      }
    });

    const timeInputs = root.querySelectorAll('[data-jalali-timepicker], input.jalali-timepicker, input.vTimeField');
    timeInputs.forEach(input => {
      if (!input._jalaliTimePicker) {
        input._jalaliTimePicker = new JalaliTimePicker(input);
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => initDatePickers());
  } else {
    initDatePickers();
  }

  document.addEventListener('htmx:afterSwap', (e) => {
    initDatePickers(e.detail.target);
  });

  window.initJalaliDatePickers = initDatePickers;
  window.JalaliDatePicker = JalaliDatePicker;
  window.JalaliTimePicker = JalaliTimePicker;
})();
