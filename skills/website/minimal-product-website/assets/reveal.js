/** Progressive enhancement. Call on the client; call the returned cleanup on unmount. */
// SPDX-License-Identifier: MIT; Copyright (c) 2026 Kail Tian. See ../LICENSE.
export function initReveals({ root = document } = {}) {
  const elements = [...root.querySelectorAll('.mpw-reveal')];
  const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
  let observer;
  const show = element => element.classList.remove('is-pending');
  const showAll = () => {
    observer?.disconnect();
    elements.forEach(show);
  };
  if (preference.matches || !('IntersectionObserver' in window)) {
    showAll();
    return () => {};
  }

  observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      show(entry.target);
      observer.unobserve(entry.target);
    }
  }, { threshold: 0.12 });

  for (const element of elements) {
    // Hero/visible content and the current focus are never concealed on init.
    if (element.getBoundingClientRect().top < window.innerHeight || element.contains(document.activeElement)) continue;
    element.classList.add('is-pending');
    observer.observe(element);
  }

  const onPreferenceChange = event => { if (event.matches) showAll(); };
  const onFocus = event => {
    // Reveal every nested ancestor immediately when keyboard focus reaches it.
    for (const element of elements) {
      if (!element.contains(event.target)) continue;
      element.classList.add('is-focus-revealed');
      show(element);
      observer.unobserve(element);
    }
  };
  preference.addEventListener('change', onPreferenceChange);
  root.addEventListener('focusin', onFocus);

  return () => {
    showAll();
    elements.forEach(element => element.classList.remove('is-focus-revealed'));
    preference.removeEventListener('change', onPreferenceChange);
    root.removeEventListener('focusin', onFocus);
  };
}
