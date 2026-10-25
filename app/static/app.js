/**
 * Expense Tracker Dashboard Client
 * Vanilla JavaScript implementation handling real API calls, calculations,
 * filtering, search, modals, and accessible keyboard controls.
 */

document.addEventListener('DOMContentLoaded', () => {
  // --- State ---
  let expensesData = [];
  let deleteTargetId = null;
  let activeMonth = new Date().toISOString().slice(0, 7); // YYYY-MM

  // --- DOM Elements ---
  const currentDateEl = document.getElementById('current-date');
  const cardTotalEl = document.getElementById('card-total');
  const cardCountEl = document.getElementById('card-count');
  const cardHighestEl = document.getElementById('card-highest');
  const cardHighestAmtEl = document.getElementById('card-highest-amount');
  const cardAvgEl = document.getElementById('card-avg');

  const catContainer = document.getElementById('category-container');
  const catCountBadge = document.getElementById('cat-count-badge');

  const searchInput = document.getElementById('search-input');
  const filterCategory = document.getElementById('filter-category');
  const filterStartDate = document.getElementById('filter-start-date');
  const filterEndDate = document.getElementById('filter-end-date');
  const sortSelect = document.getElementById('sort-select');
  const resetFiltersBtn = document.getElementById('reset-filters-btn');
  const exportCsvBtn = document.getElementById('export-csv-btn');

  const transactionRows = document.getElementById('transaction-rows');
  const recordCountEl = document.getElementById('record-count');
  const tableStateContainer = document.getElementById('table-state-container');
  const tableStateIcon = document.getElementById('table-state-icon');
  const tableStateText = document.getElementById('table-state-text');

  // Modals
  const expenseModal = document.getElementById('expense-modal');
  const modalTitle = document.getElementById('modal-title');
  const expenseForm = document.getElementById('expense-form');
  const expenseIdInput = document.getElementById('expense-id');
  const expenseAmountInput = document.getElementById('expense-amount');
  const expenseCategorySelect = document.getElementById('expense-category');
  const customCategoryGroup = document.getElementById('custom-category-group');
  const customCategoryInput = document.getElementById('expense-custom-category');
  const expenseDateInput = document.getElementById('expense-date');
  const expenseDescInput = document.getElementById('expense-desc');

  const openAddBtn = document.getElementById('open-add-btn');
  const closeModalBtn = document.getElementById('close-modal-btn');
  const cancelModalBtn = document.getElementById('cancel-modal-btn');
  const saveExpenseBtn = document.getElementById('save-expense-btn');

  const amountError = document.getElementById('amount-error');
  const categoryError = document.getElementById('category-error');
  const customCatError = document.getElementById('custom-cat-error');
  const dateError = document.getElementById('date-error');

  // Budget
  const budgetSpentRatio = document.getElementById('budget-spent-ratio');
  const budgetProgressBar = document.getElementById('budget-progress-bar');
  const budgetRemainingText = document.getElementById('budget-remaining-text');
  const budgetPctText = document.getElementById('budget-pct-text');
  const budgetWarning = document.getElementById('budget-warning');
  const openBudgetBtn = document.getElementById('open-budget-btn');
  const budgetModal = document.getElementById('budget-modal');
  const budgetForm = document.getElementById('budget-form');
  const budgetMonthInput = document.getElementById('budget-month-input');
  const budgetLimitInput = document.getElementById('budget-limit-input');
  const closeBudgetModalBtn = document.getElementById('close-budget-modal-btn');
  const cancelBudgetBtn = document.getElementById('cancel-budget-btn');

  // Delete Modal
  const deleteModal = document.getElementById('delete-modal');
  const closeDeleteModalBtn = document.getElementById('close-delete-modal-btn');
  const cancelDeleteBtn = document.getElementById('cancel-delete-btn');
  const confirmDeleteBtn = document.getElementById('confirm-delete-btn');

  // Toasts
  const toastContainer = document.getElementById('toast-container');

  // --- Initial Setup ---
  initDate();
  refreshAll();

  // --- Helper: Format Currency in INR ---
  function formatINR(val) {
    const num = Number(val) || 0;
    return '₹' + num.toLocaleString('en-IN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }

  // --- Helper: Toast Notification ---
  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
    toast.innerHTML = `<span style="font-weight:bold">${icon}</span> <span>${escapeHtml(message)}</span>`;
    toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // Set today's date in header & modal defaults
  function initDate() {
    const today = new Date();
    const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
    currentDateEl.textContent = today.toLocaleDateString('en-IN', options);
    expenseDateInput.value = today.toISOString().split('T')[0];
    budgetMonthInput.value = activeMonth;
  }

  // --- Core Data Fetching ---
  async function refreshAll() {
    await Promise.all([
      fetchExpenses(),
      fetchTotals(),
      fetchBudget(),
    ]);
  }

  // 1. Fetch Expenses with query parameters
  async function fetchExpenses() {
    showTableState('loading', 'Loading transactions...');
    try {
      const params = new URLSearchParams();
      if (filterCategory.value) params.append('category', filterCategory.value);
      if (searchInput.value.trim()) params.append('search', searchInput.value.trim());
      if (filterStartDate.value) params.append('start_date', filterStartDate.value);
      if (filterEndDate.value) params.append('end_date', filterEndDate.value);
      if (sortSelect.value) params.append('sort_by', sortSelect.value);

      const res = await fetch(`/api/expenses?${params.toString()}`);
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to fetch transactions');
      }

      expensesData = await res.json();
      renderTransactions(expensesData);
    } catch (err) {
      console.error(err);
      showTableState('error', `Failed to load transactions: ${err.message}`);
      showToast(err.message, 'error');
    }
  }

  // 2. Fetch Totals and Category Breakdown
  async function fetchTotals() {
    try {
      const params = new URLSearchParams();
      if (filterStartDate.value) params.append('start_date', filterStartDate.value);
      if (filterEndDate.value) params.append('end_date', filterEndDate.value);

      const res = await fetch(`/api/expenses/totals?${params.toString()}`);
      if (!res.ok) throw new Error('Failed to fetch summary totals');
      const data = await res.json();
      renderSummaries(data);
      renderCategories(data.categories || []);
    } catch (err) {
      console.error(err);
      showToast('Could not refresh summaries', 'error');
    }
  }

  // 3. Fetch Budget Status
  async function fetchBudget() {
    try {
      const res = await fetch(`/api/budgets/${activeMonth}`);
      if (res.ok) {
        const bData = await res.json();
        renderBudget(bData);
      }
    } catch (err) {
      console.error('Budget fetch err:', err);
    }
  }

  // --- Rendering UI ---
  function renderSummaries(summary) {
    cardTotalEl.textContent = formatINR(summary.total_expenses);
    cardCountEl.textContent = summary.transaction_count.toString();
    cardAvgEl.textContent = formatINR(summary.average_expense);

    if (summary.highest_spending_category) {
      cardHighestEl.textContent = summary.highest_spending_category;
      const highestCat = summary.categories.find(c => c.category === summary.highest_spending_category);
      cardHighestAmtEl.textContent = highestCat ? formatINR(highestCat.total) : '₹0.00';
    } else {
      cardHighestEl.textContent = 'None';
      cardHighestAmtEl.textContent = '₹0.00';
    }
  }

  function renderCategories(categories) {
    catContainer.innerHTML = '';
    catCountBadge.textContent = `${categories.length} Categories`;

    if (categories.length === 0) {
      catContainer.innerHTML = `
        <div class="state-container">
          <div class="state-icon">📊</div>
          <p>No category spending recorded yet.</p>
        </div>
      `;
      return;
    }

    categories.forEach(cat => {
      const item = document.createElement('div');
      item.className = 'category-item';

      const header = document.createElement('div');
      header.className = 'category-header';
      header.innerHTML = `
        <span class="cat-name">${escapeHtml(cat.category)} (${cat.count})</span>
        <span class="cat-amount">${formatINR(cat.total)} <small>(${cat.percentage.toFixed(1)}%)</small></span>
      `;

      const track = document.createElement('div');
      track.className = 'progress-track';
      const bar = document.createElement('div');
      bar.className = 'progress-bar';
      bar.style.width = `${Math.min(cat.percentage, 100)}%`;
      track.appendChild(bar);

      item.appendChild(header);
      item.appendChild(track);
      catContainer.appendChild(item);
    });
  }

  function renderBudget(b) {
    if (!b || b.monthly_budget === 0) {
      budgetSpentRatio.textContent = `${formatINR(b.total_spent)} / Not set`;
      budgetProgressBar.style.width = '0%';
      budgetRemainingText.textContent = 'Remaining: N/A';
      budgetPctText.textContent = '0%';
      budgetWarning.style.display = 'none';
      return;
    }

    budgetSpentRatio.textContent = `${formatINR(b.total_spent)} / ${formatINR(b.monthly_budget)}`;
    const pct = Math.min(b.percentage_used, 100);
    budgetProgressBar.style.width = `${pct}%`;
    budgetPctText.textContent = `${b.percentage_used.toFixed(1)}%`;

    if (b.is_exceeded) {
      budgetProgressBar.style.background = '#ef4444';
      budgetRemainingText.textContent = `Overspent by: ${formatINR(Math.abs(b.remaining_budget))}`;
      budgetWarning.style.display = 'block';
    } else {
      budgetProgressBar.style.background = 'linear-gradient(90deg, #6366f1, #10b981)';
      budgetRemainingText.textContent = `Remaining: ${formatINR(b.remaining_budget)}`;
      budgetWarning.style.display = 'none';
    }
  }

  function renderTransactions(list) {
    transactionRows.innerHTML = '';
    recordCountEl.textContent = `${list.length} Records`;

    if (list.length === 0) {
      showTableState('empty', 'No transactions found matching your criteria.');
      return;
    }

    tableStateContainer.style.display = 'none';

    list.forEach(tx => {
      const tr = document.createElement('tr');
      tr.id = `expense-row-${tx.id}`;

      // ID
      const tdId = document.createElement('td');
      tdId.textContent = `#${tx.id}`;
      tr.appendChild(tdId);

      // Category
      const tdCat = document.createElement('td');
      const tag = document.createElement('span');
      tag.className = 'category-tag';
      tag.textContent = tx.category;
      tdCat.appendChild(tag);
      tr.appendChild(tdCat);

      // Amount
      const tdAmount = document.createElement('td');
      tdAmount.style.fontWeight = '600';
      tdAmount.textContent = formatINR(tx.amount);
      tr.appendChild(tdAmount);

      // Date
      const tdDate = document.createElement('td');
      tdDate.textContent = tx.date;
      tr.appendChild(tdDate);

      // Description
      const tdDesc = document.createElement('td');
      tdDesc.textContent = tx.description || '—';
      tdDesc.style.color = tx.description ? 'inherit' : 'var(--text-dim)';
      tr.appendChild(tdDesc);

      // Actions
      const tdAction = document.createElement('td');
      tdAction.style.textAlign = 'right';
      const actionDiv = document.createElement('div');
      actionDiv.className = 'action-buttons';
      actionDiv.style.justifyContent = 'flex-end';

      const editBtn = document.createElement('button');
      editBtn.className = 'btn btn-secondary btn-sm';
      editBtn.setAttribute('aria-label', `Edit expense ${tx.id}`);
      editBtn.textContent = 'Edit';
      editBtn.onclick = () => openEditModal(tx);

      const delBtn = document.createElement('button');
      delBtn.className = 'btn btn-danger btn-sm';
      delBtn.setAttribute('aria-label', `Delete expense ${tx.id}`);
      delBtn.textContent = 'Delete';
      delBtn.onclick = () => openDeleteModal(tx.id);

      actionDiv.appendChild(editBtn);
      actionDiv.appendChild(delBtn);
      tdAction.appendChild(actionDiv);
      tr.appendChild(tdAction);

      transactionRows.appendChild(tr);
    });
  }

  function showTableState(type, msg) {
    transactionRows.innerHTML = '';
    tableStateContainer.style.display = 'block';
    tableStateText.textContent = msg;
    if (type === 'loading') tableStateIcon.textContent = '⏳';
    else if (type === 'error') tableStateIcon.textContent = '⚠️';
    else tableStateIcon.textContent = '🔍';
  }

  // --- Modal Operations ---
  function openAddModal() {
    expenseForm.reset();
    expenseIdInput.value = '';
    modalTitle.textContent = 'Add New Expense';
    saveExpenseBtn.textContent = 'Save Expense';
    expenseDateInput.value = new Date().toISOString().split('T')[0];
    customCategoryGroup.style.display = 'none';
    hideFormErrors();
    expenseModal.classList.add('active');
    expenseAmountInput.focus();
  }

  function openEditModal(tx) {
    hideFormErrors();
    expenseIdInput.value = tx.id;
    modalTitle.textContent = `Edit Expense #${tx.id}`;
    saveExpenseBtn.textContent = 'Update Expense';
    expenseAmountInput.value = tx.amount;
    expenseDateInput.value = tx.date;
    expenseDescInput.value = tx.description || '';

    // Check if category exists in select
    let found = false;
    for (let opt of expenseCategorySelect.options) {
      if (opt.value === tx.category) {
        found = true;
        break;
      }
    }

    if (found) {
      expenseCategorySelect.value = tx.category;
      customCategoryGroup.style.display = 'none';
    } else {
      expenseCategorySelect.value = 'CUSTOM';
      customCategoryGroup.style.display = 'block';
      customCategoryInput.value = tx.category;
    }

    expenseModal.classList.add('active');
    expenseAmountInput.focus();
  }

  function closeModal() {
    expenseModal.classList.remove('active');
    hideFormErrors();
  }

  function hideFormErrors() {
    amountError.classList.remove('visible');
    categoryError.classList.remove('visible');
    customCatError.classList.remove('visible');
    dateError.classList.remove('visible');
  }

  expenseCategorySelect.addEventListener('change', () => {
    if (expenseCategorySelect.value === 'CUSTOM') {
      customCategoryGroup.style.display = 'block';
      customCategoryInput.focus();
    } else {
      customCategoryGroup.style.display = 'none';
    }
  });

  // Handle Form Submission (Create or Update)
  expenseForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideFormErrors();

    const amtStr = expenseAmountInput.value.trim();
    const amt = parseFloat(amtStr);
    let cat = expenseCategorySelect.value;
    const customCat = customCategoryInput.value.trim();
    const dateVal = expenseDateInput.value;
    const descVal = expenseDescInput.value.trim();
    const idVal = expenseIdInput.value;

    let hasError = false;

    if (!amtStr || isNaN(amt) || !isFinite(amt) || amt <= 0) {
      amountError.classList.add('visible');
      hasError = true;
    }

    if (!cat) {
      categoryError.classList.add('visible');
      hasError = true;
    } else if (cat === 'CUSTOM') {
      if (!customCat) {
        customCatError.classList.add('visible');
        hasError = true;
      } else {
        cat = customCat;
      }
    }

    if (!dateVal) {
      dateError.classList.add('visible');
      hasError = true;
    }

    if (hasError) return;

    saveExpenseBtn.disabled = true;
    saveExpenseBtn.textContent = 'Saving...';

    const payload = {
      amount: amt,
      category: cat,
      date: dateVal,
      description: descVal || null,
    };

    try {
      let res;
      if (idVal) {
        // Update PUT
        res = await fetch(`/api/expenses/${idVal}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      } else {
        // Create POST
        res = await fetch('/api/expenses', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      }

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        const msg = errorData.detail || errorData.errors?.join(', ') || 'Submission failed';
        throw new Error(msg);
      }

      closeModal();
      showToast(idVal ? 'Expense updated successfully!' : 'Expense created successfully!', 'success');
      await refreshAll();
    } catch (err) {
      console.error(err);
      showToast(err.message, 'error');
    } finally {
      saveExpenseBtn.disabled = false;
      saveExpenseBtn.textContent = idVal ? 'Update Expense' : 'Save Expense';
    }
  });

  // --- Delete Handling ---
  function openDeleteModal(id) {
    deleteTargetId = id;
    document.getElementById('delete-modal-msg').textContent = `Are you sure you want to delete expense #${id}?`;
    deleteModal.classList.add('active');
    confirmDeleteBtn.focus();
  }

  function closeDeleteModal() {
    deleteModal.classList.remove('active');
    deleteTargetId = null;
  }

  confirmDeleteBtn.addEventListener('click', async () => {
    if (!deleteTargetId) return;
    confirmDeleteBtn.disabled = true;
    confirmDeleteBtn.textContent = 'Deleting...';

    try {
      const res = await fetch(`/api/expenses/${deleteTargetId}`, {
        method: 'DELETE',
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Failed to delete expense');
      }

      closeDeleteModal();
      showToast('Expense deleted successfully.', 'success');
      await refreshAll();
    } catch (err) {
      console.error(err);
      showToast(err.message, 'error');
    } finally {
      confirmDeleteBtn.disabled = false;
      confirmDeleteBtn.textContent = 'Delete';
    }
  });

  // --- Budget Modal Handlers ---
  openBudgetBtn.addEventListener('click', () => {
    budgetMonthInput.value = activeMonth;
    budgetModal.classList.add('active');
    budgetLimitInput.focus();
  });

  function closeBudgetModal() {
    budgetModal.classList.remove('active');
    document.getElementById('budget-error-msg').classList.remove('visible');
  }

  budgetForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const monthVal = budgetMonthInput.value;
    const limitVal = parseFloat(budgetLimitInput.value);

    if (!monthVal || isNaN(limitVal) || limitVal <= 0) {
      document.getElementById('budget-error-msg').classList.add('visible');
      return;
    }

    try {
      const res = await fetch('/api/budgets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ month: monthVal, monthly_budget: limitVal }),
      });
      if (!res.ok) throw new Error('Failed to update monthly budget');
      activeMonth = monthVal;
      const bData = await res.json();
      renderBudget(bData);
      closeBudgetModal();
      showToast('Budget configured successfully!', 'success');
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // --- Filtering & Sorting Event Listeners ---
  let debounceTimer;
  searchInput.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      fetchExpenses();
    }, 250);
  });

  filterCategory.addEventListener('change', () => fetchExpenses());
  sortSelect.addEventListener('change', () => fetchExpenses());
  filterStartDate.addEventListener('change', () => {
    fetchExpenses();
    fetchTotals();
  });
  filterEndDate.addEventListener('change', () => {
    fetchExpenses();
    fetchTotals();
  });

  resetFiltersBtn.addEventListener('click', () => {
    searchInput.value = '';
    filterCategory.value = '';
    filterStartDate.value = '';
    filterEndDate.value = '';
    sortSelect.value = 'date_desc';
    refreshAll();
    showToast('Filters reset to default.', 'info');
  });

  // Export CSV
  exportCsvBtn.addEventListener('click', () => {
    const params = new URLSearchParams();
    if (filterCategory.value) params.append('category', filterCategory.value);
    if (searchInput.value.trim()) params.append('search', searchInput.value.trim());
    if (filterStartDate.value) params.append('start_date', filterStartDate.value);
    if (filterEndDate.value) params.append('end_date', filterEndDate.value);
    if (sortSelect.value) params.append('sort_by', sortSelect.value);

    window.location.href = `/api/expenses/export/csv?${params.toString()}`;
    showToast('Exporting filtered transactions to CSV...', 'info');
  });

  // --- Accessibility & Modal Event Bindings ---
  openAddBtn.addEventListener('click', openAddModal);
  closeModalBtn.addEventListener('click', closeModal);
  cancelModalBtn.addEventListener('click', closeModal);

  closeBudgetModalBtn.addEventListener('click', closeBudgetModal);
  cancelBudgetBtn.addEventListener('click', closeBudgetModal);

  closeDeleteModalBtn.addEventListener('click', closeDeleteModal);
  cancelDeleteBtn.addEventListener('click', closeDeleteModal);

  // Escape key closes modals
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (expenseModal.classList.contains('active')) closeModal();
      if (budgetModal.classList.contains('active')) closeBudgetModal();
      if (deleteModal.classList.contains('active')) closeDeleteModal();
    }
  });

  // Clicking backdrop closes modal
  [expenseModal, budgetModal, deleteModal].forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.remove('active');
      }
    });
  });
});
