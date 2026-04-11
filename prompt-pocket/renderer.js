const PRIORITY_META = {
  urgent: { label: '紧急', weight: 4, className: 'badge-priority-urgent' },
  high: { label: '高', weight: 3, className: 'badge-priority-high' },
  medium: { label: '中', weight: 2, className: 'badge-priority-medium' },
  low: { label: '低', weight: 1, className: 'badge-priority-low' }
}

const STATUS_META = {
  todo: { label: '未开始' },
  done: { label: '已完成' }
}

const state = {
  prompts: [],
  notes: [],
  config: {},
  dataDir: '',
  activeTab: 'prompts',
  searches: {
    prompt: '',
    note: '',
    trash: ''
  },
  sorts: {
    prompt: 'updated-desc',
    note: 'updated-desc',
    trash: 'deleted-desc'
  },
  noteStatusFilter: 'todo',
  notePriorityFilter: 'all',
  trashType: 'all',
  deleteTarget: null,
  completionTargetId: null,
  isCapturingShortcut: false,
  shortcutHandler: null
}

async function init() {
  state.prompts = await window.api.getPrompts()
  state.notes = await window.api.getNotes()
  state.config = await window.api.getConfig()
  state.dataDir = await window.api.getDataDir()

  bindEvents()
  loadConfig()
  loadSettings()
  renderAll()
}

function bindEvents() {
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => switchTab(tab.dataset.tab))
  })

  document.getElementById('prompt-search').addEventListener('input', (e) => {
    state.searches.prompt = e.target.value
    renderPrompts()
  })

  document.getElementById('note-search').addEventListener('input', (e) => {
    state.searches.note = e.target.value
    renderNotes()
  })

  document.getElementById('trash-search').addEventListener('input', (e) => {
    state.searches.trash = e.target.value
    renderTrash()
  })

  document.getElementById('prompt-sort').addEventListener('change', (e) => {
    state.sorts.prompt = e.target.value
    renderPrompts()
  })

  document.getElementById('note-sort').addEventListener('change', (e) => {
    state.sorts.note = e.target.value
    renderNotes()
  })

  document.getElementById('trash-sort').addEventListener('change', (e) => {
    state.sorts.trash = e.target.value
    renderTrash()
  })

  document.getElementById('note-status-filter').addEventListener('change', (e) => {
    state.noteStatusFilter = e.target.value
    renderNotes()
  })

  document.getElementById('note-priority-filter').addEventListener('change', (e) => {
    state.notePriorityFilter = e.target.value
    renderNotes()
  })

  document.getElementById('trash-type').addEventListener('change', (e) => {
    state.trashType = e.target.value
    renderTrash()
  })

  document.getElementById('auto-launch-toggle').addEventListener('change', toggleAutoLaunch)

  document.addEventListener('keydown', handleGlobalKeydown)
  document.addEventListener('click', handleDocumentClick)
}

function handleGlobalKeydown(e) {
  if (e.key !== 'Escape') return

  if (state.isCapturingShortcut) {
    stopCapturingShortcut()
    return
  }

  if (document.getElementById('completion-modal').classList.contains('show')) {
    closeCompletionModal()
    return
  }

  if (document.getElementById('delete-modal').classList.contains('show')) {
    closeDeleteModal()
    return
  }

  if (document.getElementById('modal').classList.contains('show')) {
    closeModal()
    return
  }

  window.api.hideWindow()
}

