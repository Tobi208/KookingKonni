const btn_add_row = document.querySelector('#change-form .plus svg')
const og_minus = document.querySelector('#change-form .minus')
const btn_del_rows = document.querySelectorAll('#change-form .minus svg')
const tb_ings = document.querySelector('#tb-ings')

function add_row() {
    const row_count = tb_ings.rows.length
    const row = tb_ings.insertRow(row_count);

    const minus = row.insertCell(0)
    const amount = row.insertCell(1)
    const unit = row.insertCell(2)
    const name = row.insertCell(3)

    minus.appendChild(og_minus.cloneNode(true))
    minus.classList.add("col-minus")
    minus.querySelector('svg').addEventListener("click", () => {del_row(minus)})
    amount.innerHTML = `<input type="number" name="amount-${row_count - 1}" class="amount" step="0.01" required>`
    amount.classList.add("col-amount")
    unit.innerHTML = `<input type="text" name="unit-${row_count - 1}" class="unit" required>`
    unit.classList.add("col-unit")
    name.innerHTML = `<input type="text" name="name-${row_count - 1}" class="name" required>`
    name.classList.add("col-name")
}

function del_row(x) {
    const row_count = tb_ings.rows.length
    if (row_count > 3) tb_ings.deleteRow(get_row_index(x))
}

function get_row_index(x) {
  while (x.tagName !== "TR")
      x = x.parentNode
  return x.rowIndex
}

btn_add_row.addEventListener("click", add_row)
for (const minus of btn_del_rows) {
    minus.addEventListener("click", () => {del_row(minus)})
}
