const table = document.querySelector('table.users')
let sorted_by = 0

function sort_table(col) {
    if (col === sorted_by) return
    sorted_by = col
    const tableBody = table.querySelector('tbody')
    const tableData = table2data(tableBody)
    tableData.sort((a, b) => {
        if (parseInt(a[col]) > parseInt(b[col])) {
            return -1
        }
        return 1
    })
    data2table(tableBody, tableData)
}

function table2data(tableBody) {
    const tableData = []
    tableBody.querySelectorAll('tr')
        .forEach(row => {
            const rowData = []
            row.querySelectorAll('td')
                .forEach(cell => {
                    rowData.push(cell.innerHTML)
                })
            tableData.push(rowData)
        });
    return tableData
}

function data2table(tableBody, tableData) {
    tableBody.querySelectorAll('tr')
        .forEach((row, i) => {
            const rowData = tableData[i]
            row.querySelectorAll('td')
                .forEach((cell, j) => {
                    cell.innerHTML = rowData[j]
                })
            tableData.push(rowData)
        })
}