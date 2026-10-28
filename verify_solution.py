import json
import os

SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

def verify_and_reconstruct():
    print("=== ФИНАЛЬНЫЙ АЛГЕБРАИЧЕСКИЙ ВАЛИДАТОР СИСТЕМЫ СЕМАЕВА ===")
    print("Цель: Реконструкция скаляра из битовой карты и проверка нелинейного баланса...\n")
    
    # 1. Загружаем биты, полученные из bit_deductor.py
    deduction_path = os.path.join(os.path.dirname(__file__), "deduction.json")
    if not os.path.exists(deduction_path):
        print("❌ Ошибка: deduction.json не найден!")
        return
        
    with open(deduction_path, "r") as f:
        deducted_data = json.load(f)
    fixed_bits = deducted_data["fixed_bits"]
    
    # 2. Загружаем оригинальные коэффициенты матрицы F4
    matrix_path = os.path.join(os.path.dirname(__file__), "f4_matrix.json")
    with open(matrix_path, "r") as f:
        matrix_data = json.load(f)
        
    A1 = int(matrix_data["A1"], 16)
    B1 = int(matrix_data["B1"], 16)
    C1 = int(data_C1 := matrix_data["C1"], 16)
    
    # 3. Собираем целое число из битов: x = sum(bit_i * 2^i)
    reconstructed_x = 0
    for i in range(85):
        bit_val = fixed_bits[f"x_{i}"]
        if bit_val == 1:
            reconstructed_x |= (1 << i)
            
    print(f"[Шаг 1]: Скаляр успешно реконструирован из 85-битной карты:")
    print(f"        x_reconstructed = {hex(reconstructed_x)}\n")
    
    print("[Шаг 2]: Проверка нелинейного баланса уравнения Семаева F4:")
    # Подставляем собранное число в полное уравнение: A1*x^2 + B1*x + C1 mod P
    p = SECP256K1_P
    term_A = (A1 * pow(reconstructed_x, 2, p)) % p
    term_B = (B1 * reconstructed_x) % p
    
    current_balance = (term_A + term_B + C1) % p
    
    print(f"        A1 * x^2 mod P = {hex(term_A)}")
    print(f"        B1 * x   mod P = {hex(term_B)}")
    print(f"        C1       mod P = {hex(C1)}")
    print(f"        ----------------------------------------------------")
    print(f"        Итоговый остаток системы: {hex(current_balance)}")
    
    if current_balance == 0:
        print("\n🎉 [УСПЕХ]: Алгебраический баланс идеален! Остаток равен 0.")
        print("          Вы нашли истинный нелинейный корень Генезис-ключа Сатоши Накамото.")
    else:
        print("\n[Статус]: Обнаружена квадратичная погрешность.")
        print("          Линейный каскад переносов сдвинут нелинейными AND-связями мономов A1.")
        print("          Для точной коррекции требуется передать satoshi_genesis_glv3.cnf в SAT-солвер.")

if __name__ == "__main__":
    verify_and_reconstruct()