function handleDocumentClick(e) {
  const actionEl = e.target.closest('[data-action]')
  if (actionEl) {
    const { action } = actionEl.dataset

    if (action === 'hide-window') return window.api.hideWindow()
    if (action === 'add-prompt') return openEditor('prompt')
    if (action === 'add-note') return openEditor('note')
    if (action === 'close-modal') return closeModal()
    if (action === 'save-edit') return saveEdit()
    if (action === 'clear-search') return clearSearch(actionEl.dataset.target)
    if (action === 'capture-shortcut') return captureShortcut()
    if (action === 'save-shortcut') return saveShortcut()
    if (action === 'open-data-dir') return openDataDir()
    if (action === 'close-delete-modal') return closeDeleteModal()
    if (action === 'confirm-delete') return confirmDelete()
    if (action === 'close-completion-modal') return closeCompletionModal()
    if (action === 'add-related-item') return addRelatedInput('')
    if (action === 'remove-related-item') return removeRelatedInput(actionEl.closest('.related-item-row'))
    if (action === 'confirm-completion') return confirmCompletion()

    const type = actionEl.dataset.type
    const id = actionEl.dataset.id

    if (action === 'edit-item') return openEditor(type, id)
    if (action === 'copy-item') return copyItem(type, id)
    if (action === 'soft-delete') return requestDelete(type, id, 'soft')
    if (action === 'restore-item') return restoreItem(type, id)
    if (action === 'purge-item') return requestDelete(type, id, 'purge')
    if (action === 'toggle-note-status') return handleNoteStatusToggle(id)

    return
  }

  const card = e.target.closest('.item-card[data-copyable="true"]')
  if (!card) return

  copyItem(card.dataset.type, card.dataset.id)
}

function switchTab(tabName) {
  state.activeTab = tabName
  document.querySelectorAll('.tab').forEach(tab => {
    tab.classList.toggle('active', tab.dataset.tab === tabName)
  })
  document.querySelectorAll('.panel').forEach(panel => {
    panel.classList.toggle('active', panel.id === `${tabName}-panel`)
  })
}

function getCollection(type) {
  return type === 'prompt' ? state.prompts : state.notes
}

function findItem(type, id) {
  return getCollection(type).find(item => item.id === id)
}

function getActiveItems(type) {
  return getCollection(type).filter(item => !item.deletedAt)
}

function getDeletedItems(type) {
  return getCollection(type).filter(item => item.deletedAt)
}

function normalizeText(value) {
  return (value || '').toString().trim().toLowerCase()
}

function normalizePriority(priority) {
  return PRIORITY_META[priority] ? priority : 'medium'
}

function normalizeStatus(status) {
  return STATUS_META[status] ? status : 'todo'
}

function getPriorityMeta(priority) {
  return PRIORITY_META[normalizePriority(priority)]
}

function getPriorityWeight(priority) {
  return getPriorityMeta(priority).weight
}

function normalizeRelatedItems(relatedItems) {
  if (!Array.isArray(relatedItems)) return []
  return relatedItems.map(item => normalizeText(item) ? item.trim() : '').filter(Boolean)
}

function matchesFilter(item, keyword) {
  const q = normalizeText(keyword)
  if (!q) return true
  return [item.title, item.category, item.content, ...(item.relatedItems || [])].some(field => normalizeText(field).includes(q))
}

function matchesNotePriority(item, filterValue) {
  if (filterValue === 'all') return true
  return normalizePriority(item.priority) === filterValue
}

function matchesNoteStatus(item, filterValue) {
  return normalizeStatus(item.status) === filterValue
}

function getSortTimestamp(item, key) {
  const raw = item[key] || item.updatedAt || item.createdAt || 0
  const time = new Date(raw).getTime()
  return Number.isNaN(time) ? 0 : time
}

function compareText(a, b) {
  return (a || '').localeCompare(b || '', 'zh-CN', { sensitivity: 'base' })
}

function sortItems(items, sortKey) {
  const list = [...items]

  switch (sortKey) {
    case 'created-asc':
      return list.sort((a, b) => getSortTimestamp(a, 'createdAt') - getSortTimestamp(b, 'createdAt'))
    case 'created-desc':
      return list.sort((a, b) => getSortTimestamp(b, 'createdAt') - getSortTimestamp(a, 'createdAt'))
    case 'title-asc':
      return list.sort((a, b) => compareText(a.title, b.title))
    case 'title-desc':
      return list.sort((a, b) => compareText(b.title, a.title))
    case 'category-asc':
      return list.sort((a, b) => compareText(a.category, b.category) || compareText(a.title, b.title))
    case 'priority-asc':
      return list.sort((a, b) => getPriorityWeight(a.priority) - getPriorityWeight(b.priority) || compareText(a.title, b.title))
    case 'priority-desc':
      return list.sort((a, b) => getPriorityWeight(b.priority) - getPriorityWeight(a.priority) || compareText(a.title, b.title))
    case 'deleted-asc':
      return list.sort((a, b) => getSortTimestamp(a, 'deletedAt') - getSortTimestamp(b, 'deletedAt'))
    case 'deleted-desc':
      return list.sort((a, b) => getSortTimestamp(b, 'deletedAt') - getSortTimestamp(a, 'deletedAt'))
    case 'updated-desc':
    default:
      return list.sort((a, b) => getSortTimestamp(b, 'updatedAt') - getSortTimestamp(a, 'updatedAt'))
  }
}

