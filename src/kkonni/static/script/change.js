/**
 * Handles edit/new recipe forms.
 */


/**
 * Add a row to the ingredients table when clicking plus and
 * remove a specific row when clicking the corresponding minus.
 */
const og_minus = document.querySelector('#change-form .minus')
const og_plus = document.querySelector('#change-form .plus')
const minuses = document.querySelectorAll('#change-form .minus svg')
const pluses = document.querySelectorAll('#change-form .plus svg')
const table = document.querySelector('#tb-ings')

/**
 * Delete a row selected by one its children
 * and only if at least one content row persists.
 */
function del_row(x) {
    // check viability
    if (table.rows.length > 2) {
        // find row parent
        while (x.tagName !== 'TR')
            x = x.parentNode
        // delete
        table.deleteRow(x.rowIndex)
        // update
        update_row_indices()
    }
}

/**
 * Create a new row and insert it
 * after the row that was clicked.
 */
function add_row(x) {

    while (x.tagName !== 'TR')
        x = x.parentNode
    const ins_row_index = x.rowIndex + 1
    const row = table.insertRow(ins_row_index)

    const ctrl = row.insertCell(0)
    const amount = row.insertCell(1)
    const unit = row.insertCell(2)
    const name = row.insertCell(3)

    ctrl.appendChild(og_minus.cloneNode(true))
    ctrl.appendChild(og_plus.cloneNode(true))
    ctrl.classList.add('col-ctrl')
    ctrl.querySelector('.minus svg').addEventListener('click', () => del_row(ctrl))
    ctrl.querySelector('.plus svg').addEventListener('click', () => add_row(ctrl))
    amount.innerHTML = `<input type="number" class="amount" step="0.01">`
    amount.classList.add('col-amount')
    unit.innerHTML = `<input type="text" class="unit">`
    unit.classList.add('col-unit')
    name.innerHTML = `<input type="text" class="name">`
    name.classList.add('col-name')

    update_row_indices()
}

/**
 * Update the indices of the row elements.
 */
function update_row_indices() {
    for (let i = 1; i < table.rows.length; i++) {
        const update_row = table.rows[i]
        update_row.querySelector('.col-amount input').setAttribute('name', `amount-${i - 1}`)
        update_row.querySelector('.col-unit input').setAttribute('name', `unit-${i - 1}`)
        update_row.querySelector('.col-name input').setAttribute('name', `name-${i - 1}`)
    }
}

// add listener to all minus elements
for (const minus of minuses)
    minus.addEventListener('click', () => del_row(minus))

// add listener to all plus elements
for (const plus of pluses)
    plus.addEventListener('click', () => add_row(plus))


/**
 * Limit the file upload size.
 * Should be resizing the file instead of limit upload size.
 * https://stackoverflow.com/a/24015367
 */
const image_upload = document.querySelector('input#image')
const decoy_upload = document.querySelector('#file-input-decoy')
image_upload.addEventListener('change', () => {
    if (image_upload.files[0].size > 209715) {
        alert('Bitte vorest nur Dateien bis 200 kb hochladen.\nLösung kommt bald.')
        image_upload.value = ''
    } else {
        decoy_upload.innerHTML = image_upload.value.replace(/^.*[\\\/]/, '')
    }
})
