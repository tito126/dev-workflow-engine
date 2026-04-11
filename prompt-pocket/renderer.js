const PRIORITY_META = {
  urgent: { label: '紧急', weight: 4, className: 'badge-priority-urgent' },
  high: { label: '高', weight: 3, className: 'badge-priority-high' },
  medium: { label: '中', weight: 2, className: 'badge-priority-medium' },
  low: { label: '低', weight: 1, className: 'badge-priority-low' }
}

const state = {
  prompts: [],
  notes: [],
  config: {},
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
  notePriorityFilter: 'all',
  trashType: 'all',
  deleteTarget: null,
  isCapturingShortcut: false,
  shortcutHandler: null
}

async function init() {
  state.prompts = await window.api.getPrompts()
  state.notes = await window.api.getNotes()
  state.config = await window.api.getConfig()

  bindEvents()
  loadConfig()
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
    if (action === 'close-delete-modal') return closeDeleteModal()
    if (action === 'confirm-delete') return confirmDelete()

    const type = actionEl.dataset.type
    const id = actionEl.dataset.id

    if (action === 'edit-item') return openEditor(type, id)
    if (action === 'copy-item') return copyItem(type, id)
    if (action === 'soft-delete') return requestDelete(type, id, 'soft')
    if (action === 'restore-item') return restoreItem(type, id)
    if (action === 'purge-item') return requestDelete(type, id, 'purge')

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

function getPriorityMeta(priority) {
  return PRIORITY_META[normalizePriority(priority)]
}

function getPriorityWeight(priority) {
  return getPriorityMeta(priority).weight
}

function matchesFilter(item, keyword) {
  const q = normalizeText(keyword)
  if (!q) return true
  return [item.title, item.category, item.content].some(field => normalizeText(field).includes(q))
}

function matchesNotePriority(item, filterValue) {
  if (filterValue === 'all') return true
  return normalizePriority(item.priority) === filterValue
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
  const items = sortItems(
    getActiveItems('note')
      .filter(item => matchesFilter(item, state.searches.note))
      .filter(item => matchesNotePriority(item, state.notePriorityFilter)),
    state.sorts.note
  )

  renderItemList({
    containerId: 'notes-list',
    type: 'note',
    items,
    emptyText: state.searches.note || state.notePriorityFilter !== 'all' ? '没有匹配的消息' : '暂无消息，点击“新增”添加',
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
  const total = [...deletedPrompts, ...deletedNotes].filter(item => {
    return state.trashType === 'all' || item._type === state.trashType
  }).length

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

function renderItemCard(type, item, copyable) {
  const title = escapeHtml(item.title || '无标题')
  const category = item.category ? `<span class="badge badge-category">${escapeHtml(item.category)}</span>` : ''
  const priority = type === 'note' ? renderPriorityBadge(item.priority) : ''
  const preview = escapeHtml(item.content || '')
  const dateText = formatDate(item.updatedAt || item.createdAt)

  return `
    <div class="item-card" data-type="${type}" data-id="${item.id}" data-copyable="${copyable}">
      <div class="item-header">
        <div class="item-main">
          <span class="item-title">${title}</span>
          ${priority}
          ${category}
        </div>
        <span class="item-date">${dateText}</span>
      </div>
      <div class="item-content">${preview}</div>
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
    state.notePriorityFilter = 'all'
    document.getElementById('note-priority-filter').value = 'all'
  }

  if (target === 'prompt') renderPrompts()
  if (target === 'note') renderNotes()
  if (target === 'trash') renderTrash()
}

function togglePriorityField(type) {
  const isNote = type === 'note'
  const group = document.getElementById('priority-field-group')
  group.classList.toggle('hidden', !isNote)
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
    state.notes = await window.api.saveNote({ ...payload, priority })
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

function copyItem(type, id) {
  const item = findItem(type, id)
  if (!item) return
  navigator.clipboard.writeText(item.content || '').then(() => {
    showHint('已复制到剪贴板')
  })
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
