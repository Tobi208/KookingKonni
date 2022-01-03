function round_two(x) {
    return Math.round(x * 100) / 100
}

const portions = document.getElementById('portions')
const amounts = document.getElementsByClassName('amount')
const default_portions = portions.value
const default_amounts = new Array(amounts.length)
for (let i = 0; i < amounts.length; i++) {
    default_amounts[i] = parseFloat(amounts[i].innerHTML)
}

function adjust_amounts() {
    const ratio = portions.value / default_portions
    for (let i = 0; i < amounts.length; i++) {
        amounts[i].innerHTML = round_two(default_amounts[i] * ratio).toString()
    }
}

portions.addEventListener('change', adjust_amounts)
portions.value = round_two(default_portions)
adjust_amounts()

const user_rating = document.querySelector('#comment-form #user-rating')
const post_stars = document.querySelector('#comment-form .stars')
post_stars.dataset.stars = user_rating.dataset.stars
post_stars.classList.add('post')

for (const post_star of post_stars.querySelectorAll('.star')) {
    post_star.addEventListener('click', () => rate_recipe(post_star.dataset.star))
}

const user_comment = document.querySelector('#user-comment')
const btn_cancel_comment = document.querySelector('#user-comment-cancel')
btn_cancel_comment.addEventListener('click', () => user_comment.value = '')
