import { useState } from 'react'
import MenuTab from './components/MenuTab'
import ShopTab from './components/ShopTab'
import HistoryTab from './components/HistoryTab'
import Settings from './components/Settings'

const TABS = [
  { id: 'menu', label: '菜单', icon: '🍽️' },
  { id: 'shop', label: '购物', icon: '🛒' },
  { id: 'history', label: '历史', icon: '📅' },
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
        {activeTab === 'settings' && <Settings />}
      </main>

      {/* Bottom tab bar */}
      <nav className="fixed bottom-0 left-0 right-0 max-w-lg mx-auto bg-white border-t border-gray-200 flex z-10">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 flex flex-col items-center py-2 text-xs transition-colors ${
              activeTab === tab.id ? 'text-orange-500' : 'text-gray-400'
            }`}
          >
            <span className="text-xl leading-none mb-0.5">{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </nav>
    </div>
  )
}
