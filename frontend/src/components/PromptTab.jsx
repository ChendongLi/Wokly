import { useState, useEffect } from 'react'
import { useGetPrompt, useUpdatePrompt, useResetPrompt } from '../hooks/useMenu'

export default function PromptTab() {
  const { data, isLoading } = useGetPrompt()
  const updatePrompt = useUpdatePrompt()
  const resetPrompt = useResetPrompt()
  const [text, setText] = useState('')
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    if (data?.content !== undefined) {
      setText(data.content)
    }
  }, [data?.content])

  const handleSave = () => {
    updatePrompt.mutate(text, {
      onSuccess: () => {
        setSaved(true)
        setTimeout(() => setSaved(false), 2000)
      },
    })
  }

  const handleReset = () => {
    resetPrompt.mutate(undefined, {
      onSuccess: (result) => {
        setText(result.content)
      },
    })
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-4 pt-5 pb-3">
        <h1 className="text-xl font-bold text-gray-900">提示词设置</h1>
        <p className="text-xs text-gray-400 mt-0.5">自定义 AI 生成菜单时使用的指令</p>
        {data?.is_custom && (
          <span className="inline-block mt-1.5 text-xs px-2 py-0.5 bg-orange-100 text-orange-600 rounded-full">
            已自定义
          </span>
        )}
      </div>

      {/* Textarea */}
      <div className="flex-1 px-4 pb-2">
        {isLoading ? (
          <div className="text-center py-12 text-gray-400">加载中…</div>
        ) : (
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            className="w-full h-full min-h-64 text-sm font-mono text-gray-800 border border-gray-200 rounded-xl p-3 focus:outline-none focus:border-orange-400 resize-none leading-relaxed"
            spellCheck={false}
          />
        )}
      </div>

      {/* Action buttons */}
      <div className="px-4 pb-6 pt-2 flex gap-3">
        <button
          onClick={handleReset}
          disabled={resetPrompt.isPending || !data?.is_custom}
          className="flex-1 py-2.5 rounded-xl border border-gray-200 text-sm text-gray-500 disabled:opacity-40"
        >
          重置默认
        </button>
        <button
          onClick={handleSave}
          disabled={updatePrompt.isPending || isLoading}
          className="flex-1 py-2.5 rounded-xl bg-orange-500 text-white text-sm font-semibold disabled:opacity-50"
        >
          {saved ? '已保存 ✓' : updatePrompt.isPending ? '保存中…' : '保存'}
        </button>
      </div>
    </div>
  )
}
