// https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
async function post_request(url = '', data = {}) {
    const response = await fetch(url, {
        method: 'POST',
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json'
        },
        redirect: 'follow',
        referrerPolicy: 'no-referrer',
        body: JSON.stringify(data)
    });
    return response.json();
}

function delete_comment(cid) {
    const comment = document.querySelector(`#comment-${cid}`)
    post_request(`/api/delete/c/${cid}`, {'cid': cid})
        .then(() => comment.remove())
        .catch(err => console.log(err))
}

function add_comment(rid) {
    const user_comment = document.querySelector('#user-comment')
    if (user_comment.value === '') return
    post_request(`/api/add/c/${rid}`, {'comment': user_comment.value})
        .then(data => {
            const comment = document.createElement('div')
            comment.classList.add('comment')
            comment.id = `comment-${data['cid']}`
            comment.innerHTML =
                `<div class="modify">
                    <div onclick="delete_comment(${data['cid']})">
                         <svg fill="#000000" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24px" height="24px"><path d="M 10.806641 2 C 10.289641 2 9.7956875 2.2043125 9.4296875 2.5703125 L 9 3 L 4 3 A 1.0001 1.0001 0 1 0 4 5 L 20 5 A 1.0001 1.0001 0 1 0 20 3 L 15 3 L 14.570312 2.5703125 C 14.205312 2.2043125 13.710359 2 13.193359 2 L 10.806641 2 z M 4.3652344 7 L 5.8925781 20.263672 C 6.0245781 21.253672 6.877 22 7.875 22 L 16.123047 22 C 17.121047 22 17.974422 21.254859 18.107422 20.255859 L 19.634766 7 L 4.3652344 7 z"></path></svg>
                    </div>
                 </div>
                 <div class="comment-content">${data['comment']}</div>
                 <div class="author">${data['author']}, ${data['time']}</div>`
            const comments = document.querySelector('#comment-section')
            comments.insertBefore(comment, comments.firstChild)
        })
        .catch(err => console.error(err))
    user_comment.value = ''
}

function rate_recipe(rating) {
    const user_rating = document.querySelector('#user-rating')
    const rid = user_rating.dataset.rid
    const old_rating = user_rating.dataset.stars
    if (rating === old_rating) return
    post_request(`/api/rate/r/${rid}`, {'rating': rating})
        .then(data => {
            const new_rating = data['rating']
            const recipe_stars = document.querySelector('#rating .stars')
            recipe_stars.dataset.stars = new_rating
            const post_stars = document.querySelector('.stars.post')
            post_stars.dataset.stars = rating
            user_rating.dataset.stars = rating
        })
        .catch(err => console.error(err))
}

function delete_recipe(rid) {
    post_request(`/api/delete/r/${rid}`)
        .then(() => window.location.href = '/')
        .catch(err => console.error(err))
}
