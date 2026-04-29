function formatDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00')
  return `${d.getMonth() + 1}/${d.getDate()} 那周`
}

export default function WeekCard({ week, onClick }) {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center justify-between px-4 py-3 bg-white rounded-xl border border-gray-100 active:bg-gray-50 text-left"
    >
      <div>
        <div className="font-medium text-gray-900">{formatDate(week.week_start)}</div>
        <div className="text-xs text-gray-400 mt-0.5">
          {week.dish_count} 道菜
          {week.generated_at &&
            ` · 生成于 ${new Date(week.generated_at).toLocaleDateString('zh-CN')}`}
        </div>
      </div>
      <span className="text-gray-300 text-lg">›</span>
    </button>
  )
}
