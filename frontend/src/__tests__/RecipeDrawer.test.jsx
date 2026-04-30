import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import RecipeDrawer from '../components/RecipeDrawer'

const mockDish = {
  name: '鱼香肉丝',
  tag: 'meat',
  style: '多料炒',
  diff: 2,
  ingredients: '猪里脊、木耳、胡萝卜',
  steps: ['切丝备用', '热锅下油', '翻炒均匀'],
  search_query: '鱼香肉丝做法',
}

describe('RecipeDrawer', () => {
  it('renders dish name', () => {
    render(<RecipeDrawer dish={mockDish} onClose={() => {}} />)
    expect(screen.getByText('鱼香肉丝')).toBeTruthy()
  })

  it('renders ingredients', () => {
    render(<RecipeDrawer dish={mockDish} onClose={() => {}} />)
    expect(screen.getByText('猪里脊、木耳、胡萝卜')).toBeTruthy()
  })

  it('renders all steps', () => {
    render(<RecipeDrawer dish={mockDish} onClose={() => {}} />)
    expect(screen.getByText('切丝备用')).toBeTruthy()
    expect(screen.getByText('热锅下油')).toBeTruthy()
    expect(screen.getByText('翻炒均匀')).toBeTruthy()
  })

  it('renders numbered step indicators', () => {
    render(<RecipeDrawer dish={mockDish} onClose={() => {}} />)
    expect(screen.getByText('1')).toBeTruthy()
    expect(screen.getByText('2')).toBeTruthy()
    expect(screen.getByText('3')).toBeTruthy()
  })

  it('renders 小红书 link with correct href', () => {
    render(<RecipeDrawer dish={mockDish} onClose={() => {}} />)
    const link = screen.getByText('📕 小红书').closest('a')
    expect(link.href).toContain('xiaohongshu.com')
    expect(link.href).toContain(encodeURIComponent('鱼香肉丝做法'))
  })

  it('renders YouTube link with correct href', () => {
    render(<RecipeDrawer dish={mockDish} onClose={() => {}} />)
    const link = screen.getByText('▶️ YouTube').closest('a')
    expect(link.href).toContain('youtube.com')
  })

  it('calls onClose when × button clicked', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    render(<RecipeDrawer dish={mockDish} onClose={onClose} />)
    await user.click(screen.getByText('×'))
    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('calls onClose when backdrop clicked', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    const { container } = render(<RecipeDrawer dish={mockDish} onClose={onClose} />)
    const backdrop = container.querySelector('.fixed.inset-0')
    await user.click(backdrop)
    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('calls onClose on Escape key', () => {
    const onClose = vi.fn()
    render(<RecipeDrawer dish={mockDish} onClose={onClose} />)
    fireEvent.keyDown(document, { key: 'Escape' })
    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('renders nothing when dish is null', () => {
    const { container } = render(<RecipeDrawer dish={null} onClose={() => {}} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders style and tag badge', () => {
    render(<RecipeDrawer dish={mockDish} onClose={() => {}} />)
    expect(screen.getByText('多料炒')).toBeTruthy()
    expect(screen.getByText('荤')).toBeTruthy()
  })
})
