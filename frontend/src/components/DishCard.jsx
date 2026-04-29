import { useState } from 'react'
import RecipeDrawer from './RecipeDrawer'
import { useRegenDish } from '../hooks/useMenu'

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
  const regen = useRegenDish()

  if (!dish) return null

  const handleRegen = (e) => {
    e.stopPropagation()
    regen.mutate({ mealId, dish_slot: slot })
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
          <button
            onClick={handleRegen}
            disabled={regen.isPending}
            className="ml-3 text-gray-400 hover:text-orange-500 transition-colors disabled:opacity-40 text-lg"
            title="重新生成"
          >
            {regen.isPending ? '⏳' : '↺'}
          </button>
        )}
      </div>

      {open && <RecipeDrawer dish={dish} onClose={() => setOpen(false)} />}
    </>
  )
}
