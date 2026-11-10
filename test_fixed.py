import pytest
from fixed_code import ProcessFixed

def test_isolated_inbox():
    """Тест підтверджує, що процеси більше не крадуть повідомлення."""
    p1 = ProcessFixed(1)
    p2 = ProcessFixed(2)
    p3 = ProcessFixed(3)
    
    p1.send_to(p2, "Дані для P2")
    
    # P3 не бачить це повідомлення (його inbox ізольований і порожній)
    with pytest.raises(IndexError, match="Inbox порожній"):
        p3.recv_one()
        
    # P2 успішно читає своє повідомлення
    p2_time = p2.recv_one()
    
    # Годинник P2 оновився: max(0, 1) + 1 = 2
    assert p2_time == 2
    assert p2.clock.time == 2

def test_happens_before_property():
    """Тест перевіряє класичне правило happens-before для годинника Лемпорта."""
    pA = ProcessFixed(1)
    pB = ProcessFixed(2)
    
    pA.local_event() # Час pA: 1
    pA.local_event() # Час pA: 2
    
    # Відправка від pA (збільшує час pA до 3, мітка повідомлення = 3)
    pA.send_to(pB, "Подія")
    
    assert pA.clock.time == 3
    
    pB.local_event() # Час pB: 1
    
    # Отримання pB: max(локальний час 1, мітка повідомлення 3) + 1 = 4
    recv_time = pB.recv_one()
    
    assert recv_time == 4
    assert pB.clock.time == 4
    # Перевірка happens-before: подія в pA відбулася раніше, ніж pB обробив її
    assert pA.clock.time < pB.clock.time