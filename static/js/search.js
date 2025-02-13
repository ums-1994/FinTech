document.getElementById('searchInput').addEventListener('input', function() {
    const query = this.value;
    const rows = document.querySelectorAll('#expenseTable tbody tr');
    rows.forEach(row => {
        const descriptionCell = row.querySelector('td:nth-child(5)');
        const description = descriptionCell.textContent;
        if (fuzzySearch(query, description)) {
            descriptionCell.innerHTML = highlightMatches(query, description);
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
});

function sortTable(columnIndex) {
    const table = document.getElementById('expenseTable');
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    rows.sort((a, b) => {
        const aValue = a.children[columnIndex].textContent;
        const bValue = b.children[columnIndex].textContent;
        return aValue.localeCompare(bValue, undefined, { numeric: true });
    });
    table.tBodies[0].append(...rows);
}

function paginateTable(pageNumber, pageSize) {
    const rows = document.querySelectorAll('#expenseTable tbody tr');
    rows.forEach((row, index) => {
        row.style.display = (index >= (pageNumber - 1) * pageSize && index < pageNumber * pageSize) ? '' : 'none';
    });
}

function fuzzySearch(query, text) {
    const queryChars = query.toLowerCase().split('');
    const textChars = text.toLowerCase().split('');
    let queryIndex = 0;
    for (let i = 0; i < textChars.length; i++) {
        if (textChars[i] === queryChars[queryIndex]) {
            queryIndex++;
            if (queryIndex === queryChars.length) return true;
        }
    }
    return false;
}

function highlightMatches(query, text) {
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<span class="highlight">$1</span>');
}

function applyFilters() {
    const searchQuery = document.getElementById('searchInput').value.toLowerCase();
    const category = document.getElementById('categoryFilter').value.toLowerCase();
    const startDate = document.getElementById('startDateFilter').value;
    const endDate = document.getElementById('endDateFilter').value;

    const rows = document.querySelectorAll('#expenseTable tbody tr');
    rows.forEach(row => {
        const description = row.querySelector('td:nth-child(5)').textContent.toLowerCase();
        const rowCategory = row.querySelector('td:nth-child(3)').textContent.toLowerCase();
        const rowDate = row.querySelector('td:nth-child(2)').textContent;

        const matchesSearch = description.includes(searchQuery);
        const matchesCategory = category === '' || rowCategory === category;
        const matchesDate = (!startDate || rowDate >= startDate) && (!endDate || rowDate <= endDate);

        row.style.display = matchesSearch && matchesCategory && matchesDate ? '' : 'none';
    });
}

document.getElementById('searchInput').addEventListener('input', applyFilters);
document.getElementById('categoryFilter').addEventListener('change', applyFilters);
document.getElementById('startDateFilter').addEventListener('change', applyFilters);
document.getElementById('endDateFilter').addEventListener('change', applyFilters);

function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('categoryFilter').value = '';
    document.getElementById('startDateFilter').value = '';
    document.getElementById('endDateFilter').value = '';
    applyFilters();
}