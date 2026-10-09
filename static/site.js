const toggle=document.querySelector('.menu-toggle');const nav=document.querySelector('#navigation');
toggle?.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')==='true';toggle.setAttribute('aria-expanded',String(!open));nav.classList.toggle('open',!open);});
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&nav?.classList.contains('open')){toggle.setAttribute('aria-expanded','false');nav.classList.remove('open');toggle.focus();}});