function renderAll() {
  renderPrompts()
  renderNotes()
  renderTrash()
}

function renderPrompts() {
  const items = sortItems(
    getActiveItems('prompt').filter(item => matchesFilter(item, state.searches.prompt)),
    state.sorts.prompt
  )

  renderItemList({
    containerId: 'prompts-list',
    type: 'prompt',
    items,
    emptyText: state.searches.prompt ? '没有匹配的 Prompt' : '暂无 Prompt，点击“新增”添加',
    copyable: true
  })
  updateCount('prompt-count', items.length, getActiveItems('prompt').length)
}

function renderNotes() {
  const filtered = getActiveItems('note')
    .filter(item => matchesFilter(item, state.searches.note))
    .filter(item => matchesNoteStatus(item, state.noteStatusFilter))
    .filter(item => matchesNotePriority(item, state.notePriorityFilter))

  const items = sortItems(filtered, state.sorts.note)

  renderItemList({
    containerId: 'notes-list',
    type: 'note',
    items,
    emptyText: state.searches.note || state.notePriorityFilter !== 'all' ? '没有匹配的消息' : (state.noteStatusFilter === 'todo' ? '暂无未开始消息，点击“新增”添加' : '暂无已完成消息'),
    copyable: true
  })
  updateCount('note-count', items.length, getActiveItems('note').length)
}

function renderTrash() {
  const deletedPrompts = getDeletedItems('prompt').map(item => ({ ...item, _type: 'prompt' }))
  const deletedNotes = getDeletedItems('note').map(item => ({ ...item, _type: 'note' }))

  const filteredByType = [...deletedPrompts, ...deletedNotes].filter(item => {
    if (state.trashType !== 'all' && item._type !== state.trashType) return false
    return matchesFilter(item, state.searches.trash)
  })

  const items = sortItems(filteredByType, state.sorts.trash)
  const total = [...deletedPrompts, ...deletedNotes].filter(item => state.trashType === 'all' || item._type === state.trashType).length

  const list = document.getElementById('trash-list')
  if (items.length === 0) {
    list.innerHTML = `<div class="empty-hint">${state.searches.trash || total > 0 ? '垃圾站里没有匹配内容' : '垃圾站是空的'}</div>`
  } else {
    list.innerHTML = items.map(item => renderTrashCard(item)).join('')
  }

  updateCount('trash-count', items.length, total)
}

function renderItemList({ containerId, type, items, emptyText, copyable }) {
  const list = document.getElementById(containerId)
  if (items.length === 0) {
    list.innerHTML = `<div class="empty-hint">${emptyText}</div>`
    return
  }

  list.innerHTML = items.map(item => renderItemCard(type, item, copyable)).join('')
}

function renderPriorityBadge(priority) {
  const meta = getPriorityMeta(priority)
  return `<span class="badge ${meta.className}">${meta.label}优先级</span>`
}

function renderRelatedBlock(item) {
  const relatedItems = normalizeRelatedItems(item.relatedItems)
  if (!relatedItems.length) return ''

  return `
    <div class="related-preview">
      <div class="related-title">关联内容 ${relatedItems.length} 条</div>
      <ul>
        ${relatedItems.slice(0, 3).map(text => `<li>${escapeHtml(text)}</li>`).join('')}
      </ul>
    </div>
  `
}

