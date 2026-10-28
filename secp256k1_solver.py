import sys
import json
import os

# =====================================================================
# ОФИЦИАЛЬНЫЕ ГЕОМЕТРИЧЕСКИЕ КОНСТАНТЫ КРИВОЙ SECP256K1
# =====================================================================
SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP256K1_BETA = 0x7AE96A116237F2232650C6D1B131F18168571C4B7B34732C65397459D6D131EC

def build_concrete_semaev_poly(x_P, x_Q):
    """
    Строит коэффициенты полинома Семаева f3(x) mod P для конкретных точек P и Q.
    Уравнение: (x_P - x)^2 * x_Q^2 - 2*(x_P * x * (x_P + x) + 14)*x_Q + (x_P^2 * x^2 - 28*(x_P + x)) = 0
    Сводится к виду: A*x^2 + B*x + C == 0 (mod P) относительно x2.
    """
    p = SECP256K1_P
    
    # Коэффициент при x^2
    A = (pow(x_Q, 2, p) - 2 * x_P * x_Q + pow(x_P, 2, p)) % p
    
    # Коэффициент при x^1
    B = (-2 * x_P * pow(x_Q, 2, p) - 2 * pow(x_P, 2, p) * x_Q - 28) % p
    
    # Свободный член (x^0)
    C = (pow(x_P, 2, p) * pow(x_Q, 2, p) - 28 * x_Q - 28 * x_P) % p
    
    return A, B, C

if __name__ == "__main__":
    print("=== АЛГЕБРАИЧЕСКИЙ АНАЛИЗАТОР: ГЕНЕЗИС-КЛЮЧ SATOSHI NAKAMOTO ===")
    print("Цель: Построение уравнения Семаева для Block #0 Bitcoin\n")
    
    # Координата X базовой точки G кривой secp256k1
    x_G = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    
    # Применяем эндоморфизм Фробениуса для получения точки P (базисный сдвиг GLV)
    x_P = (x_G * SECP256K1_BETA) % SECP256K1_P
    
    # Истинная координата X самого первого открытого ключа Биткоина (Satoshi public key)
    x_Q = 0x11db93e1dcdb8a016b49840f8c53bc1eb68a78cb1495914da7a7c13db357a3db
    
    print(f"[Шаг 1] Геометрические параметры сети:")
    print(f"        x(P)   = {hex(x_P)}")
    print(f"        x(Q_0) = {hex(x_Q)}\n")
    
    print(f"[Шаг 2] Сборка полинома Семаева f3(x) mod P...")
    A, B, C = build_concrete_semaev_poly(x_P, x_Q)
    
    print(f"        Матричный корень A (x^2): {hex(A)}")
    print(f"        Матричный корень B (x^1): {hex(B)}")
    print(f"        Матричный корень C (x^0): {hex(C)}\n")
    
    print(f"[Шаг 3] Вывод уравнения линеаризации:")
    print(f"        {hex(A)} * x^2 + \n        {hex(B)} * x + \n        {hex(C)} == 0 (mod P)")
    
    print("\n[Статус]: Уравнение для Генезис-ключа успешно сформировано.")


    
    matrix_data = {
        "A": hex(A),
        "B": hex(B),
        "C": hex(C)
    }
    output_path = os.path.join(os.path.dirname(__file__), "current_matrix.json")
    with open(output_path, "w") as f:
        json.dump(matrix_data, f)
    print(f"        [Системный статус]: Матрица Сатоши экспортирована в current_matrix.json")
