import { useState } from 'react'
import WeekCard from './WeekCard'
import MenuTab from './MenuTab'
import { useHistory, useWeekDetail } from '../hooks/useMenu'

function WeekDetailView({ weekId, onBack }) {
  const { data: week, isLoading } = useWeekDetail(weekId)

  return (
    <div>
      <button
        onClick={onBack}
        className="flex items-center gap-1 px-4 pt-5 pb-1 text-orange-500 text-sm font-medium"
      >
        ‹ 返回
      </button>
      {isLoading ? (
        <div className="text-center py-12 text-gray-400">加载中…</div>
      ) : (
        <MenuTab weekData={week} readOnly />
      )}
    </div>
  )
}

export default function HistoryTab() {
  const { data: history = [], isLoading } = useHistory()
  const [selectedId, setSelectedId] = useState(null)

  if (selectedId) {
    return <WeekDetailView weekId={selectedId} onBack={() => setSelectedId(null)} />
  }

  return (
    <div className="px-4 pt-5">
      <h1 className="text-xl font-bold text-gray-900 mb-4">历史菜单</h1>

      {isLoading && <div className="text-center py-12 text-gray-400">加载中…</div>}

      {!isLoading && history.length === 0 && (
        <div className="text-center py-16 text-gray-400">还没有历史记录</div>
      )}

      <div className="space-y-2">
        {history.map((week) => (
          <WeekCard key={week.id} week={week} onClick={() => setSelectedId(week.id)} />
        ))}
      </div>
    </div>
  )
}
