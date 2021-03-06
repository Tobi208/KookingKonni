/**
 * Handles the ubiquitous topnav display style.
 */

/**
 * Toggle display style of vertical topnav on small screens.
 */
const toggle = document.querySelector('.toggle')
const submits = document.querySelectorAll('.submit')
toggle.addEventListener('click', () => {
    for (const flex_break of flex_breaks) {
        if (window.getComputedStyle(flex_break, null).getPropertyValue('display') === 'none')
            flex_break.style.display = 'block'
        else
            flex_break.style.display = 'none'
    }
    for (const submit of submits) {
        if (window.getComputedStyle(submit, null).getPropertyValue('display') === 'none')
            submit.style.display = 'block'
        else
            submit.style.display = 'none'
    }
})

/**
 * Toggle display style back to big even if toggle button disappears.
 */
const flex_breaks = document.querySelectorAll('.flex-break')
window.addEventListener('resize', () => {
    if (window.innerWidth <= 920) {
        for (const flex_break of flex_breaks)
            flex_break.style.display = 'none'
        for (const submit of submits)
            submit.style.display = 'none'
    } else {
        for (const flex_break of flex_breaks)
            flex_break.style.display = 'none'
        for (const submit of submits)
            submit.style.display = 'block'
    }
})

/**
 * Go to index page with search words.
 */
const search_bar = document.querySelector('.topnav #search')
const index_url = search_bar.dataset.url
search_bar.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && window.location.pathname !== '/') {
        const values = search_bar.value
        if (values !== '') {
            window.location.href = `${index_url}?q=${values.replace(' ', '+')}`
        }
    }
})
