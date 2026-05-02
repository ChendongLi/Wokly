import { useState } from 'react'
import RecipeDrawer from './RecipeDrawer'
import { useFillDish, useRegenDish, useUpdateMeal } from '../hooks/useMenu'

const TAG_LABELS = { meat: '荤', veg: '素', soup: '汤', opt: '选' }
const TAG_COLORS = {
  meat: 'bg-red-100 text-red-700',
  veg: 'bg-green-100 text-green-700',
  soup: 'bg-blue-100 text-blue-700',
  opt: 'bg-purple-100 text-purple-700',
}

function Stars({ diff }) {
  return <span className="text-yellow-400 text-sm">{'⭐'.repeat(diff)}</span>
}

export default function DishCard({ dish, mealId, slot, readOnly = false }) {
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState(false)
  const [editName, setEditName] = useState('')
  const [editUrl, setEditUrl] = useState('')
  const regen = useRegenDish()
  const updateMeal = useUpdateMeal()
  const fillDish = useFillDish()

  if (!dish) return null

  const handleRegen = (e) => {
    e.stopPropagation()
    regen.mutate({ mealId, dish_slot: slot })
  }

  const startEdit = (e) => {
    e.stopPropagation()
    setEditName(dish.name)
    setEditUrl(dish.url || '')
    setEditing(true)
  }

  const cancelEdit = (e) => {
    e?.stopPropagation()
    setEditing(false)
  }

  const saveEdit = (e) => {
    e?.stopPropagation()
    const trimmedName = editName.trim()
    if (!trimmedName) return
    const trimmedUrl = editUrl.trim() || undefined
    if (trimmedName !== dish.name) {
      fillDish.mutate(
        { mealId, dish_slot: slot, name: trimmedName, url: trimmedUrl },
        { onSuccess: () => setEditing(false) }
      )
    } else {
      updateMeal.mutate(
        { mealId, dish_slot: slot, dish: { ...dish, name: trimmedName, url: trimmedUrl } },
        { onSuccess: () => setEditing(false) }
      )
    }
  }

  if (editing) {
    return (
      <div className="px-4 py-3 bg-white rounded-xl border border-orange-300 space-y-2">
        <input
          autoFocus
          value={editName}
          onChange={(e) => setEditName(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') saveEdit()
            if (e.key === 'Escape') cancelEdit()
          }}
          placeholder="菜名"
          className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-orange-400"
        />
        <input
          value={editUrl}
          onChange={(e) => setEditUrl(e.target.value)}
          placeholder="食谱链接（可选）"
          className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-orange-400"
        />
        <div className="flex gap-2 pt-1">
          <button
            onClick={cancelEdit}
            className="flex-1 py-1.5 rounded-lg border border-gray-200 text-sm text-gray-500"
          >
            取消
          </button>
          <button
            onClick={saveEdit}
            disabled={updateMeal.isPending || fillDish.isPending}
            className="flex-1 py-1.5 rounded-lg bg-orange-500 text-white text-sm font-medium disabled:opacity-50"
          >
            {updateMeal.isPending || fillDish.isPending ? '保存中…' : '保存'}
          </button>
        </div>
      </div>
    )
  }

  return (
    <>
      <div
        className="flex items-center justify-between px-4 py-3 bg-white rounded-xl border border-gray-100 active:bg-gray-50 cursor-pointer"
        onClick={() => setOpen(true)}
      >
        <div className="flex-1 min-w-0">
          <div className="font-medium text-gray-900 truncate">{dish.name}</div>
          <div className="flex items-center gap-1.5 mt-0.5">
            <Stars diff={dish.diff} />
            <span
              className={`text-xs px-1.5 py-0.5 rounded-full font-medium ${TAG_COLORS[dish.tag] || ''}`}
            >
              {TAG_LABELS[dish.tag] || dish.tag}
            </span>
            <span className="text-xs text-gray-400">{dish.style}</span>
          </div>
        </div>

        {!readOnly && (
          <div className="flex items-center gap-1 ml-3">
            <button
              onClick={startEdit}
              className="text-gray-400 hover:text-orange-500 transition-colors text-base px-1"
              title="编辑"
            >
              ✎
            </button>
            <button
              onClick={handleRegen}
              disabled={regen.isPending}
              className="text-gray-400 hover:text-orange-500 transition-colors disabled:opacity-40 text-lg"
              title="重新生成"
            >
              {regen.isPending ? '⏳' : '↺'}
            </button>
          </div>
        )}
      </div>

      {open && <RecipeDrawer dish={dish} onClose={() => setOpen(false)} />}
    </>
  )
}
