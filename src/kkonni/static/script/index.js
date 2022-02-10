/**
 * Handles dynamic filtering on the index page.
 */

/**
 * Display any recipe whose keywords contain any of the search words.
 * Should be expanded to sophisticated search syntax with "" - etc.
 */
const recipes = document.querySelectorAll('.recipe')
function filter_recipes() {
    // gather words from search input
    const words = search_bar.value.toLowerCase().trim().split(/\s+/)
    // reset display style on empty input
    if (words.length === 0) {
        for (const recipe of recipes) { recipe.style.display = 'block' }
    } else {
        // else only display viable recipes
        for (const recipe of recipes) {
            const keywords = recipe.dataset.keywords
            recipe.style.display = 'none'
            words.forEach(word => { if (keywords.includes(word)) { recipe.style.display = 'block' } })
        }
    }
}
// add listener and filter once in case of POST request
search_bar.addEventListener('input', filter_recipes)
filter_recipes()

const sort_criteria = ['name', 'rating', 'newest']
const search_sort = document.querySelector('.search-sort')
const recipes_ul = document.querySelector('#recipes')

let current_criterion = 0
let criterion, switching, should_switch, i, b
function sort_recipes() {
    current_criterion = (current_criterion + 1) % sort_criteria.length
    criterion = sort_criteria[current_criterion]

    switching = true
    while (switching) {
        switching = false
        b = recipes_ul.querySelectorAll('li.recipe')

        for (i = 0; i < (b.length - 1); i++) {
            should_switch = false
            if (criterion === 'name') {
                if (b[i].dataset.name > b[i + 1].dataset.name) {
                    should_switch = true
                    break
                }
            } else if (criterion === 'rating') {
                if (Number(b[i].dataset.rating) < Number(b[i + 1].dataset.rating)) {
                    should_switch = true
                    break
                }
            } else if (criterion === 'newest') {
                if (Number(b[i].dataset.time) < Number(b[i + 1].dataset.time)) {
                    should_switch = true
                    break
                }
            }
        }

        if (should_switch) {
            b[i].parentNode.insertBefore(b[i + 1], b[i]);
            switching = true;
        }
    }
}
search_sort.addEventListener('click', sort_recipes)
