import { useState } from 'react'
import { useHealth, useCurrentWeek, useDeleteWeek } from '../hooks/useMenu'

function ConfirmDeleteModal({ weekStart, onConfirm, onCancel, isPending }) {
  const [input, setInput] = useState('')
  const ready = input === '删除'

  return (
    <>
      <div className="fixed inset-0 bg-black/50 z-40" onClick={onCancel} />
      <div className="fixed inset-x-4 top-1/2 -translate-y-1/2 max-w-sm mx-auto bg-white rounded-2xl z-50 p-5 shadow-xl">
        <h2 className="text-base font-bold text-gray-900 mb-1">删除菜单</h2>
        <p className="text-sm text-gray-500 mb-4">
          将删除 <span className="font-medium text-gray-700">{weekStart}</span>{' '}
          那周的全部菜单和购物清单，无法撤销。
        </p>
        <p className="text-xs text-gray-400 mb-2">
          请输入 <span className="font-mono font-bold text-red-500">删除</span> 以确认
        </p>
        <input
          autoFocus
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="删除"
          className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-red-400 mb-4"
        />
        <div className="flex gap-2">
          <button
            onClick={onCancel}
            className="flex-1 py-2 rounded-xl border border-gray-200 text-sm text-gray-500"
          >
            取消
          </button>
          <button
            onClick={onConfirm}
            disabled={!ready || isPending}
            className="flex-1 py-2 rounded-xl bg-red-500 text-white text-sm font-semibold disabled:opacity-40"
          >
            {isPending ? '删除中…' : '确认删除'}
          </button>
        </div>
      </div>
    </>
  )
}

function formatWeekStart(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr + 'T00:00:00')
  return `${d.getMonth() + 1}月${d.getDate()}日`
}

export default function Settings() {
  const { data: health, isLoading: healthLoading, isError } = useHealth()
  const { data: currentWeek } = useCurrentWeek()
  const deleteWeek = useDeleteWeek()
  const [lang, setLang] = useState('zh')
  const [showModal, setShowModal] = useState(false)
  const [targetWeek, setTargetWeek] = useState(null)

  const statusColor = healthLoading ? 'bg-gray-300' : isError ? 'bg-red-400' : 'bg-green-400'
  const statusText = healthLoading ? '检测中…' : isError ? '无法连接' : '已连接'

  const handleDeleteClick = (week) => {
    setTargetWeek(week)
    setShowModal(true)
  }

  const handleConfirm = () => {
    if (!targetWeek) return
    deleteWeek.mutate(targetWeek.id, {
      onSuccess: () => {
        setShowModal(false)
        setTargetWeek(null)
      },
    })
  }

  return (
    <div className="px-4 pt-5 pb-8">
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
      <div className="bg-white rounded-xl border border-gray-100 px-4 py-4 mb-4">
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

      {/* Danger zone */}
      <div className="bg-white rounded-xl border border-red-100 px-4 py-4">
        <p className="text-xs font-semibold text-red-400 uppercase tracking-wide mb-3">危险操作</p>
        {currentWeek ? (
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-700">删除本周菜单</p>
              <p className="text-xs text-gray-400 mt-0.5">
                {formatWeekStart(currentWeek.week_start)}那周 · 删除后可重新生成
              </p>
            </div>
            <button
              onClick={() => handleDeleteClick(currentWeek)}
              className="ml-4 px-3 py-1.5 rounded-lg border border-red-300 text-red-500 text-sm font-medium active:scale-95 transition-transform"
            >
              删除
            </button>
          </div>
        ) : (
          <p className="text-sm text-gray-400">暂无菜单可删除</p>
        )}
      </div>

      {showModal && targetWeek && (
        <ConfirmDeleteModal
          weekStart={formatWeekStart(targetWeek.week_start)}
          onConfirm={handleConfirm}
          onCancel={() => {
            setShowModal(false)
            setTargetWeek(null)
          }}
          isPending={deleteWeek.isPending}
        />
      )}
    </div>
  )
}
