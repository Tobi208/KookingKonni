const btn_add_row = document.getElementById("add-row")
const btn_del_row = document.getElementById("remove-row")
const tb_ings = document.getElementById('tb-ings')

function add_row() {
    const row_count = tb_ings.rows.length
    const row = tb_ings.insertRow(row_count - 1);

    const amount = row.insertCell(0)
    const unit = row.insertCell(1)
    const name = row.insertCell(2)

    amount.innerHTML = `<input type="number" name="amount-${row_count - 2}" class="amount" required>`
    unit.innerHTML = `<input type="text" name="unit-${row_count - 2}" class="unit" required>`
    name.innerHTML = `<input type="text" name="name-${row_count - 2}" class="name" required>`
}

function del_row() {
    const row_count = tb_ings.rows.length
    if (row_count > 3) { tb_ings.deleteRow(row_count - 2) }
}

btn_add_row.addEventListener("click", add_row)
btn_del_row.addEventListener("click", del_row)