function renderNoteSwitch(item) {
  const isTodo = normalizeStatus(item.status) === 'todo'
  return `
    <label class="todo-switch" title="${isTodo ? '点击标记完成' : '点击恢复为未开始'}">
      <input type="checkbox" ${isTodo ? 'checked' : ''} data-action="toggle-note-status" data-id="${item.id}">
      <span class="todo-slider"></span>
      <span class="todo-label">${isTodo ? '未开始' : '已完成'}</span>
    </label>
  `
}

function renderItemCard(type, item, copyable) {
  const title = escapeHtml(item.title || '无标题')
  const category = item.category ? `<span class="badge badge-category">${escapeHtml(item.category)}</span>` : ''
  const priority = type === 'note' ? renderPriorityBadge(item.priority) : ''
  const statusSwitch = type === 'note' ? renderNoteSwitch(item) : ''
  const preview = escapeHtml(item.content || '')
  const dateText = type === 'note' && normalizeStatus(item.status) === 'done' && item.completedAt
    ? `完成于 ${formatDate(item.completedAt)}`
    : formatDate(item.updatedAt || item.createdAt)
  const relatedBlock = type === 'note' ? renderRelatedBlock(item) : ''

  return `
    <div class="item-card ${type === 'note' ? `item-card-note status-${normalizeStatus(item.status)}` : ''}" data-type="${type}" data-id="${item.id}" data-copyable="${copyable}">
      <div class="item-header">
        <div class="item-main">
          <span class="item-title">${title}</span>
          ${priority}
          ${category}
        </div>
        <div class="item-side">
          ${statusSwitch}
          <span class="item-date">${dateText}</span>
        </div>
      </div>
      <div class="item-content">${preview}</div>
      ${relatedBlock}
      <div class="item-actions">
        <button class="btn-action" data-action="edit-item" data-type="${type}" data-id="${item.id}">编辑</button>
        <button class="btn-action" data-action="copy-item" data-type="${type}" data-id="${item.id}">复制</button>
        <button class="btn-action delete" data-action="soft-delete" data-type="${type}" data-id="${item.id}">删除</button>
      </div>
    </div>
  `
}

function renderTrashCard(item) {
  const typeLabel = item._type === 'prompt' ? 'Prompt' : '消息'
  const title = escapeHtml(item.title || '无标题')
  const category = item.category ? `<span class="badge badge-category">${escapeHtml(item.category)}</span>` : ''
  const priority = item._type === 'note' ? renderPriorityBadge(item.priority) : ''
  const preview = escapeHtml(item.content || '')
  const relatedBlock = item._type === 'note' ? renderRelatedBlock(item) : ''

  return `
    <div class="item-card trash-card" data-type="${item._type}" data-id="${item.id}">
      <div class="item-header">
        <div class="item-main">
          <span class="item-title">${title}</span>
          <span class="badge badge-type">${typeLabel}</span>
          ${priority}
          ${category}
        </div>
        <span class="item-date">删除于 ${formatDate(item.deletedAt)}</span>
      </div>
      <div class="item-content">${preview}</div>
      ${relatedBlock}
      <div class="item-actions item-actions-visible">
        <button class="btn-action" data-action="restore-item" data-type="${item._type}" data-id="${item.id}">恢复</button>
        <button class="btn-action delete" data-action="purge-item" data-type="${item._type}" data-id="${item.id}">彻底删除</button>
      </div>
    </div>
  `
}

function updateCount(elementId, filtered, total) {
  const el = document.getElementById(elementId)
  if (!el) return
  el.textContent = filtered === total ? `${total} 条` : `${filtered} / ${total} 条`
}

function clearSearch(target) {
  const input = document.getElementById(`${target}-search`)
  if (input) input.value = ''
  state.searches[target] = ''

  if (target === 'note') {
    state.noteStatusFilter = 'todo'
    state.notePriorityFilter = 'all'
    document.getElementById('note-status-filter').value = 'todo'
    document.getElementById('note-priority-filter').value = 'all'
  }

  if (target === 'prompt') renderPrompts()
  if (target === 'note') renderNotes()
  if (target === 'trash') renderTrash()
}

