import { describe, expect, it } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import { EARTHLY_BRANCHES, PALACE_ORDER, type ChartPalace, type ChartPayload } from '@cosmic/shared'
import Grid from '../components/chart/Grid.vue'

/**
 * The địa bàn layout is fixed: a palace's cell is decided by its địa chi, never
 * by its position in the array. Getting this wrong misplaces every palace while
 * still looking plausible, so it is worth pinning down.
 */
function palace(branchIndex: number, index: number): ChartPalace {
  return {
    name: PALACE_ORDER[index]!,
    label: `Cung ${index}`,
    branch: EARTHLY_BRANCHES[branchIndex]!,
    branch_index: branchIndex,
    stem: 'Giáp',
    stem_index: 0,
    element: 'KIM',
    nap_am: 'Kiếm Phong Kim',
    is_menh: index === 0,
    is_than: false,
    has_tuan: false,
    has_triet: false,
    is_empty_main_star: true,
    major_stars: [],
    minor_stars: [],
    transformations: [],
  }
}

const chart = {
  // Deliberately shuffled: the component must not rely on array order.
  palaces: [11, 3, 7, 0, 5, 9, 2, 6, 10, 1, 4, 8].map((branch, i) => palace(branch, i)),
} as unknown as ChartPayload

describe('ChartGrid', () => {
  it('places each palace in the cell its địa chi owns', async () => {
    const wrapper = await mountSuspended(Grid, { props: { chart } })
    const rendered = wrapper.findAll('[data-branch]').map((el) => el.attributes('data-branch'))

    expect(rendered).toEqual(['Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Thìn', 'Dậu', 'Mão', 'Tuất', 'Dần', 'Sửu', 'Tý', 'Hợi'])
  })

  it('renders all twelve palaces', async () => {
    const wrapper = await mountSuspended(Grid, { props: { chart } })
    expect(wrapper.findAll('[data-branch]')).toHaveLength(12)
  })
})
