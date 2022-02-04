/**
 * Handles edit/new recipe forms.
 */


/**
 * Add a row to the ingredients table when clicking plus and
 * remove a specific row when clicking the corresponding minus.
 */
const plus = document.querySelector('#change-form .plus svg')
const og_minus = document.querySelector('#change-form .minus')
const minuses = document.querySelectorAll('#change-form .minus svg')
const table = document.querySelector('#tb-ings')

/**
 * Delete a row selected by one its children
 * and only if at least one content row persists.
 */
function del_row(x) {
    // check viability
    if (table.rows.length > 2) {
        // find row elements
        while (x.tagName !== 'TR')
            x = x.parentNode
        // delete
        table.deleteRow(x.rowIndex)
    }
}

// add listener to all minus elements
for (const minus of minuses)
    minus.addEventListener('click', () => del_row(minus))

/**
 * Insert a new row at the bottom of the table.
 * Create all DOM elements and add them one by one.
 */
plus.addEventListener('click', () => {
    const row_count = table.rows.length
    const row = table.insertRow(row_count);

    const minus = row.insertCell(0)
    const amount = row.insertCell(1)
    const unit = row.insertCell(2)
    const name = row.insertCell(3)

    minus.appendChild(og_minus.cloneNode(true))
    minus.classList.add('col-minus')
    minus.querySelector('svg').addEventListener('click', () => del_row(minus))
    amount.innerHTML = `<input type="number" name="amount-${row_count - 1}" class="amount" step="0.01" >`
    amount.classList.add('col-amount')
    unit.innerHTML = `<input type="text" name="unit-${row_count - 1}" class="unit" >`
    unit.classList.add('col-unit')
    name.innerHTML = `<input type="text" name="name-${row_count - 1}" class="name" >`
    name.classList.add('col-name')
})


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