function togglePriorityField(type) {
  const isNote = type === 'note'
  document.getElementById('priority-field-group').classList.toggle('hidden', !isNote)
}

function openEditor(type, id = '') {
  const item = id ? findItem(type, id) : null
  const isPrompt = type === 'prompt'

  document.getElementById('modal-title').textContent = `${id ? '编辑' : '新增'}${isPrompt ? ' Prompt' : '消息'}`
  document.getElementById('edit-id').value = item?.id || ''
  document.getElementById('edit-type').value = type
  document.getElementById('edit-title').value = item?.title || ''
  document.getElementById('edit-category').value = item?.category || ''
  document.getElementById('edit-priority').value = normalizePriority(item?.priority)
  document.getElementById('edit-content').value = item?.content || ''
  togglePriorityField(type)
  document.getElementById('modal').classList.add('show')
  document.getElementById('edit-content').focus()
}

function closeModal() {
  document.getElementById('modal').classList.remove('show')
}

async function saveEdit() {
  const id = document.getElementById('edit-id').value.trim()
  const type = document.getElementById('edit-type').value
  const title = document.getElementById('edit-title').value.trim()
  const category = document.getElementById('edit-category').value.trim()
  const content = document.getElementById('edit-content').value.trim()
  const priority = normalizePriority(document.getElementById('edit-priority').value)

  if (!content) {
    alert('内容不能为空')
    return
  }

  const payload = {
    id: id || undefined,
    title,
    category,
    content
  }

  if (type === 'prompt') {
    state.prompts = await window.api.savePrompt(payload)
  } else {
    const original = id ? findItem('note', id) : null
    state.notes = await window.api.saveNote({
      ...payload,
      priority,
      status: normalizeStatus(original?.status),
      relatedItems: normalizeRelatedItems(original?.relatedItems),
      completedAt: original?.completedAt || null
    })
  }

  closeModal()
  renderAll()
}

function requestDelete(type, id, mode) {
  const item = findItem(type, id)
  if (!item) return

  state.deleteTarget = {
    id,
    type,
    mode,
    focusSelector: `#${type}-search`
  }

  const isSoftDelete = mode === 'soft'
  document.getElementById('delete-modal-title').textContent = isSoftDelete ? '移入垃圾站' : '彻底删除'
  document.getElementById('delete-message').textContent = isSoftDelete
    ? `确定把这条${type === 'prompt' ? ' Prompt' : '消息'}移入垃圾站吗？`
    : '确定彻底删除这条记录吗？'
  document.getElementById('delete-hint').textContent = isSoftDelete
    ? '删除后仍可在垃圾站恢复'
    : '彻底删除后将无法恢复'
  document.getElementById('delete-confirm-btn').textContent = isSoftDelete ? '移入垃圾站' : '彻底删除'
  document.getElementById('delete-modal').classList.add('show')
}

function closeDeleteModal() {
  document.getElementById('delete-modal').classList.remove('show')
  state.deleteTarget = null
}

async function confirmDelete() {
  const target = state.deleteTarget
  if (!target) return

  const { type, id, mode, focusSelector } = target

  if (mode === 'soft') {
    if (type === 'prompt') {
      state.prompts = await window.api.deletePrompt(id)
    } else {
      state.notes = await window.api.deleteNote(id)
    }
    showHint('已移入垃圾站')
  } else {
    if (type === 'prompt') {
      state.prompts = await window.api.purgePrompt(id)
    } else {
      state.notes = await window.api.purgeNote(id)
    }
    showHint('已彻底删除')
  }

  closeDeleteModal()
  renderAll()

  const input = document.querySelector(focusSelector)
  if (input && state.activeTab !== 'trash') {
    input.focus()
  }
}

async function restoreItem(type, id) {
  if (type === 'prompt') {
    state.prompts = await window.api.restorePrompt(id)
  } else {
    state.notes = await window.api.restoreNote(id)
  }

  renderAll()
  showHint('已恢复')
}

