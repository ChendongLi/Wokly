const DAYS = ['周一', '周二', '周三', '周四', '周五']

export default function DayNav({ selected, onChange }) {
  return (
    <div className="flex gap-2 overflow-x-auto px-4 py-3 scrollbar-none">
      {DAYS.map((day) => (
        <button
          key={day}
          onClick={() => onChange(day)}
          className={`flex-shrink-0 px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
            selected === day
              ? 'bg-orange-500 text-white'
              : 'bg-white text-gray-600 border border-gray-200'
          }`}
        >
          {day}
        </button>
      ))}
    </div>
  )
}
