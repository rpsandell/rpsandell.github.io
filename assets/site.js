/* Mobile menu toggle. Wix's own handler lived in the stripped bundle;
   #MENU_AS_CONTAINER is shown/hidden purely by the data-undisplayed attribute
   (its rule is [data-undisplayed=true]{display:none} in Wix's inline CSS). */
(function () {
  var toggle = document.getElementById('MENU_AS_CONTAINER_TOGGLE');
  var panel  = document.getElementById('MENU_AS_CONTAINER');
  if (!toggle || !panel) return;

  function setOpen(open) {
    if (open) panel.removeAttribute('data-undisplayed');
    else panel.setAttribute('data-undisplayed', 'true');
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  setOpen(false);

  toggle.addEventListener('click', function (e) {
    e.preventDefault();
    setOpen(panel.getAttribute('data-undisplayed') === 'true');
  });
  toggle.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle.click(); }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') setOpen(false);
  });
  panel.addEventListener('click', function (e) {
    if (e.target.closest('a')) setOpen(false);
  });
})();
