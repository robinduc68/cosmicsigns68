<script setup lang="ts">
import { ChevronDown } from 'lucide-vue-next'

const QUESTIONS = [
  {
    q: 'Lập lá số có mất phí không?',
    a: 'Không. Bạn lập lá số và xem đầy đủ 12 cung hoàn toàn miễn phí, không cần tài khoản. Chỉ phần luận giải chuyên sâu mới cần trả phí.',
  },
  {
    q: 'Mình không nhớ chính xác giờ sinh thì sao?',
    a: 'Tử Vi an Mệnh theo canh giờ, tức khoảng hai tiếng một canh, nên sai lệch vài phút không ảnh hưởng. Nhưng nếu bạn không chắc mình sinh vào canh nào thì lá số sẽ lệch — lúc đó nên hỏi lại người nhà hoặc xem giấy khai sinh.',
  },
  {
    q: 'Mình chỉ biết ngày âm lịch, có nhập được không?',
    a: 'Được. Bạn chọn âm lịch khi nhập, kể cả ngày rơi vào tháng nhuận. Việc đổi lịch do engine làm theo thuật toán thiên văn chứ không tra bảng.',
  },
  {
    q: 'AI có tự nghĩ ra sao và cung không?',
    a: 'Không, và đây là điều chúng mình giữ chặt nhất. Lá số do engine tính, AI chỉ nhận kết quả đã tính cùng các dấu hiệu kèm dẫn chứng rồi viết thành lời. Sao nào không có trong lá số thì AI không được nhắc tới.',
  },
  {
    q: 'Tử Vi có đúng không?',
    a: 'Cosmic Signs không hứa hẹn điều đó. Phần tính toán thì tất định và kiểm chứng được. Phần luận giải là một góc nhìn để bạn tự soi lại mình, không phải lời tiên tri, và không thay thế lời khuyên của chuyên gia y tế, pháp lý hay tài chính.',
  },
  {
    q: 'Dữ liệu ngày sinh của mình được dùng làm gì?',
    a: 'Chỉ để tính và lưu lá số cho bạn xem lại. Lá số có địa chỉ ngẫu nhiên không đoán được, và bạn xoá được bất cứ lúc nào — xoá là xoá thật.',
  },
]
</script>

<template>
  <section id="cau-hoi-thuong-gap" class="scroll-mt-20 py-20 sm:py-24">
    <CsContainer size="sm">
      <CsSectionHeading align="center" eyebrow="Câu hỏi thường gặp" title="Những điều hay được hỏi" />
      <div class="mt-10 divide-y divide-[var(--border)] border-y border-[var(--border)]">
        <details v-for="item in QUESTIONS" :key="item.q" class="group py-4">
          <summary
            class="flex cursor-pointer list-none items-center justify-between gap-4 rounded text-small font-medium text-[var(--text)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)]"
          >
            {{ item.q }}
            <ChevronDown
              class="size-4 shrink-0 text-[var(--text-subtle)] transition-transform duration-200 group-open:rotate-180"
              aria-hidden="true"
            />
          </summary>
          <p class="mt-3 text-small text-[var(--text-muted)]">{{ item.a }}</p>
        </details>
      </div>
    </CsContainer>
  </section>
</template>
