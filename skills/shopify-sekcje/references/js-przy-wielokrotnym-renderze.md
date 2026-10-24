# Sekcja renderowana wielokrotnie: JS pod jednym globalnym guardem + registry

**Wdrożone:** sklep z pluszakami (2026-06, motyw na bazie Nook).

Gdy sekcja może wystąpić kilka razy na stronie i/lub theme editor ją przeładowuje, inline `<script>` wykonuje się raz na instancję → duplikaty globalnych listenerów (resize, `shopify:section:load`). Wzorzec: definicje klasy + globalne listenery raz, reszta to rejestracja instancji.

```js
(function () {
  'use strict';
  if (window.__myComp) { window.__myComp.boot('{{ section.id }}'); return; } // 2. instancja+ tylko bootuje

  var registry = {};
  function initWrapper(w){ if(!w || w._inited) return; w._inited=true; registry[w.dataset.sectionId]=new Comp(w); }

  var t; window.addEventListener('resize', function(){ clearTimeout(t); t=setTimeout(function(){
    Object.keys(registry).forEach(function(k){ registry[k].onResize(); }); }, 150); });   // jeden listener globalnie

  document.addEventListener('shopify:section:load', function(e){
    var w = e.target.querySelector('.my-wrapper'); if(w){ w._inited=false; initWrapper(w); } });

  window.__myComp = { boot: function(id){ initWrapper(document.getElementById('comp-' + id)); } };
  window.__myComp.boot('{{ section.id }}');   // 1. instancja: rejestruje globalne + bootuje siebie
})();
```

Guard `w._inited` na elemencie (nie globalny boolean), pozwala re-init konkretnego wrappera po section reload, nie blokując pozostałych.
