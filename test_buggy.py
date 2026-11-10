import pytest
from buggy_code import Process

def test_shared_inbox_breaks_happens_before():
    """Тест показує, що Процес 3 може перехопити повідомлення для Процесу 2."""
    p1 = Process(1)
    p2 = Process(2)
    p3 = Process(3)
    
    # Очищаємо чергу перед тестом (оскільки вона спільна для всього класу)
    Process.inbox.clear()
    
    # Подія відбувається: P1 відправляє повідомлення строго для P2
    p1.send_to(p2, "Секретні дані для P2")
    
    # Помилка: P3 раптом читає повідомлення, призначене для P2
    # Це руйнує відношення happens-before, адже час оновлюється у P3, а не у P2
    p3_time = p3.recv_one()
    
    # P3 отримав час з повідомлення від P1
    assert p3.clock.time > 0
    assert p3_time == 2  # max(0, 1) + 1 = 2
    
    # P2 намагається прочитати своє повідомлення, але скринька порожня!
    with pytest.raises(IndexError, match="Inbox порожній"):
        p2.recv_one()