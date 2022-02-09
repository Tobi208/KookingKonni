const unseen = document.querySelectorAll('.notification.unseen')
unseen.forEach(n => n.addEventListener('mouseenter', () => n.classList.remove('unseen')))
