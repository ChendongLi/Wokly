import { useUpdateIngredient } from '../hooks/useMenu'

export default function ShopItem({ item }) {
  const update = useUpdateIngredient()

  const toggle = () => update.mutate({ id: item.id, checked: !item.checked })
  const swapStore = () =>
    update.mutate({ id: item.id, store: item.store === 'costco' ? 'tnt' : 'costco' })

  return (
    <div className={`flex items-center gap-2 py-2 ${item.checked ? 'opacity-40' : ''}`}>
      <button
        onClick={toggle}
        className={`w-5 h-5 rounded border-2 flex-shrink-0 flex items-center justify-center transition-colors ${
          item.checked ? 'bg-orange-500 border-orange-500' : 'border-gray-300'
        }`}
      >
        {item.checked && <span className="text-white text-xs leading-none">✓</span>}
      </button>

      <span className={`flex-1 text-sm text-gray-800 ${item.checked ? 'line-through' : ''}`}>
        {item.name}
        {item.quantity && <span className="text-gray-400 ml-1 text-xs">{item.quantity}</span>}
      </span>

      <button
        onClick={swapStore}
        className={`text-xs px-2 py-0.5 rounded-full font-medium transition-colors ${
          item.store === 'costco' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'
        }`}
      >
        {item.store === 'costco' ? 'Costco' : 'T&T'}
      </button>
    </div>
  )
}
