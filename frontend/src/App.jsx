import { useState } from 'react'
import MenuTab from './components/MenuTab'
import ShopTab from './components/ShopTab'
import HistoryTab from './components/HistoryTab'
import Settings from './components/Settings'
import PromptTab from './components/PromptTab'

const TABS = [
  { id: 'menu', label: '菜单', icon: '🍽️' },
  { id: 'shop', label: '购物', icon: '🛒' },
  { id: 'history', label: '历史', icon: '📅' },
  { id: 'prompt', label: '提示词', icon: '📝' },
  { id: 'settings', label: '设置', icon: '⚙️' },
]

export default function App() {
  const [activeTab, setActiveTab] = useState('menu')

  return (
    <div className="flex flex-col h-screen bg-gray-50 max-w-lg mx-auto">
      {/* Content area */}
      <main className="flex-1 overflow-y-auto pb-16">
        {activeTab === 'menu' && <MenuTab />}
        {activeTab === 'shop' && <ShopTab />}
        {activeTab === 'history' && <HistoryTab />}
        {activeTab === 'prompt' && <PromptTab />}
        {activeTab === 'settings' && <Settings />}
      </main>

      {/* Bottom tab bar */}
      <nav className="fixed bottom-0 left-0 right-0 max-w-lg mx-auto bg-white border-t border-gray-200 flex z-10">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 flex flex-col items-center pt-1 pb-2 text-xs transition-colors relative ${
              activeTab === tab.id ? 'text-orange-500' : 'text-gray-400'
            }`}
          >
            {activeTab === tab.id && (
              <span className="absolute top-0 left-1/2 -translate-x-1/2 w-6 h-0.5 rounded-full bg-orange-500" />
            )}
            <span className="text-xl leading-none mb-0.5 mt-1">{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </nav>
    </div>
  )
}