function addRelatedInput(value = '') {
  const list = document.getElementById('related-items-list')
  const row = document.createElement('div')
  row.className = 'related-item-row'
  row.innerHTML = `
    <textarea class="related-item-input" rows="3" placeholder="补充一条关联内容，例如完成说明、链接、结论...">${escapeTextarea(value)}</textarea>
    <button class="btn-action delete" data-action="remove-related-item">移除</button>
  `
  list.appendChild(row)
}

function removeRelatedInput(row) {
  if (!row) return
  const list = document.getElementById('related-items-list')
  if (list.children.length === 1) {
    row.querySelector('.related-item-input').value = ''
    return
  }
  row.remove()
}

function getRelatedInputs() {
  return Array.from(document.querySelectorAll('.related-item-input'))
    .map(input => input.value.trim())
    .filter(Boolean)
}

function openCompletionModal(id) {
  const note = findItem('note', id)
  if (!note) return

  state.completionTargetId = id
  document.getElementById('completion-note-id').value = id
  document.getElementById('completion-title').value = note.title || ''
  document.getElementById('completion-category').value = note.category || ''
  document.getElementById('completion-priority').value = normalizePriority(note.priority)
  document.getElementById('completion-content').value = note.content || ''

  const list = document.getElementById('related-items-list')
  list.innerHTML = ''
  const relatedItems = normalizeRelatedItems(note.relatedItems)
  if (relatedItems.length) {
    relatedItems.forEach(item => addRelatedInput(item))
  } else {
    addRelatedInput('')
  }

  document.getElementById('completion-modal').classList.add('show')
  document.getElementById('completion-content').focus()
}

function closeCompletionModal() {
  document.getElementById('completion-modal').classList.remove('show')
  state.completionTargetId = null
  renderAll()
}

async function confirmCompletion() {
  const id = document.getElementById('completion-note-id').value
  const note = findItem('note', id)
  if (!note) return

  const title = document.getElementById('completion-title').value.trim()
  const category = document.getElementById('completion-category').value.trim()
  const priority = normalizePriority(document.getElementById('completion-priority').value)
  const content = document.getElementById('completion-content').value.trim()
  const relatedItems = getRelatedInputs()

  if (!content) {
    alert('内容不能为空')
    return
  }

  state.notes = await window.api.saveNote({
    ...note,
    id,
    title,
    category,
    priority,
    content,
    status: 'done',
    relatedItems,
    completedAt: new Date().toISOString()
  })

  closeCompletionModal()
  renderAll()
  showHint('已归档到已完成')
}

async function handleNoteStatusToggle(id) {
  const note = findItem('note', id)
  if (!note) return

  if (normalizeStatus(note.status) === 'todo') {
    openCompletionModal(id)
    return
  }

  state.notes = await window.api.saveNote({
    ...note,
    id,
    status: 'todo',
    completedAt: null
  })
  renderAll()
  showHint('已恢复为未开始')
}

function copyItem(type, id) {
  const item = findItem(type, id)
  if (!item) return
  navigator.clipboard.writeText(item.content || '').then(() => {
    showHint('已复制到剪贴板')
  })
}

async function openDataDir() {
  const result = await window.api.openDataDir()
  if (result.success) {
    showHint('已打开数据目录')
  } else {
    alert(`打开失败: ${result.error || '未知错误'}`)
  }
}

function showHint(message) {
  const hint = document.createElement('div')
  hint.className = 'toast'
  hint.textContent = message
  document.body.appendChild(hint)
  setTimeout(() => hint.remove(), 1600)
}

