/**
 * Marketing content that is genuinely static. Anything a business owner would
 * want to change without a deploy — prices, packages — belongs in the API,
 * not here.
 */

export interface InsightCategory {
  key: string
  title: string
  description: string
}

export const INSIGHT_CATEGORIES: InsightCategory[] = [
  {
    key: 'personality',
    title: 'Tính cách & nội tâm',
    description: 'Cách bạn phản ứng khi không có ai nhìn, và điều gì thật sự khiến bạn an tâm.',
  },
  {
    key: 'career',
    title: 'Công danh & sự nghiệp',
    description: 'Môi trường nào hợp với bạn, và vì sao có những giai đoạn bạn muốn đổi hướng.',
  },
  {
    key: 'finance',
    title: 'Tài chính',
    description: 'Cách tiền vào và ra trong lá số bạn: tích lũy đều hay lên xuống theo đợt.',
  },
  {
    key: 'love',
    title: 'Tình yêu & hôn nhân',
    description: 'Kiểu người bạn bị thu hút, và điểm dễ va chạm trong một mối quan hệ dài.',
  },
  {
    key: 'family',
    title: 'Gia đình',
    description: 'Quan hệ với cha mẹ, anh chị em và vai trò bạn thường mang trong nhà.',
  },
  {
    key: 'health',
    title: 'Sức khỏe',
    description: 'Những vùng cần giữ gìn theo cách nhìn của Tử Vi — mang tính tham khảo.',
  },
  {
    key: 'major-cycles',
    title: 'Đại vận',
    description: 'Nhịp mười năm: giai đoạn nào nên tích lũy, giai đoạn nào nên bung sức.',
  },
  {
    key: 'annual',
    title: 'Lưu niên',
    description: 'Bức tranh của riêng năm nay, đặt trong bối cảnh đại vận bạn đang đi.',
  },
]

export const DISCLAIMER_TEXT =
  'Nội dung Tử Vi trên Cosmic Signs mang tính tham khảo và định hướng tự nhìn nhận. ' +
  'Không nên sử dụng như lời khuyên thay thế cho chuyên gia y tế, pháp lý, tài chính ' +
  'hoặc các quyết định quan trọng.'
