import { useEffect } from 'react'

const TAG_LABELS = { meat: '荤', veg: '素', soup: '汤', opt: '选' }
const TAG_COLORS = {
  meat: 'bg-red-100 text-red-700',
  veg: 'bg-green-100 text-green-700',
  soup: 'bg-blue-100 text-blue-700',
  opt: 'bg-purple-100 text-purple-700',
}

function Stars({ diff }) {
  return <span className="text-yellow-400">{'⭐'.repeat(diff)}</span>
}

export default function RecipeDrawer({ dish, onClose }) {
  useEffect(() => {
    const handleKey = (e) => e.key === 'Escape' && onClose()
    document.addEventListener('keydown', handleKey)
    return () => document.removeEventListener('keydown', handleKey)
  }, [onClose])

  if (!dish) return null

  const keyword = encodeURIComponent(dish.search_query || dish.name)
  const xhsUrl = `https://oia.xiaohongshu.com/oia?deeplink=xhsdiscover%3A%2F%2Fsearch%2Fresult%3Fkeyword%3D${keyword}`
  const ytUrl = `https://www.youtube.com/results?search_query=${encodeURIComponent((dish.search_query || dish.name) + ' 做法')}`

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/40 z-20" onClick={onClose} />

      {/* Sheet */}
      <div className="fixed bottom-0 left-0 right-0 max-w-lg mx-auto bg-white rounded-t-2xl z-30 max-h-[85vh] flex flex-col">
        {/* Handle */}
        <div className="flex justify-center pt-3 pb-1">
          <div className="w-10 h-1 bg-gray-300 rounded-full" />
        </div>

        <div className="overflow-y-auto px-5 pb-8">
          {/* Header */}
          <div className="flex items-start justify-between mt-2 mb-4">
            <div>
              <h2 className="text-xl font-bold text-gray-900">{dish.name}</h2>
              <div className="flex items-center gap-2 mt-1">
                <Stars diff={dish.diff} />
                <span
                  className={`text-xs px-2 py-0.5 rounded-full font-medium ${TAG_COLORS[dish.tag] || ''}`}
                >
                  {TAG_LABELS[dish.tag] || dish.tag}
                </span>
                <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
                  {dish.style}
                </span>
              </div>
            </div>
            <button onClick={onClose} className="text-gray-400 text-2xl leading-none ml-4">
              ×
            </button>
          </div>

          {/* Ingredients */}
          <section className="mb-4">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-1">
              食材
            </h3>
            <p className="text-gray-800 text-sm leading-relaxed">{dish.ingredients}</p>
          </section>

          {/* Steps */}
          <section className="mb-5">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
              步骤
            </h3>
            <ol className="space-y-2">
              {(dish.steps || []).map((step, i) => (
                <li key={i} className="flex gap-3 text-sm text-gray-800">
                  <span className="flex-shrink-0 w-5 h-5 rounded-full bg-orange-100 text-orange-600 text-xs font-bold flex items-center justify-center mt-0.5">
                    {i + 1}
                  </span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>
          </section>

          {/* Search links */}
          <section className="flex gap-3">
            <a
              href={xhsUrl}
              target="_blank"
              rel="noreferrer"
              className="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl bg-red-50 text-red-600 text-sm font-medium"
            >
              📕 小红书
            </a>
            <a
              href={ytUrl}
              target="_blank"
              rel="noreferrer"
              className="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl bg-gray-100 text-gray-700 text-sm font-medium"
            >
              ▶️ YouTube
            </a>
            {dish.url && (
              <a
                href={dish.url}
                target="_blank"
                rel="noreferrer"
                className="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl bg-orange-50 text-orange-600 text-sm font-medium"
              >
                🌐 食谱
              </a>
            )}
          </section>
        </div>
      </div>
    </>
  )
}