function escapeHtml(text) {
  return (text || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
    .replace(/\n/g, '<br>')
}

function escapeTextarea(text) {
  return (text || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

function formatDate(isoString) {
  if (!isoString) return ''

  const date = new Date(isoString)
  if (Number.isNaN(date.getTime())) return ''

  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`

  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function loadConfig() {
  const displayShortcut = formatShortcut(state.config.shortcut)
  document.getElementById('shortcut-input').value = displayShortcut
  document.getElementById('shortcut-input').dataset.shortcut = ''
  document.getElementById('shortcut-hint').textContent = `${displayShortcut} 呼出/隐藏 | Esc 隐藏`
  document.getElementById('auto-launch-toggle').checked = Boolean(state.config.autoLaunch)
}

function loadSettings() {
  document.getElementById('data-dir-input').value = state.dataDir
  document.getElementById('note-status-filter').value = state.noteStatusFilter
  document.getElementById('note-priority-filter').value = state.notePriorityFilter
}

function formatShortcut(shortcut = '') {
  return shortcut
    .replace(/CommandOrControl\+/g, 'Ctrl+')
    .replace(/Alt\+/g, 'Alt+')
    .replace(/Shift\+/g, 'Shift+')
}

function captureShortcut() {
  if (state.isCapturingShortcut) {
    stopCapturingShortcut()
    return
  }

  state.isCapturingShortcut = true

  const input = document.getElementById('shortcut-input')
  input.value = 'Recording...'
  input.style.borderColor = '#4fc3f7'
  input.focus()

  showHint('按下新的快捷键组合，Esc 取消')

  if (state.shortcutHandler) {
    document.removeEventListener('keydown', state.shortcutHandler)
  }

  state.shortcutHandler = (e) => {
    if (e.key === 'Escape') {
      stopCapturingShortcut()
      return
    }

    e.preventDefault()
    e.stopPropagation()

    const keys = []
    if (e.ctrlKey) keys.push('CommandOrControl')
    if (e.altKey) keys.push('Alt')
    if (e.shiftKey) keys.push('Shift')

    const mainKey = e.key.toUpperCase()
    const isModifier = ['CONTROL', 'ALT', 'SHIFT', 'META'].includes(mainKey)

    if (!isModifier && keys.length >= 1) {
      let key = mainKey
      if (key === ' ') key = 'Space'
      if (key === 'ARROWUP') key = 'Up'
      if (key === 'ARROWDOWN') key = 'Down'
      if (key === 'ARROWLEFT') key = 'Left'
      if (key === 'ARROWRIGHT') key = 'Right'

      keys.push(key)
      const shortcut = keys.join('+')
      input.value = formatShortcut(shortcut)
      input.dataset.shortcut = shortcut
      input.style.borderColor = '#0f3460'
      stopCapturingShortcut(false)
      showHint(`快捷键已录制为 ${formatShortcut(shortcut)}`)
    } else if (!isModifier) {
      showHint('请至少使用一个修饰键 + 主键')
    } else {
      const displayKeys = keys.map(key => key === 'CommandOrControl' ? 'Ctrl' : key)
      input.value = `${displayKeys.join(' + ')} + ?`
    }
  }

  document.addEventListener('keydown', state.shortcutHandler)
}

function stopCapturingShortcut(resetValue = true) {
  if (!state.isCapturingShortcut) return

  state.isCapturingShortcut = false

  if (state.shortcutHandler) {
    document.removeEventListener('keydown', state.shortcutHandler)
    state.shortcutHandler = null
  }

  const input = document.getElementById('shortcut-input')
  input.style.borderColor = '#0f3460'

  if (resetValue && !input.dataset.shortcut) {
    input.value = formatShortcut(state.config.shortcut)
  }
}

async function saveShortcut() {
  const input = document.getElementById('shortcut-input')
  const shortcut = input.dataset.shortcut || state.config.shortcut

  const result = await window.api.updateShortcut(shortcut)
  if (!result.success) {
    alert('快捷键更新失败，可能与其他软件冲突')
    return
  }

  state.config.shortcut = shortcut
  input.dataset.shortcut = ''
  loadConfig()
  showHint('快捷键已更新')
}

async function toggleAutoLaunch(e) {
  const enable = e.target.checked
  const result = await window.api.toggleAutoLaunch(enable)

  if (!result.success) {
    e.target.checked = !enable
    alert('设置失败')
    return
  }

  state.config.autoLaunch = enable
  showHint(enable ? '已开启开机自启' : '已关闭开机自启')
}

init()
