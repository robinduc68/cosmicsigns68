"""Chủ Mệnh và Chủ Thân — hai nhãn ở khối giữa lá số.

Đây **không phải sao an vào cung**. Chúng là hai nhãn nói sao nào cai quản Mệnh và
sao nào cai quản Thân, tra thẳng từ chi năm sinh. Vì thế chúng đi vào
``TraditionalMetadata`` chứ không đi vào danh sách sao: thêm chúng vào ``stars`` sẽ
làm mọi phép đếm sao sai, và làm lá số hiện hai lần cùng một ngôi sao.

Cả hai bảng **đối xứng gương qua trục Tý–Ngọ**: Sửu soi với Hợi, Dần với Tuất, và cứ
thế. Tính đối xứng ấy là chốt kiểm, không phải nhận xét vui — một ô gõ sai sẽ phá
đối xứng, và test bắt được ngay mà không cần chờ ai đối chiếu ấn bản.
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from cosmic_astrology.calendar.sexagenary import CHI

__all__ = ["CHU_MENH_BY_YEAR_BRANCH", "CHU_THAN_BY_YEAR_BRANCH", "rulers_for_year_branch"]

#: Chủ Mệnh theo chi năm sinh. Khoá là **chỉ số** chi (Tý = 0).
CHU_MENH_BY_YEAR_BRANCH: Mapping[int, str] = MappingProxyType(
    {
        0: "Tham Lang",  # Tý
        1: "Cự Môn",  # Sửu
        2: "Lộc Tồn",  # Dần
        3: "Văn Khúc",  # Mão
        4: "Liêm Trinh",  # Thìn
        5: "Vũ Khúc",  # Tỵ
        6: "Phá Quân",  # Ngọ
        7: "Vũ Khúc",  # Mùi
        8: "Liêm Trinh",  # Thân
        9: "Văn Khúc",  # Dậu
        10: "Lộc Tồn",  # Tuất
        11: "Cự Môn",  # Hợi
    }
)

#: Chủ Thân theo chi năm sinh. Cùng kiểu đối xứng như Chủ Mệnh.
CHU_THAN_BY_YEAR_BRANCH: Mapping[int, str] = MappingProxyType(
    {
        0: "Linh Tinh",  # Tý
        1: "Thiên Tướng",  # Sửu
        2: "Thiên Lương",  # Dần
        3: "Thiên Đồng",  # Mão
        4: "Văn Xương",  # Thìn
        5: "Thiên Cơ",  # Tỵ
        6: "Hỏa Tinh",  # Ngọ
        7: "Thiên Tướng",  # Mùi
        8: "Thiên Lương",  # Thân
        9: "Thiên Đồng",  # Dậu
        10: "Văn Xương",  # Tuất
        11: "Thiên Cơ",  # Hợi
    }
)


def rulers_for_year_branch(year_branch: int) -> tuple[str, str]:
    """``(chủ Mệnh, chủ Thân)`` cho một chi năm sinh."""
    if not 0 <= year_branch < len(CHI):
        raise ValueError(f"chi năm phải trong 0..11, nhận {year_branch}")
    return CHU_MENH_BY_YEAR_BRANCH[year_branch], CHU_THAN_BY_YEAR_BRANCH[year_branch]
