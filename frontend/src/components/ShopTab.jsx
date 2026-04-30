import ShopItem from './ShopItem'
import { useIngredients } from '../hooks/useMenu'

export default function ShopTab() {
  const { data: ingredients = [], isLoading } = useIngredients()

  const costcoItems = ingredients.filter((i) => i.store === 'costco')
  const tntItems = ingredients.filter((i) => i.store === 'tnt')

  return (
    <div className="px-4 pt-5">
      <h1 className="text-xl font-bold text-gray-900 mb-4">购物清单</h1>

      {isLoading && <div className="text-center py-12 text-gray-400">加载中…</div>}

      {!isLoading && ingredients.length === 0 && (
        <div className="text-center py-16 text-gray-400">先生成菜单，购物清单会自动出现</div>
      )}

      {ingredients.length > 0 && (
        <div className="grid grid-cols-2 gap-4">
          {/* Costco column */}
          <div>
            <div className="flex items-center gap-1.5 mb-2">
              <span className="text-sm font-semibold text-blue-700">Costco</span>
              <span className="text-xs text-gray-400">({costcoItems.length})</span>
            </div>
            <div className="bg-white rounded-xl px-3 py-1 border border-gray-100 divide-y divide-gray-50">
              {costcoItems.length === 0 ? (
                <p className="text-xs text-gray-400 py-3 text-center">无</p>
              ) : (
                costcoItems.map((item) => <ShopItem key={item.id} item={item} />)
              )}
            </div>
          </div>

          {/* T&T column */}
          <div>
            <div className="flex items-center gap-1.5 mb-2">
              <span className="text-sm font-semibold text-green-700">T&T</span>
              <span className="text-xs text-gray-400">({tntItems.length})</span>
            </div>
            <div className="bg-white rounded-xl px-3 py-1 border border-gray-100 divide-y divide-gray-50">
              {tntItems.length === 0 ? (
                <p className="text-xs text-gray-400 py-3 text-center">无</p>
              ) : (
                tntItems.map((item) => <ShopItem key={item.id} item={item} />)
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
