const portions = document.getElementById("portions")
const amounts = document.getElementsByClassName("amount")

const default_portions = portions.value
const default_amounts = new Array(amounts.length)
for (let i = 0; i < amounts.length; i++) {
    default_amounts[i] = parseFloat(amounts[i].innerHTML)
}

function adjust_amounts() {
    const ratio = portions.value / default_portions
    for (let i = 0; i < amounts.length; i++) {
        amounts[i].innerHTML = (Math.round(default_amounts[i] * ratio * 100) / 100).toString()
    }
}

portions.addEventListener("change", adjust_amounts)
adjust_amounts()


const user_rating = document.querySelector('#comment-form #user-rating')
const stars = document.querySelector('#comment-form .stars')
stars.dataset.stars = user_rating.dataset.stars
stars.classList.add('post')
