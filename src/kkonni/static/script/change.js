/**
 * Handles edit/new recipe forms.
 */

const og_minus = document.querySelector('#change-form .minus')
const og_plus = document.querySelector('#change-form .plus')
const minuses = document.querySelectorAll('#change-form .minus svg')
const pluses = document.querySelectorAll('#change-form .plus svg')
const tb_minuses = document.querySelectorAll('#change-form .tb-minus svg')
const tb_pluses = document.querySelectorAll('#change-form .tb-plus svg')
const tables_cont = document.querySelector('#change-form #all-tb-ings')
let table_conts = tables_cont.querySelectorAll('#change-form .tb-ings-cont')

/**
 * Delete a row selected by one its children
 * and only if at least one content row persists.
 */
function del_row(x) {
    while (x.tagName !== 'TR')
        x = x.parentNode

    let table = x
    while (table.tagName !== 'TABLE')
        table = table.parentNode

    // check viability
    if (table.rows.length > 2) {
        table.deleteRow(x.rowIndex)
        update_row_indices(table)
    }
}

/**
 * Create a new row and insert it
 * after the row that was clicked.
 */
function add_row(x) {

    while (x.tagName !== 'TR')
        x = x.parentNode
    let table = x
    while (table.tagName !== 'TABLE')
        table = table.parentNode
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
    amount.querySelector('.amount').focus()
    unit.innerHTML = `<input type="text" class="unit">`
    unit.classList.add('col-unit')
    name.innerHTML = `<input type="text" class="name">`
    name.classList.add('col-name')

    update_row_indices(table)
}

/**
 * Update the indices of the row elements.
 */
function update_row_indices(table) {
    const t = table.dataset.index
    for (let i = 1; i < table.rows.length; i++) {
        const update_row = table.rows[i]
        update_row.querySelector('.col-amount input').setAttribute('name', `amount-${t}-${i - 1}`)
        update_row.querySelector('.col-unit input').setAttribute('name', `unit-${t}-${i - 1}`)
        update_row.querySelector('.col-name input').setAttribute('name', `name-${t}-${i - 1}`)
    }
}

// add listener to all minus elements
for (const minus of minuses)
    minus.addEventListener('click', () => del_row(minus))

// add listener to all plus elements
for (const plus of pluses)
    plus.addEventListener('click', () => add_row(plus))

/**
 * Delete a table container containing an element x.
 */
function del_table(x) {
    while (!x.classList.contains('tb-ings-cont'))
        x = x.parentNode

    if (table_conts.length > 1) {
        x.remove()
        update_table_indices()
    }
}

/**
 * Add a new table container after an element x.
 */
function add_table(x) {

    while (!x.classList.contains('tb-ings-cont'))
        x = x.parentNode

    const table_cont = table_conts[0].cloneNode(true)
    x.insertAdjacentElement('afterend', table_cont)

    table_cont.querySelector('.pair input').setAttribute('value', '')

    const table = table_cont.querySelector('.tb-ings')
    while (table.rows.length > 2)
        table.rows[table.rows.length - 1].remove()

    for (const input of table.querySelectorAll('input'))
        input.setAttribute('value', '')

    const row = table.rows[1]
    const ctrl = row.cells[0]
    ctrl.querySelector('.minus svg').addEventListener('click', () => del_row(ctrl))
    ctrl.querySelector('.plus svg').addEventListener('click', () => add_row(ctrl))

    const tb_minus = table_cont.querySelector('.tb-minus')
    const tb_plus = table_cont.querySelector('.tb-plus')
    tb_minus.addEventListener('click', () => del_table(tb_minus))
    tb_plus.addEventListener('click', () => add_table(tb_plus))

    update_table_indices()
}

/**
 * Adjust table container and inner table indices.
 */
function update_table_indices() {
    table_conts = tables_cont.querySelectorAll('.tb-ings-cont')
    let label, input, table
    for (let i = 0; i < table_conts.length; i++) {
        label = table_conts[i].querySelector('.pair label')
        label.setAttribute('for', `tb-ings-title-${i}`)
        input = table_conts[i].querySelector('.pair input')
        input.setAttribute('id', `tb-ings-title-${i}`)
        input.setAttribute('name', `tb-ings-title-${i}`)
        table = table_conts[i].querySelector('.tb-ings')
        table.dataset.index = i.toString()
        update_row_indices(table)
    }
}

// add listener to all table minus elements
for (const minus of tb_minuses)
    minus.addEventListener('click', () => del_table(minus))

// add listener to all table plus elements
for (const plus of tb_pluses)
    plus.addEventListener('click', () => add_table(plus))

/**
 * Add a new row if enter is pressed in the description
 * cell of the last row.
 */
tables_cont.addEventListener('keypress', (event) => {
    if (event.keyCode === 13) {
        const e = document.activeElement
        if (e.parentNode.classList.contains('col-name') && is_in_last_row(e)) {
            add_row(e)
            event.preventDefault()
            event.stopPropagation()
        }
    }
})
function is_in_last_row(x) {
    while (x.tagName !== 'TR')
        x = x.parentNode
    let table = x
    while (table.tagName !== 'TABLE')
        table = table.parentNode
    return x.rowIndex === table.rows.length - 1
}


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
