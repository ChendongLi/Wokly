import { useState } from 'react'
import { useHealth } from '../hooks/useMenu'

export default function Settings() {
  const { data, isLoading, isError } = useHealth()
  const [lang, setLang] = useState('zh')

  const statusColor = isLoading ? 'bg-gray-300' : isError ? 'bg-red-400' : 'bg-green-400'
  const statusText = isLoading ? '检测中…' : isError ? '无法连接' : '已连接'

  return (
    <div className="px-4 pt-5">
      <h1 className="text-xl font-bold text-gray-900 mb-6">设置</h1>

      {/* Backend status */}
      <div className="bg-white rounded-xl border border-gray-100 px-4 py-4 mb-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-700">后端连接状态</span>
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${statusColor}`} />
            <span className="text-sm text-gray-500">{statusText}</span>
          </div>
        </div>
      </div>

      {/* Language toggle */}
      <div className="bg-white rounded-xl border border-gray-100 px-4 py-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-700">界面语言</span>
          <div className="flex rounded-lg overflow-hidden border border-gray-200 text-sm">
            <button
              onClick={() => setLang('zh')}
              className={`px-3 py-1.5 transition-colors ${lang === 'zh' ? 'bg-orange-500 text-white' : 'text-gray-500'}`}
            >
              中文
            </button>
            <button
              onClick={() => setLang('en')}
              className={`px-3 py-1.5 transition-colors ${lang === 'en' ? 'bg-orange-500 text-white' : 'text-gray-500'}`}
            >
              English
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
