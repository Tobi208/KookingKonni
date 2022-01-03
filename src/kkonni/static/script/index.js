/**
 * Handles dynamic filtering on the index page.
 */

/**
 * Display any recipe whose keywords contain any of the search words.
 * Should be expanded to sophisticated search syntax with "" - etc.
 */
const search_bar = document.getElementById("search")
const recipes = document.getElementsByClassName("recipe")
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
