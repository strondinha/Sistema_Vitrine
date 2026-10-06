/* Melhorias progressivas: os formulários e as buscas funcionam sem JavaScript. */
'use strict';
const menu = document.querySelector('.menu-toggle');
menu?.addEventListener('click', () => {
  const open = menu.getAttribute('aria-expanded') !== 'true';
  menu.setAttribute('aria-expanded', String(open));
  document.querySelector('#main-nav')?.classList.toggle('is-open', open);
});

document.querySelectorAll('form[data-confirm]').forEach(form => {
  form.addEventListener('submit', event => {
    if (!window.confirm(form.dataset.confirm)) event.preventDefault();
  });
});

document.querySelectorAll('textarea[data-count]').forEach(input => {
  const counter = document.querySelector(`[data-counter-for="${input.id}"]`);
  const update = () => { if (counter) counter.textContent = `${input.value.length}/${input.maxLength}`; };
  input.addEventListener('input', update);
  update();
});

const fileInput = document.querySelector('#images');
const preview = document.querySelector('#image-preview');
let previewUrls = [];
fileInput?.addEventListener('change', () => {
  previewUrls.forEach(url => URL.revokeObjectURL(url));
  previewUrls = [];
  preview.replaceChildren();
  const files = Array.from(fileInput.files);
  if (files.length > 6 || files.some(file => file.size > 5 * 1024 * 1024)) {
    const note = document.createElement('p');
    note.className = 'field-help';
    note.textContent = 'Escolha até 6 imagens de no máximo 5 MB cada. Confira também quantas imagens já existem no projeto.';
    preview.append(note);
  }
  files.slice(0, 6).forEach(file => {
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) return;
    const figure = document.createElement('figure');
    const img = document.createElement('img');
    const caption = document.createElement('figcaption');
    const url = URL.createObjectURL(file);
    previewUrls.push(url);
    img.src = url;
    img.alt = `Prévia de ${file.name}`;
    caption.textContent = file.name;
    figure.append(img, caption);
    preview.append(figure);
  });
});

document.querySelectorAll('[data-gallery-src]').forEach(button => {
  button.addEventListener('click', () => {
    const image = document.querySelector('#main-project-image');
    image.src = button.dataset.gallerySrc;
    image.alt = button.dataset.galleryAlt;
    document.querySelector('#image-caption').textContent = button.dataset.galleryCaption;
    document.querySelectorAll('[data-gallery-src]').forEach(item => {
      item.classList.toggle('active', item === button);
      item.setAttribute('aria-pressed', String(item === button));
    });
  });
});

document.querySelector('[data-copy-link]')?.addEventListener('click', async () => {
  const status = document.querySelector('.copy-status');
  try {
    await navigator.clipboard.writeText(window.location.href);
    status.textContent = 'Link copiado!';
  } catch {
    status.textContent = 'Copie o endereço na barra do navegador para compartilhar.';
  }
});

document.querySelector('[data-errors]')?.focus();
