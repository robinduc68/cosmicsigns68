import { describe, expect, it } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import Button from '../../../packages/ui/components/Button.vue'
import Badge from '../../../packages/ui/components/Badge.vue'

describe('CsButton', () => {
  it('renders its label', async () => {
    const wrapper = await mountSuspended(Button, { slots: { default: () => 'Lập lá số' } })
    expect(wrapper.text()).toContain('Lập lá số')
  })

  it('is disabled and marked busy while loading', async () => {
    const wrapper = await mountSuspended(Button, { props: { loading: true } })
    const button = wrapper.get('button')
    expect(button.attributes('disabled')).toBeDefined()
    expect(button.attributes('aria-busy')).toBe('true')
  })

  it('exposes an accessible name when only an icon is shown', async () => {
    const wrapper = await mountSuspended(Button, { props: { ariaLabel: 'Đóng' } })
    expect(wrapper.get('button').attributes('aria-label')).toBe('Đóng')
  })
})

describe('CsBadge', () => {
  it('applies the variant styling', async () => {
    const wrapper = await mountSuspended(Badge, {
      props: { variant: 'accent' },
      slots: { default: () => 'Miếu' },
    })
    expect(wrapper.text()).toBe('Miếu')
    expect(wrapper.get('span').classes().join(' ')).toContain('accent')
  })
})
