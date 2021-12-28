const search_bar = document.getElementById("search")
const recipes = document.getElementsByClassName("recipe")

function filter_recipes() {
    const words = search_bar.value.toLowerCase().trim().split(/\s+/)
    if (words.length === 0) {
        for (const recipe of recipes) { recipe.style.display = "block" }
    } else {
        for (const recipe of recipes) {
            const keywords = recipe.dataset.keywords
            recipe.style.display = "none"
            words.forEach(word => { if (keywords.includes(word)) { recipe.style.display = "block" } })
        }
    }
}

search_bar.addEventListener("input", filter_recipes)
filter_recipes()
