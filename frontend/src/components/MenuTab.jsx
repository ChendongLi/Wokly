import { useState } from 'react'
import DayNav from './DayNav'
import DishCard from './DishCard'
import { useCurrentWeek, useTriggerGenerate } from '../hooks/useMenu'

function MealSection({ title, meal, readOnly }) {
  const [wfhOn, setWfhOn] = useState(false)

  if (!meal) return null

  const isLunch = meal.meal_type === 'lunch'

  return (
    <section className="mb-4">
      <div className="flex items-center justify-between px-4 mb-2">
        <h3 className="font-semibold text-gray-700">{title}</h3>
        {isLunch && (
          <label className="flex items-center gap-1.5 text-xs text-gray-500 cursor-pointer">
            <span>太太在家</span>
            <div
              onClick={() => setWfhOn((v) => !v)}
              className={`w-9 h-5 rounded-full relative transition-colors cursor-pointer ${wfhOn ? 'bg-orange-400' : 'bg-gray-200'}`}
            >
              <span
                className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${wfhOn ? 'translate-x-4' : 'translate-x-0.5'}`}
              />
            </div>
          </label>
        )}
      </div>

      <div className="px-4 space-y-2">
        <DishCard dish={meal.dish1} mealId={meal.id} slot="dish1" readOnly={readOnly} />
        <DishCard dish={meal.dish2} mealId={meal.id} slot="dish2" readOnly={readOnly} />
        {isLunch && wfhOn && meal.optional_dish && (
          <DishCard
            dish={meal.optional_dish}
            mealId={meal.id}
            slot="optional_dish"
            readOnly={readOnly}
          />
        )}
        {!isLunch && meal.soup && (
          <DishCard dish={meal.soup} mealId={meal.id} slot="soup" readOnly={readOnly} />
        )}
      </div>
    </section>
  )
}

export default function MenuTab({ weekData, readOnly = false }) {
  const [selectedDay, setSelectedDay] = useState('周一')
  const { data: currentWeek, isLoading } = useCurrentWeek()
  const generate = useTriggerGenerate()

  const week = weekData || currentWeek

  const dayMeals = week?.meals?.filter((m) => m.day === selectedDay) || []
  const lunch = dayMeals.find((m) => m.meal_type === 'lunch')
  const dinner = dayMeals.find((m) => m.meal_type === 'dinner')

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between px-4 pt-5 pb-1">
        <h1 className="text-xl font-bold text-gray-900">本周菜单</h1>
        {!readOnly && (
          <button
            onClick={() => generate.mutate()}
            disabled={generate.isPending}
            className="text-sm px-3 py-1.5 rounded-lg bg-orange-500 text-white font-medium disabled:opacity-50"
          >
            {generate.isPending ? '生成中…' : '生成菜单'}
          </button>
        )}
      </div>

      <DayNav selected={selectedDay} onChange={setSelectedDay} />

      {isLoading && <div className="text-center py-12 text-gray-400">加载中…</div>}

      {!isLoading && !week && (
        <div className="text-center py-16 px-8">
          <p className="text-gray-400 mb-4">本周菜单还没生成</p>
          {!readOnly && (
            <button
              onClick={() => generate.mutate()}
              disabled={generate.isPending}
              className="px-6 py-3 rounded-xl bg-orange-500 text-white font-semibold"
            >
              {generate.isPending ? '生成中…' : '立即生成'}
            </button>
          )}
        </div>
      )}

      {week && (
        <>
          <MealSection title="午餐" meal={lunch} readOnly={readOnly} />
          <MealSection title="晚餐" meal={dinner} readOnly={readOnly} />
        </>
      )}
    </div>
  )
}
